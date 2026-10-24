from fastapi import FastAPI, Depends, BackgroundTasks, HTTPException, status, WebSocket, WebSocketDisconnect, Request
from fastapi import Query, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import case
from sqlalchemy.dialects.postgresql import insert as pg_insert
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List
import os
import json
import smtplib
import random
import secrets
import hmac
import hashlib
import asyncio
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from groq import Groq
from dotenv import load_dotenv

from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone

from . import models, schemas
from .jarvis_tools import (
    consultar_anomalias_usuario,
    HERRAMIENTAS_JARVIS
)
from .database import engine, get_db, SessionLocal
from .schema_migrations import migrate_legacy_auth_schema
from .color_utils import get_color
from .metricas_service import registrar_metrica, simular_metrica_usuario
from .pipeline_keys import autenticar_clave
from .auth_router import (
    crear_router_auth,
    VerificarRequest,
    SolicitarCodigoRequest,
    RecuperarRequest,
)
from .anomalias_router import crear_router_anomalias
from .pipelines_router import crear_router_pipelines
from .chat_router import crear_router_chat, ChatRequest
from .metricas_router import crear_router_metricas
from .websocket_router import ConnectionManager, crear_router_websocket

# Fuerza a Python a leer la llave nueva
load_dotenv(override=True, encoding='utf-8')
# Actualizar columnas de bases antiguas antes de atender solicitudes.
# La migracion es transaccional y no borra registros existentes.
with engine.begin() as conexion_migracion:
    migrate_legacy_auth_schema(conexion_migracion)
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Obligamos a Groq a usar la llave del archivo .env
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")

SECRET_KEY = (os.getenv("SECRET_KEY") or "").strip()

if len(SECRET_KEY) < 32:
    raise RuntimeError(
        "Debes configurar SECRET_KEY con al menos 32 caracteres."
    )
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Seguridad de códigos de verificación y recuperación
CODIGO_DURACION_MINUTOS = 10
CODIGO_MAX_INTENTOS = 5
def generar_codigo_seguro():
    return str(100000 + secrets.randbelow(900000))


