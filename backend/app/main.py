from fastapi import FastAPI, Depends, BackgroundTasks, HTTPException, status, WebSocket, WebSocketDisconnect, Request
from fastapi import Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import case
from sqlalchemy.dialects.postgresql import insert as pg_insert
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
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
from pydantic import BaseModel, Field
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
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Limites de solicitudes por IP de origen y ruta, compartidos por
# las instancias mediante una tabla PostgreSQL.
# El formato es ruta: (maximo de solicitudes, segundos de ventana).
LIMITES_AUTENTICACION = {
    "/registro/": (20, 3600),
    "/login/": (15, 300),
    "/verificar/": (30, 600),
    "/reenviar-verificacion/": (8, 3600),
    "/solicitar-recuperacion/": (10, 3600),
    "/recuperar-password/": (30, 600),
}


@app.middleware("http")
async def limitar_solicitudes_autenticacion(request: Request, call_next):
    # No tocar el resto de rutas ni las conexiones WebSocket.
    configuracion = LIMITES_AUTENTICACION.get(request.url.path)
    if request.method != "POST" or configuracion is None:
        return await call_next(request)

    maximo, ventana_segundos = configuracion
    origen = request.client.host if request.client else "origen-desconocido"
    # No guardar direcciones IP en texto claro dentro de la tabla.
    clave = hmac.new(
        SECRET_KEY.encode("utf-8"),
        f"{request.url.path}|{origen}".encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    ahora = datetime.now(timezone.utc).replace(tzinfo=None)
    limite_anterior = ahora - timedelta(seconds=ventana_segundos)
    tabla = models.AuthRateLimit
    vencida = tabla.inicio_ventana <= limite_anterior

    # ON CONFLICT aplica el contador atomica y persistentemente,
    # aun si llegan varias peticiones simultaneamente.
    insercion = pg_insert(tabla).values(
        clave=clave, inicio_ventana=ahora, cantidad=1
    )
    instruccion = insercion.on_conflict_do_update(
        index_elements=[tabla.clave],
        set_={
            "inicio_ventana": case(
                (vencida, ahora), else_=tabla.inicio_ventana
            ),
            "cantidad": case(
                (vencida, 1), else_=tabla.cantidad + 1
            ),
        },
    ).returning(tabla.cantidad, tabla.inicio_ventana)

    with SessionLocal() as db:
        cantidad, inicio_ventana = db.execute(instruccion).one()
        db.commit()

    if cantidad > maximo:
        espera = max(
            1,
            int((inicio_ventana + timedelta(seconds=ventana_segundos) - ahora)
                .total_seconds()) + 1,
        )
        return JSONResponse(
            status_code=429,
            content={"detail": "Demasiadas solicitudes. Intenta mas tarde."},
            headers={"Retry-After": str(espera)},
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
#                MODELOS EXTRAS PARA REQUESTS
# =================================================================

class ChatRequest(BaseModel):
    anomaly_id: int
    pregunta: str
    contexto_anomalia: str
    historial: List[dict] = Field(default_factory=list)


class VerificarRequest(BaseModel):
    correo: str
    codigo: str

class SolicitarCodigoRequest(BaseModel):
    correo: str

class RecuperarRequest(BaseModel):
    correo: str
    codigo: str
    nueva_password: str = Field(min_length=8)

# =================================================================
#                GESTOR DE WEBSOCKETS
# =================================================================

class ConnectionManager:
    def __init__(self):
        # Cada usuario tiene sus propias conexiones.
        self.active_connections = {}

    def connect(self, user_id: int, websocket: WebSocket):
        self.active_connections.setdefault(user_id, set()).add(websocket)

    def disconnect(self, user_id: int, websocket: WebSocket):
        conexiones = self.active_connections.get(user_id)
        if conexiones is not None:
            conexiones.discard(websocket)
            if not conexiones:
                del self.active_connections[user_id]

    async def send_to_user(self, user_id: int, message: str):
        conexiones = list(self.active_connections.get(user_id, set()))
        for conexion in conexiones:
            try:
                await conexion.send_text(message)
            except Exception:
                self.disconnect(user_id, conexion)


manager = ConnectionManager()


@app.websocket("/ws/anomalias")
async def websocket_endpoint(websocket: WebSocket):
    origen = websocket.headers.get("origin")
    permitidos = {
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    }

    if origen is not None and origen not in permitidos:
        await websocket.close(code=1008)
        return

    await websocket.accept()
    user_id = None

    try:
        # El token se recibe en el primer mensaje,
        # nunca como parámetro en la URL.
        datos = await asyncio.wait_for(
            websocket.receive_json(),
            timeout=10
        )

        if (
            not isinstance(datos, dict)
            or datos.get("type") != "auth"
            or not isinstance(datos.get("token"), str)
            or len(datos["token"]) > 4096
        ):
            await websocket.close(code=1008)
            return

        try:
            payload = jwt.decode(
                datos["token"],
                SECRET_KEY,
                algorithms=[ALGORITHM]
            )
        except JWTError:
            await websocket.close(code=1008)
            return

        correo = payload.get("sub")
        expiracion = payload.get("exp")

        if (
            not isinstance(correo, str)
            or not isinstance(expiracion, (int, float))
        ):
            await websocket.close(code=1008)
            return

        # Verificar que la cuenta exista y esté activa.
        with SessionLocal() as db:
            usuario = db.query(models.User).filter(
                models.User.correo == correo,
                models.User.is_active.is_(True)
            ).first()

            if usuario:
                user_id = usuario.id

        if user_id is None:
            await websocket.close(code=1008)
            return

        manager.connect(user_id, websocket)
        await websocket.send_json({"type": "auth_ok"})

        while True:
            tiempo_restante = expiracion - time.time()

            if tiempo_restante <= 0:
                await websocket.close(code=1008)
                break

            try:
                await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=tiempo_restante
                )
            except asyncio.TimeoutError:
                await websocket.close(code=1008)
                break

    except WebSocketDisconnect:
        pass
    except (asyncio.TimeoutError, ValueError):
        await websocket.close(code=1008)
    finally:
        if user_id is not None:
            manager.disconnect(user_id, websocket)

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
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        correo: str = payload.get("sub")
        if correo is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.correo == correo).first()
    if user is None or not user.is_active:
        raise credentials_exception
    return user


