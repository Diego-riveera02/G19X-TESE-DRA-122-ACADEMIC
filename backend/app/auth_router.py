"""Endpoints de registro, verificacion, acceso y recuperacion de cuentas.

Los servicios y callbacks se inyectan desde main para conservar el contrato
HTTP y permitir las sustituciones utilizadas por las pruebas aisladas.
"""

from datetime import datetime, timedelta, timezone
from typing import Callable

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from . import models, schemas
from .auth_utils import get_password_hash, verify_password
from .database import get_db
from .verification_codes import crear_hash_codigo, verificar_codigo_guardado


class VerificarRequest(BaseModel):
    correo: str
    codigo: str

class SolicitarCodigoRequest(BaseModel):
    correo: str

class RecuperarRequest(BaseModel):
    correo: str
    codigo: str
    nueva_password: str = Field(min_length=8)


def crear_router_auth(
    *,
    secret_key: str,
    codigo_duracion_minutos: int,
    codigo_max_intentos: int,
    token_expire_minutes: int,
    generar_codigo: Callable[[], str],
    enviar_correo: Callable[[str, str], None],
    emitir_token: Callable[..., str],
    enviar_correo_recuperacion: Callable[[str, str], None] | None = None,
):
    """Crea las rutas sin duplicar configuracion ni utilidades de seguridad."""
    router = APIRouter()

    @router.post("/registro/", response_model=dict[str, str])
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
        codigo_secreto = generar_codigo()
        nuevo_usuario = models.User(
            nombre_completo=user.nombre_completo,
            correo=user.correo,
            telefono=user.telefono,
            hashed_password=get_password_hash(user.password),
            codigo_verificacion=crear_hash_codigo(
                codigo_secreto, user.correo, "verificacion", secret_key
            ),
            codigo_expira_en=datetime.utcnow() + timedelta(
                minutes=codigo_duracion_minutos
            ),
            codigo_intentos=0,
            codigo_proposito="verificacion",
            is_active=False
        )

        db.add(nuevo_usuario)
        db.commit()
        db.refresh(nuevo_usuario)

        background_tasks.add_task(enviar_correo, user.correo, codigo_secreto)
        return respuesta

    @router.post("/verificar/")
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
        if user.codigo_intentos >= codigo_max_intentos:
            # Mantener el vencimiento original para impedir reenvios
            # inmediatos despues de agotar los cinco intentos.
            user.codigo_verificacion = None
            db.commit()

            raise HTTPException(
                status_code=400,
                detail="Codigo de verificacion invalido o vencido"
            )

        # Comparar el codigo de forma segura
        if not verificar_codigo_guardado(
            user.codigo_verificacion,
            req.codigo,
            user.correo,
            "verificacion",
            secret_key,
        ):
            user.codigo_intentos += 1

            if user.codigo_intentos >= codigo_max_intentos:
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


    @router.post("/reenviar-verificacion/")
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

        codigo_secreto = generar_codigo()
        user.codigo_verificacion = crear_hash_codigo(
            codigo_secreto, user.correo, "verificacion", secret_key
        )
        user.codigo_expira_en = ahora + timedelta(minutes=codigo_duracion_minutos)
        user.codigo_intentos = 0
        user.codigo_proposito = "verificacion"
        db.commit()

        background_tasks.add_task(
            enviar_correo,
            user.correo,
            codigo_secreto,
        )
        return respuesta


    @router.post("/solicitar-recuperacion/")
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

        codigo_secreto = generar_codigo()

        user.codigo_verificacion = crear_hash_codigo(
            codigo_secreto, user.correo, "recuperacion", secret_key
        )
        user.codigo_expira_en = ahora + timedelta(
            minutes=codigo_duracion_minutos
        )
        user.codigo_intentos = 0
        user.codigo_proposito = "recuperacion"

        db.commit()

        background_tasks.add_task(
            enviar_correo_recuperacion or enviar_correo,
            user.correo,
            codigo_secreto
        )

        return respuesta


    @router.post("/recuperar-password/")
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
            user.codigo_intentos >= codigo_max_intentos
            or not user.codigo_verificacion
        ):
            raise HTTPException(
                status_code=400,
                detail="Codigo de recuperacion invalido o vencido"
            )

        if not verificar_codigo_guardado(
            user.codigo_verificacion,
            req.codigo,
            user.correo,
            "recuperacion",
            secret_key,
        ):
            user.codigo_intentos += 1
            if user.codigo_intentos >= codigo_max_intentos:
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

    @router.post("/login/")
    def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
        user = db.query(models.User).filter(models.User.correo == form_data.username).first()
        if not user or not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Credenciales incorrectas")

        if not user.is_active:
            raise HTTPException(status_code=403, detail="Tu cuenta aún no está verificada. Revisa tu correo o verifica tu cuenta.")

        token = emitir_token(data={"sub": user.correo}, expires_delta=timedelta(minutes=token_expire_minutes))
        return {"access_token": token, "token_type": "bearer", "nombre": user.nombre_completo, "correo": user.correo}

    return router