from .auth_utils import pwd_context, verify_password, get_password_hash
from .jwt_utils import encode_access_token
from .auth_dependencies import resolve_current_user
from .email_utils import (
    _enviar_correo_verificacion_impl,
    _enviar_alerta_correo_consolidado_impl,
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Limites compartidos por las instancias mediante AuthRateLimit.
# Formato: ruta -> (solicitudes permitidas, ventana en segundos).
LIMITES_AUTENTICACION = {
    "/registro/": (20, 3600),
    "/login/": (15, 300),
    "/verificar/": (30, 600),
    "/reenviar-verificacion/": (8, 3600),
    "/solicitar-recuperacion/": (10, 3600),
    "/recuperar-password/": (30, 600),
}

LIMITES_POR_IP = {
    **LIMITES_AUTENTICACION,
    "/metricas/": (60, 60),
    "/metricas/externas/": (60, 60),
    "/pipelines/": (60, 60),
}


def consumir_limite_solicitudes(
    db: Session,
    identificador: str,
    maximo: int,
    ventana_segundos: int,
    detalle: str = "Demasiadas solicitudes. Intenta mas tarde.",
) -> None:
    """Contador atomico compartido entre middleware y endpoints."""
    clave = hmac.new(
        SECRET_KEY.encode("utf-8"),
        identificador.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    ahora = datetime.now(timezone.utc).replace(tzinfo=None)
    limite_anterior = ahora - timedelta(seconds=ventana_segundos)

    tabla = models.AuthRateLimit
    vencida = tabla.inicio_ventana <= limite_anterior

    insercion = pg_insert(tabla).values(
        clave=clave,
        inicio_ventana=ahora,
        cantidad=1,
    )

    instruccion = insercion.on_conflict_do_update(
        index_elements=[tabla.clave],
        set_={
            "inicio_ventana": case(
                (vencida, ahora),
                else_=tabla.inicio_ventana,
            ),
            "cantidad": case(
                (vencida, 1),
                else_=tabla.cantidad + 1,
            ),
        },
    ).returning(
        tabla.cantidad,
        tabla.inicio_ventana,
    )

    cantidad, inicio_ventana = db.execute(instruccion).one()
    db.commit()

    if cantidad > maximo:
        espera = max(
            1,
            int(
                (
                    inicio_ventana
                    + timedelta(seconds=ventana_segundos)
                    - ahora
                ).total_seconds()
            ) + 1,
        )

        raise HTTPException(
            status_code=429,
            detail=detalle,
            headers={"Retry-After": str(espera)},
        )


@app.middleware("http")
async def limitar_solicitudes_autenticacion(request: Request, call_next):
    if request.method != "POST":
        return await call_next(request)

    ruta = request.url.path

    # Crear, rotar y revocar comparten el limite de pipelines.
    if ruta.startswith("/pipelines/"):
        ruta = "/pipelines/"

    configuracion = LIMITES_POR_IP.get(ruta)

    if configuracion is None:
        return await call_next(request)

    maximo, ventana_segundos = configuracion

    origen = (
        request.client.host
        if request.client
        else "origen-desconocido"
    )

    try:
        with SessionLocal() as db:
            consumir_limite_solicitudes(
                db,
                f"{ruta}|{origen}",
                maximo,
                ventana_segundos,
            )

    except HTTPException as error:
        return JSONResponse(
            status_code=error.status_code,
            content={"detail": error.detail},
            headers=error.headers,
        )

    return await call_next(request)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =================================================================
#                GESTOR DE WEBSOCKETS
# =================================================================

manager = ConnectionManager()

app.include_router(
    crear_router_websocket(
        manager,
        lambda: SessionLocal(),
        SECRET_KEY,
        ALGORITHM,
    )
)


# =================================================================
#                FUNCIONES DE UTILIDAD Y SEGURIDAD
# =================================================================


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    return encode_access_token(
        data,
        expires_delta=expires_delta,
        secret_key=SECRET_KEY,
        algorithm=ALGORITHM,
    )

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    return resolve_current_user(
        token,
        db,
        secret_key=SECRET_KEY,
        algorithm=ALGORITHM,
    )


# =================================================================
#                SISTEMA DE CORREOS E IA
# =================================================================
def enviar_correo_verificacion(destinatario: str, codigo: str):
    return _enviar_correo_verificacion_impl(destinatario, codigo, smtp_server=SMTP_SERVER, smtp_port=SMTP_PORT, sender_email=SENDER_EMAIL, sender_password=SENDER_PASSWORD)

def enviar_alerta_correo_consolidado(destinatario: str, lat_v: str, lat_s: str, cal_v: str, cal_s: str, fal_v: str, fal_s: str, diag_general: str):
    return _enviar_alerta_correo_consolidado_impl(destinatario, lat_v, lat_s, cal_v, cal_s, fal_v, fal_s, diag_general, smtp_server=SMTP_SERVER, smtp_port=SMTP_PORT, sender_email=SENDER_EMAIL, sender_password=SENDER_PASSWORD)


def generar_recomendacion_ia(pipeline_name: str, metric_type: str, value: float) -> str:
    """
    Genera recomendaciones técnicas locales para la telemetría simulada.
    No realiza solicitudes a Groq ni consume tokens de IA.
    """

    if metric_type == "latencia_ms":
        return (
            f"Se detectó una latencia de {value:.2f} ms en {pipeline_name}. "
            "Revisar tiempos de respuesta, consultas lentas, "
            "saturación de recursos y posibles cuellos de botella."
        )

    elif metric_type == "datos_corruptos_%":
        return (
            f"Se detectó un {value:.2f}% de datos corruptos en {pipeline_name}. "
            "Verificar validaciones, integridad de registros, "
            "transformaciones y calidad de los datos de origen."
        )

    elif metric_type == "tasa_fallos_%":
        return (
            f"Se detectó una tasa de fallos del {value:.2f}% en {pipeline_name}. "
            "Revisar registros de errores, conectividad, "
            "dependencias del servicio y mecanismos de reintento."
        )

    return (
        f"Se detectó una anomalía en {pipeline_name}. "
        "Revisar los registros del sistema y el comportamiento de la métrica."
    )


# =================================================================
#                SIMULADOR DE INGESTA AUTOMATICA (NIVEL INGENIERÍA)
# =================================================================
async def generar_telemetria_automatica():
    """Simula metricas con un ciclo de 30 segundos."""

    while True:
        await asyncio.sleep(30)

        db = SessionLocal()

        try:
            usuarios_activos = (
                db.query(models.User)
                .filter(models.User.is_active.is_(True))
                .all()
            )

            for user in usuarios_activos:
                try:
                    await simular_metrica_usuario(
                        db=db,
                        user_id=user.id,
                        enviar_ws=manager.send_to_user,
                        generar_recomendacion=generar_recomendacion_ia,
                    )

                except Exception as error:
                    db.rollback()
                    print(
                        "Error de simulacion para usuario "
                        + str(user.id) + ": " + str(error)
                    )

        except Exception as error:
            db.rollback()
            print("Error general del simulador: " + str(error))

        finally:
            db.close()

# Inicia el motor automático al prender FastAPI
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(generar_telemetria_automatica())

# =================================================================
#                ENDPOINTS DE AUTENTICACIÓN
# =================================================================
app.include_router(
    crear_router_auth(
        secret_key=SECRET_KEY,
        codigo_duracion_minutos=CODIGO_DURACION_MINUTOS,
        codigo_max_intentos=CODIGO_MAX_INTENTOS,
        token_expire_minutes=ACCESS_TOKEN_EXPIRE_MINUTES,
        generar_codigo=lambda: generar_codigo_seguro(),
        enviar_correo=lambda destinatario, codigo: enviar_correo_verificacion(
            destinatario, codigo
        ),
        emitir_token=lambda data, expires_delta: create_access_token(
            data=data, expires_delta=expires_delta
        ),
    )
)

# =================================================================
#                ENDPOINTS DE LECTURA E HISTORIAL
# =================================================================


app.include_router(
    crear_router_metricas(
        get_current_user,
        consumir_limite_solicitudes,
        registrar_metrica,
        manager,
    )
)


app.include_router(crear_router_anomalias(get_current_user))
app.include_router(crear_router_pipelines(get_current_user))





def limitar_chat_por_usuario(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Conserva el limite de seis mensajes por minuto y usuario."""
    consumir_limite_solicitudes(
        db,
        f"/chat/|usuario:{current_user.id}",
        6,
        60,
        detalle="Limite del chat alcanzado. Intenta mas tarde.",
    )

app.include_router(
    crear_router_chat(
        get_current_user,
        limitar_chat_por_usuario,
        client,
    )
)