# =================================================================
#                SISTEMA DE CORREOS E IA
# =================================================================
def enviar_correo_verificacion(destinatario: str, codigo: str):
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = destinatario
        msg['Subject'] = "🔒 Código de Verificación - PluriOne"

        body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #0b0c10; color: #c5c6c7; padding: 20px;">
                <div style="border: 2px solid #E5B80B; border-radius: 8px; padding: 30px; background-color: #1a1a1d; text-align: center;">
                    <h2 style="color: #E5B80B; margin-top: 0;">VERIFICACIÓN DE CUENTA PLURIONE</h2>
                    <p style="font-size: 16px;">Para completar tu solicitud, ingresa el siguiente código de 6 dígitos en la plataforma:</p>
                    <div style="background-color: #0b0c10; padding: 15px; margin: 20px 0; border-radius: 8px; display: inline-block;">
                        <h1 style="color: #E63946; margin: 0; letter-spacing: 5px;">{codigo}</h1>
                    </div>
                    <p style="font-size: 12px; color: #888;">Si tú no solicitaste este acceso, puedes ignorar este mensaje.</p>
                </div>
            </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print(f"Error al enviar código de verificación: {e}")

def enviar_alerta_correo_consolidado(destinatario: str, lat_v: str, lat_s: str, cal_v: str, cal_s: str, fal_v: str, fal_s: str, diag_general: str):
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = destinatario
        msg['Subject'] = "🚨 REPORTE CONSOLIDADO DE INFRAESTRUCTURA - PluriOne"

        body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #0b0c10; color: #c5c6c7; padding: 20px;">
                <div style="border: 2px solid #8B0000; border-radius: 8px; padding: 20px; background-color: #1a1a1d;">
                    <h2 style="color: #E63946; margin-top: 0;">SISTEMA CENTRAL PLURIONE - REPORTE DE ESTADO</h2>
                    <p>Se ha registrado un evento crítico. A continuación se presenta el estado consolidado de los tres componentes del sistema:</p>

                    <table style="width: 100%; border-collapse: collapse; margin-top: 15px; background-color: #111217;">
                        <tr style="background-color: #333; color: #fff;">
                            <th style="padding: 10px; text-align: left;">Componente / Métrica</th>
                            <th style="padding: 10px; text-align: left;">Valor</th>
                            <th style="padding: 10px; text-align: left;">Estado</th>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #333;">Latencia de Red (API Gateway)</td>
                            <td style="padding: 10px; border-bottom: 1px solid #333;">{lat_v}</td>
                            <td style="padding: 10px; border-bottom: 1px solid #333; font-weight: bold; color: {get_color(lat_s)};">{lat_s}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #333;">Calidad de Datos (Ventas MX)</td>
                            <td style="padding: 10px; border-bottom: 1px solid #333;">{cal_v}</td>
                            <td style="padding: 10px; border-bottom: 1px solid #333; font-weight: bold; color: {get_color(cal_s)};">{cal_s}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #333;">Tasa de Fallos (Migración AWS)</td>
                            <td style="padding: 10px; border-bottom: 1px solid #333;">{fal_v}</td>
                            <td style="padding: 10px; border-bottom: 1px solid #333; font-weight: bold; color: {get_color(fal_s)};">{fal_s}</td>
                        </tr>
                    </table>

                    <h4 style="color: #E5B80B; margin-top: 25px; margin-bottom: 5px;">DIAGNÓSTICO DE CAUSA RAÍZ (J.A.R.V.I.S.)</h4>
                    <div style="background-color: rgba(212, 160, 23, 0.1); border-left: 3px solid #E5B80B; padding: 12px; color: #e0e0e0; line-height: 1.5;">
                        {diag_general}
                    </div>
                </div>
            </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print(f"Error al enviar correo: {e}")


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
    """Genera una metrica simulada por usuario activo y ciclo."""

    pipelines = [
        "API Gateway Core",
        "Pipeline Ventas MX",
        "Migración AWS S3",
        "Sync PostgreSQL",
    ]

    metricas = [
        ("latencia_ms", 50.0, 900.0, "ms"),
        ("datos_corruptos_%", 0.0, 15.0, "%"),
        ("tasa_fallos_%", 0.0, 25.0, "%"),
    ]

    while True:
        await asyncio.sleep(5)

        db = SessionLocal()

        try:
            usuarios_activos = (
                db.query(models.User)
                .filter(models.User.is_active.is_(True))
                .all()
            )

            for user in usuarios_activos:
                try:
                    pipe = random.choice(pipelines)
                    m_tipo, min_v, max_v, unidad = (
                        random.choice(metricas)
                    )
                    valor_generado = round(
                        random.uniform(min_v, max_v), 2
                    )

                    estado = "Normal"

                    if valor_generado > max_v * 0.75:
                        estado = "Critico"
                    elif valor_generado > max_v * 0.45:
                        estado = "Alerta"

                    recomendacion = "Operación normal."

                    if estado != "Normal":
                        # Ejecutar la llamada sin bloquear
                        # el ciclo de eventos de FastAPI.
                        recomendacion = await asyncio.to_thread(
                            generar_recomendacion_ia,
                            pipe,
                            m_tipo,
                            valor_generado,
                        )

                    db_anomalia = models.AnomalyLog(
                        pipeline_name=pipe,
                        metric_type=m_tipo,
                        value=valor_generado,
                        status=estado,
                        ai_recommendation=recomendacion,
                        user_id=user.id,
                    )

                    db.add(db_anomalia)
                    db.commit()
                    db.refresh(db_anomalia)

                    mensaje_ws = json.dumps({
                        "id": db_anomalia.id,
                        "pipeline_name": db_anomalia.pipeline_name,
                        "metric_type": db_anomalia.metric_type,
                        "value": db_anomalia.value,
                        "status": db_anomalia.status,
                        "ai_recommendation":
                            db_anomalia.ai_recommendation,
                        "timestamp": (
                            db_anomalia.timestamp.isoformat() + "Z"
                            if db_anomalia.timestamp else None
                        ),
                    })

                    await manager.send_to_user(
                        user.id, mensaje_ws
                    )

                except Exception as error:
                    db.rollback()
                    print(
                        f"Error de simulacion para usuario "
                        f"{user.id}: {error}"
                    )

        except Exception as error:
            db.rollback()
            print(f"Error general del simulador: {error}")

        finally:
            db.close()

