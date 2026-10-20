"""Rutas de consulta y archivado de anomalias."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from . import models, schemas
from .database import get_db


def crear_router_anomalias(get_current_user):
    router = APIRouter()

    @router.get("/anomalias/", response_model=list[schemas.AnomalyLogResponse])
    def read_anomalies(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=500),
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
    ):
        return (
            db.query(models.AnomalyLog)
            .filter(
                models.AnomalyLog.user_id == current_user.id,
                models.AnomalyLog.archived.is_(False)
            )
            .order_by(models.AnomalyLog.id.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )


    @router.delete("/anomalias/")
    def clear_anomalies(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
        from datetime import datetime, timezone

        total = (
            db.query(models.AnomalyLog)
            .filter(
                models.AnomalyLog.user_id == current_user.id,
                models.AnomalyLog.archived.is_(False)
            )
            .update(
                {
                    models.AnomalyLog.archived: True,
                    models.AnomalyLog.archived_at:
                        datetime.now(timezone.utc),
                },
                synchronize_session=False
            )
        )

        db.commit()

        return {
            "status": "Historial archivado exitosamente",
            "archivadas": total,
        }


    @router.get(
        "/anomalias/archivadas/",
        response_model=list[schemas.AnomalyLogResponse]
    )
    def read_archived_anomalies(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=500),
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
    ):
        return (
            db.query(models.AnomalyLog)
            .filter(
                models.AnomalyLog.user_id == current_user.id,
                models.AnomalyLog.archived.is_(True)
            )
            .order_by(models.AnomalyLog.id.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )


    @router.post("/anomalias/restaurar/")
    def restore_archived_anomalies(
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
    ):
        total = (
            db.query(models.AnomalyLog)
            .filter(
                models.AnomalyLog.user_id == current_user.id,
                models.AnomalyLog.archived.is_(True)
            )
            .update(
                {
                    models.AnomalyLog.archived: False,
                    models.AnomalyLog.archived_at: None,
                },
                synchronize_session=False
            )
        )

        db.commit()

        return {
            "status": "Historial restaurado exitosamente",
            "restauradas": total,
        }


    return router
