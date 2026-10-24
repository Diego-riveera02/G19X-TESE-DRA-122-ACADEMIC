"""Rutas de ingesta de metricas de PluriOne."""

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from . import models, schemas
from .database import get_db
from .pipeline_keys import autenticar_clave


def crear_router_metricas(
    get_current_user,
    consumir_limite_solicitudes,
    registrar_metrica,
    manager,
):
    router = APIRouter()

    @router.post("/metricas/externas/", status_code=201)
    async def ingestar_metrica_externa(
        metrica: schemas.MetricaExternaEntrada,
        x_pipeline_key: str | None = Header(
            default=None,
            alias="X-Pipeline-Key"
        ),
        db: Session = Depends(get_db),
    ):
        pipeline = autenticar_clave(
            db,
            x_pipeline_key
        )

        if pipeline is None:
            raise HTTPException(
                status_code=401,
                detail="Clave de pipeline invalida"
            )

        usuario = db.query(models.User).filter(
            models.User.id == pipeline.user_id,
            models.User.is_active.is_(True)
        ).first()

        if usuario is None:
            raise HTTPException(
                status_code=401,
                detail="Clave de pipeline invalida"
            )

        consumir_limite_solicitudes(
            db,
            f"/metricas/externas/|pipeline:{pipeline.id}",
            60,
            60,
        )

        return await registrar_metrica(
            db=db,
            user_id=usuario.id,
            pipeline=pipeline.nombre,
            metrica=metrica.metrica,
            valor=metrica.valor,
            enviar_ws=manager.send_to_user,
        )


    @router.post("/metricas/", status_code=201)
    async def ingestar_metrica(
        metrica: schemas.MetricaEntrada,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user),
    ):
        """Registra telemetria de la cuenta autenticada."""
        consumir_limite_solicitudes(
            db,
            f"/metricas/|usuario:{current_user.id}",
            60,
            60,
        )

        return await registrar_metrica(
            db=db,
            user_id=current_user.id,
            pipeline=metrica.pipeline,
            metrica=metrica.metrica,
            valor=metrica.valor,
            enviar_ws=manager.send_to_user,
        )

    return router