# Inicia el motor automático al prender FastAPI
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(generar_telemetria_automatica())

# =================================================================
#                ENDPOINTS DE AUTENTICACIÓN
# =================================================================
@app.post("/registro/", response_model=dict[str, str])
def registrar_usuario(user: schemas.UserCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    respuesta = {
        "status": (
            "Si el correo puede registrarse, recibiras "
            "un codigo de verificacion. Si ya tienes "
            "cuenta, inicia sesion o recupera tu acceso."
        )
    }
    if db.query(models.User).filter(models.User.correo == user.correo).first():
        return respuesta
    codigo_secreto = generar_codigo_seguro()
    nuevo_usuario = models.User(
        nombre_completo=user.nombre_completo,
        correo=user.correo,
        telefono=user.telefono,
        hashed_password=get_password_hash(user.password),
        codigo_verificacion=codigo_secreto,
        codigo_expira_en=datetime.utcnow() + timedelta(
            minutes=CODIGO_DURACION_MINUTOS
        ),
        codigo_intentos=0,
        codigo_proposito="verificacion",
        is_active=False
    )

    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    background_tasks.add_task(enviar_correo_verificacion, user.correo, codigo_secreto)
    return respuesta

@app.post("/verificar/")
def verificar_codigo(req: VerificarRequest, db: Session = Depends(get_db)):
    user = (
        db.query(models.User)
        .filter(models.User.correo == req.correo)
        .with_for_update()
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=400,
            detail="Codigo de verificacion invalido o vencido"
        )

    if user.is_active:
        raise HTTPException(
            status_code=400,
            detail="Codigo de verificacion invalido o vencido"
        )

    # Verificar que exista un codigo valido para activar la cuenta
    if (
        not user.codigo_verificacion
        or user.codigo_proposito != "verificacion"
        or user.codigo_expira_en is None
    ):
        raise HTTPException(
            status_code=400,
            detail="Codigo de verificacion invalido o vencido"
        )

    # Rechazar codigos vencidos
    if datetime.utcnow() >= user.codigo_expira_en:
        user.codigo_verificacion = None
        user.codigo_expira_en = None
        user.codigo_proposito = None
        user.codigo_intentos = 0
        db.commit()

        raise HTTPException(
            status_code=400,
            detail="Codigo de verificacion invalido o vencido"
        )

    # Impedir nuevos intentos si ya se alcanzo el limite
    if user.codigo_intentos >= CODIGO_MAX_INTENTOS:
        # Mantener el vencimiento original para impedir reenvios
        # inmediatos despues de agotar los cinco intentos.
        user.codigo_verificacion = None
        db.commit()

        raise HTTPException(
            status_code=400,
            detail="Codigo de verificacion invalido o vencido"
        )

    # Comparar el codigo de forma segura
    if not secrets.compare_digest(
        user.codigo_verificacion,
        str(req.codigo)
    ):
        user.codigo_intentos += 1

        if user.codigo_intentos >= CODIGO_MAX_INTENTOS:
            # Bloquear el codigo, pero conservar el vencimiento
            # para aplicar la espera por cuenta antes de reenviar.
            user.codigo_verificacion = None

            db.commit()

            raise HTTPException(
                status_code=400,
                detail="Codigo de verificacion invalido o vencido"
            )

        db.commit()

        raise HTTPException(
            status_code=400,
            detail="Codigo de verificacion invalido o vencido"
        )

    # Activar la cuenta y eliminar el codigo utilizado
    user.is_active = True
    user.codigo_verificacion = None
    user.codigo_expira_en = None
    user.codigo_intentos = 0
    user.codigo_proposito = None

    db.commit()

    return {"status": "Cuenta verificada con exito"}


@app.post("/reenviar-verificacion/")
def reenviar_verificacion(
    req: SolicitarCodigoRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Reenvia un codigo solo a cuentas sin activar y con codigo vencido.

    Se devuelve la misma respuesta si el correo no existe, esta activo
    o aun se encuentra en espera, para no revelar cuentas existentes.
    """
    respuesta = {
        "status": (
            "Si tu cuenta requiere verificacion y el codigo anterior "
            "ya vencio, recibiras uno nuevo. Los codigos duran 10 minutos."
        )
    }

    user = (
        db.query(models.User)
        .filter(models.User.correo == req.correo)
        .with_for_update()
        .first()
    )
    if user is None or user.is_active:
        return respuesta

    ahora = datetime.now(timezone.utc).replace(tzinfo=None)

    # Evitar inundar el buzon y preservar el bloqueo de cinco intentos.
    if (
        user.codigo_proposito == "verificacion"
        and user.codigo_expira_en is not None
        and ahora < user.codigo_expira_en
    ):
        return respuesta

    codigo_secreto = generar_codigo_seguro()
    user.codigo_verificacion = codigo_secreto
    user.codigo_expira_en = ahora + timedelta(minutes=CODIGO_DURACION_MINUTOS)
    user.codigo_intentos = 0
    user.codigo_proposito = "verificacion"
    db.commit()

    background_tasks.add_task(
        enviar_correo_verificacion,
        user.correo,
        codigo_secreto,
    )
    return respuesta


@app.post("/solicitar-recuperacion/")
def solicitar_recuperacion(
    req: SolicitarCodigoRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    respuesta = {
        "status": (
            "Si existe una cuenta verificada que puede "
            "recuperar su acceso, recibiras un codigo "
            "en el correo indicado."
        )
    }

    user = (
        db.query(models.User)
        .filter(models.User.correo == req.correo)
        .with_for_update()
        .first()
    )

    if not user:
        return respuesta

    if not user.is_active:
        return respuesta

    ahora = datetime.utcnow()

    # Mantener el periodo de espera de 10 minutos.
    # No permitir otro codigo aunque se hayan agotado
    # los cinco intentos del codigo anterior.
    if (
        user.codigo_proposito == "recuperacion"
        and user.codigo_expira_en is not None
        and ahora < user.codigo_expira_en
    ):
        return respuesta

    codigo_secreto = generar_codigo_seguro()

    user.codigo_verificacion = codigo_secreto
    user.codigo_expira_en = ahora + timedelta(
        minutes=CODIGO_DURACION_MINUTOS
    )
    user.codigo_intentos = 0
    user.codigo_proposito = "recuperacion"

    db.commit()

    background_tasks.add_task(
        enviar_correo_verificacion,
        user.correo,
        codigo_secreto
    )

    return respuesta


@app.post("/recuperar-password/")
def recuperar_password(
    req: RecuperarRequest,
    db: Session = Depends(get_db)
):
    user = (
        db.query(models.User)
        .filter(models.User.correo == req.correo)
        .with_for_update()
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=400,
            detail="Codigo de recuperacion invalido o vencido"
        )

    # Solo los codigos de recuperacion pueden cambiar contrasenas.
    if (
        user.codigo_proposito != "recuperacion"
        or user.codigo_expira_en is None
    ):
        raise HTTPException(
            status_code=400,
            detail="Codigo de recuperacion invalido o vencido"
        )

    # Vencimiento de 10 minutos (fecha UTC almacenada en PostgreSQL).
    if datetime.utcnow() >= user.codigo_expira_en:
        user.codigo_verificacion = None
        user.codigo_expira_en = None
        user.codigo_intentos = 0
        user.codigo_proposito = None
        db.commit()
        raise HTTPException(
            status_code=400,
            detail="Codigo de recuperacion invalido o vencido"
        )

    # Preservar el periodo de espera si se agotaron los intentos.
    if (
        user.codigo_intentos >= CODIGO_MAX_INTENTOS
        or not user.codigo_verificacion
    ):
        raise HTTPException(
            status_code=400,
            detail="Codigo de recuperacion invalido o vencido"
        )

    if not secrets.compare_digest(
        user.codigo_verificacion,
        str(req.codigo)
    ):
        user.codigo_intentos += 1
        if user.codigo_intentos >= CODIGO_MAX_INTENTOS:
            # Invalidar el codigo, pero conservar su vencimiento.
            user.codigo_verificacion = None
            db.commit()
            raise HTTPException(
                status_code=400,
                detail="Codigo de recuperacion invalido o vencido"
            )

        db.commit()
        raise HTTPException(
            status_code=400,
            detail="Codigo de recuperacion invalido o vencido"
        )

    # Aceptar el codigo una sola vez y borrar su estado.
    user.hashed_password = get_password_hash(req.nueva_password)
    user.codigo_verificacion = None
    user.codigo_expira_en = None
    user.codigo_intentos = 0
    user.codigo_proposito = None
    db.commit()
    return {"status": "Contrasena actualizada exitosamente"}

@app.post("/login/")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.correo == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Tu cuenta aún no está verificada. Revisa tu correo o verifica tu cuenta.")

    token = create_access_token(data={"sub": user.correo}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": token, "token_type": "bearer", "nombre": user.nombre_completo, "correo": user.correo}

# =================================================================
#                ENDPOINTS DE LECTURA E HISTORIAL
# =================================================================
@app.get("/anomalias/", response_model=list[schemas.AnomalyLogResponse])
def read_anomalies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return (
        db.query(models.AnomalyLog)
        .filter(models.AnomalyLog.user_id == current_user.id)
        .order_by(models.AnomalyLog.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

@app.delete("/anomalias/")
def clear_anomalies(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db.query(models.AnomalyLog).filter(models.AnomalyLog.user_id == current_user.id).delete()
    db.commit()
    return {"status": "Historial borrado exitosamente"}

def limitar_chat_por_usuario(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Limita el chat por usuario autenticado usando PostgreSQL."""
    maximo = 6
    ventana_segundos = 60

    identificador = (
        f"/chat/|usuario:{current_user.id}"
    ).encode("utf-8")

    clave = hmac.new(
        SECRET_KEY.encode("utf-8"),
        identificador,
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

    cantidad, inicio_ventana = db.execute(
        instruccion
    ).one()

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
            detail="Limite del chat alcanzado. Intenta mas tarde.",
            headers={"Retry-After": str(espera)},
        )


@app.post("/chat/")
def chat_causa_raiz(
    chat_req: ChatRequest,
      current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
    _limite_chat: None = Depends(limitar_chat_por_usuario)
):
    contexto = (
        chat_req.contexto_anomalia
        if chat_req.contexto_anomalia
        else "Sin diagnóstico previo."
    )

    # Preparar un historial de conversación seguro y limitado.
    historial_seguro = []

    for mensaje in chat_req.historial[-10:]:
        if not isinstance(mensaje, dict):
            continue

        rol = mensaje.get("role")
        contenido = mensaje.get("content")

        if rol not in ("user", "assistant"):
            continue

        if not isinstance(contenido, str):
            continue

        contenido = contenido.strip()

        if contenido:
            historial_seguro.append({
                "role": rol,
                "content": contenido[:1200]
            })

    # Preparar la conversación para Groq.
    mensajes = [
        {
            "role": "system",
            "content": (
                "Eres J.A.R.V.I.S., el asistente inteligente de PluriOne. "
                "Responde en español de manera clara, útil y concisa. "
                "Recuerda el contexto de los mensajes anteriores. "
                "Puedes explicar conceptos de tecnología, programación "
                "y observabilidad de datos. "
                "Si te preguntan por anomalías reales del usuario, "
                "no inventes fechas, cantidades ni valores. "
                "Utiliza únicamente los datos que el backend "
                "te proporcione mediante herramientas autorizadas. "
                "La telemetría actual de PluriOne es simulada. "
                "Distingue siempre las posibles causas de los "
                "problemas que realmente se hayan comprobado."
                                "Nunca presentes hipótesis como causas verificadas. "
                "Cuando no existan pruebas suficientes, indica que "
                "las posibles causas requieren comprobación. "
                "No recomiendes borrar datos, restaurar respaldos, "
                "detener servicios ni ejecutar acciones destructivas "
                "basándote solamente en telemetría simulada. "
                "Propón primero verificaciones y medidas preventivas. "
                "Actualmente solo puedes consultar anomalías por "
                "estado: normal, alerta, critico o todos, y obtener "
                "hasta diez registros recientes por consulta. "
                "No ofrezcas filtros por fechas, severidad, métricas "
                "ni otras funciones que no estén implementadas. "
                "Si el usuario pide un diagnóstico, proporciona "
                "los datos disponibles, posibles causas y "
                "recomendaciones relacionadas con la métrica. "
                "No inventes evidencias ni afirmes haber revisado "
                "logs, servidores o infraestructura externa."
            )
        },
        *historial_seguro,
        {
            "role": "user",
            "content": chat_req.pregunta.strip()[:2000]
        }
    ]

    try:
        respuesta = client.chat.completions.create(
            messages=mensajes,
            model="openai/gpt-oss-20b",
            temperature=0.3,
            max_tokens=2048,
             tools=HERRAMIENTAS_JARVIS,
            tool_choice="auto"
        )

        contenido = respuesta.choices[0].message.content

        # Revisar si Groq solicitó herramientas de PostgreSQL.
        mensaje_ia = respuesta.choices[0].message
        llamadas = mensaje_ia.tool_calls or []

        if llamadas:
            # Registrar las solicitudes realizadas por la IA.
            mensajes.append({
                "role": "assistant",
                "content": mensaje_ia.content,
                "tool_calls": [
                    {
                        "id": llamada.id,
                        "type": "function",
                        "function": {
                            "name": llamada.function.name,
                            "arguments": llamada.function.arguments
                        }
                    }
                    for llamada in llamadas
                ]
            })

            # Ejecutar solamente herramientas autorizadas.
            for llamada in llamadas:
                nombre_funcion = llamada.function.name

                if nombre_funcion != "consultar_anomalias_usuario":
                    resultado = {
                        "error": "Herramienta no autorizada."
                    }
                else:
                    try:
                        argumentos = json.loads(
                            llamada.function.arguments or "{}"
                        )

                        if not isinstance(argumentos, dict):
                            raise ValueError("Argumentos no válidos.")

                        resultado = consultar_anomalias_usuario(
                            db=db,
                            user_id=current_user.id,
                            estado=argumentos.get("estado", "todos"),
                            limite=argumentos.get("limite", 5)
                        )

                    except (ValueError, TypeError, AttributeError):
                        resultado = {
                            "error": "No se pudieron interpretar los argumentos."
                        }

                # Entregar a Groq los datos obtenidos.
                mensajes.append({
                    "role": "tool",
                    "tool_call_id": llamada.id,
                    "name": nombre_funcion,
                    "content": json.dumps(
                        resultado,
                        ensure_ascii=False
                    )
                })

            # Solicitar la respuesta final usando los datos consultados.
            respuesta = client.chat.completions.create(
                messages=mensajes,
                model="openai/gpt-oss-20b",
                temperature=0.3,
                max_tokens=2048
            )
        contenido = respuesta.choices[0].message.content
        if contenido and contenido.strip():
            return {"respuesta": contenido.strip()}
        return {
            "respuesta": (
                "No recibí una respuesta del modelo de IA. "
                "Por favor, intenta reformular tu pregunta."
            )
        }

    except Exception as e:
        codigo = getattr(e, "status_code", None)

        print(
            f"Error IA en chat: "
            f"tipo={type(e).__name__}, codigo={codigo}"
        )

        if codigo == 429:
            return {
                "respuesta": (
                    "J.A.R.V.I.S. alcanzó temporalmente el límite "
                    "de uso de Groq. Intenta nuevamente más tarde."
                )
            }

        if codigo in (401, 403):
            return {
                "respuesta": (
                    "J.A.R.V.I.S. no pudo autenticarse con Groq. "
                    "Es necesario revisar la configuración del servicio."
                )
            }

        if codigo == 404:
            return {
                "respuesta": (
                    "El modelo de inteligencia artificial configurado "
                    "no está disponible."
                )
            }

        return {
            "respuesta": (
                "No fue posible obtener una respuesta del servicio "
                "de inteligencia artificial. Intenta nuevamente más tarde."
            )
        }
