
"""Validacion y registro compartido de metricas."""

import json
import math

from sqlalchemy.orm import Session

from . import models


LIMITES = {
    "latencia_ms": (900.0, 10000.0),
    "datos_corruptos_%": (15.0, 100.0),
    "tasa_fallos_%": (25.0, 100.0),
}


def clasificar_metrica(tipo: str, valor: float) -> str:
    if tipo not in LIMITES:
        raise ValueError("Tipo de metrica no permitido")

    referencia, maximo = LIMITES[tipo]

    if not math.isfinite(valor) or not 0 <= valor <= maximo:
        raise ValueError("Valor fuera de rango")

    if valor > referencia * 0.75:
        return "Critico"

    if valor > referencia * 0.45:
        return "Alerta"

    return "Normal"


async def registrar_metrica(
    db: Session,
    user_id: int,
    pipeline: str,
    metrica: str,
    valor: float,
    enviar_ws,
    recomendacion: str | None = None,
    guardar_normales: bool = True,
) -> dict:
    """Almacena la metrica y notifica al usuario propietario."""

    estado = clasificar_metrica(metrica, valor)

    if (
        not pipeline
        or len(pipeline) > 100
        or not pipeline.strip()
    ):
        raise ValueError("Pipeline invalido")

    if not guardar_normales and estado == "Normal":
        return {
            "id": None,
            "pipeline_name": pipeline,
            "metric_type": metrica,
            "value": valor,
            "status": estado,
            "ai_recommendation": "Operacion normal.",
            "timestamp": None,
            "registrada": False,
        }

    if recomendacion is None:
        recomendacion = (
            "Operacion normal."
            if estado == "Normal"
            else "Revisar la metrica y su fuente de datos."
        )

    registro = models.AnomalyLog(
        user_id=user_id,
        pipeline_name=pipeline,
        metric_type=metrica,
        value=valor,
        status=estado,
        ai_recommendation=recomendacion,
        archived=False,
    )

    try:
        db.add(registro)
        db.commit()
        db.refresh(registro)
    except Exception:
        db.rollback()
        raise

    resultado = {
        "id": registro.id,
        "pipeline_name": registro.pipeline_name,
        "metric_type": registro.metric_type,
        "value": registro.value,
        "status": registro.status,
        "ai_recommendation": registro.ai_recommendation,
        "timestamp": (
            registro.timestamp.isoformat() + "Z"
            if registro.timestamp else None
        ),
        "registrada": True,
    }

    await enviar_ws(
        user_id,
        json.dumps(resultado, ensure_ascii=False),
    )

    return resultado
