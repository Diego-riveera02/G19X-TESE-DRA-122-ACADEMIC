from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import models, schemas
from .database import get_db
from .pipeline_keys import emitir_clave, calcular_hash


def crear_router_pipelines(get_current_user):
    router = APIRouter()

    @router.post("/pipelines/", status_code=201)
    def crear_pipeline(
        entrada: schemas.PipelineNuevo,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user),
    ):
        pipeline = models.Pipeline(
            user_id=current_user.id,
            nombre=entrada.nombre,
            clave_hash="0" * 64,
            revocado=False
        )

        try:
            db.add(pipeline)
            db.flush()

            clave = emitir_clave(pipeline.id)
            pipeline.clave_hash = calcular_hash(clave)

            db.commit()
            db.refresh(pipeline)

        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=409,
                detail="Ya existe un pipeline con ese nombre"
            )

        except Exception:
            db.rollback()
            raise

        return {
            "id": pipeline.id,
            "nombre": pipeline.nombre,
            "clave_api": clave,
            "mensaje": "Guarda la clave ahora; no se mostrara otra vez"
        }


    @router.get("/pipelines/")
    def listar_pipelines(
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user),
    ):
        pipelines = db.query(models.Pipeline).filter(
            models.Pipeline.user_id == current_user.id
        ).order_by(models.Pipeline.id.desc()).all()

        return [
            {
                "id": p.id,
                "nombre": p.nombre,
                "revocado": p.revocado
            }
            for p in pipelines
        ]


    @router.post("/pipelines/{pipeline_id}/rotar/")
    def rotar_clave_pipeline(
        pipeline_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user),
    ):
        pipeline = db.query(models.Pipeline).filter(
            models.Pipeline.id == pipeline_id,
            models.Pipeline.user_id == current_user.id,
            models.Pipeline.revocado.is_(False)
        ).first()

        if pipeline is None:
            raise HTTPException(
                status_code=404,
                detail="Pipeline no encontrado"
            )

        clave = emitir_clave(pipeline.id)
        pipeline.clave_hash = calcular_hash(clave)

        try:
            db.commit()
        except Exception:
            db.rollback()
            raise

        return {
            "id": pipeline.id,
            "clave_api": clave,
            "mensaje": "La clave anterior ya no es valida"
        }


    @router.post("/pipelines/{pipeline_id}/revocar/")
    def revocar_pipeline(
        pipeline_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user),
    ):
        pipeline = db.query(models.Pipeline).filter(
            models.Pipeline.id == pipeline_id,
            models.Pipeline.user_id == current_user.id,
            models.Pipeline.revocado.is_(False)
        ).first()

        if pipeline is None:
            raise HTTPException(
                status_code=404,
                detail="Pipeline no encontrado"
            )

        pipeline.revocado = True

        try:
            db.commit()
        except Exception:
            db.rollback()
            raise

        return {
            "id": pipeline.id,
            "revocado": True
        }

    return router
