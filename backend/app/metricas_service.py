
"""Validacion y registro compartido de metricas."""

import asyncio
import json
import math
import random
from datetime import datetime, timezone

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
        resultado = {
            "type": "metrica_normal",
            "id": None,
            "pipeline_name": pipeline,
            "metric_type": metrica,
            "value": valor,
            "status": estado,
            "ai_recommendation": "Operacion normal.",
            "timestamp": (
                datetime.now(timezone.utc)
                .isoformat()
                .replace("+00:00", "Z")
            ),
            "registrada": False,
        }

        await enviar_ws(
            user_id,
            json.dumps(resultado, ensure_ascii=False),
        )

        return resultado

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


async def simular_metrica_usuario(
    db: Session,
    user_id: int,
    enviar_ws,
    generar_recomendacion,
) -> dict:
    """Simula una metrica sin almacenar registros normales."""

    pipelines = [
        "API Gateway Core",
        "Pipeline Ventas MX",
        "Migracion AWS S3",
        "Sync PostgreSQL",
    ]

    metricas = [
        ("latencia_ms", 50.0, 900.0, "ms"),
        ("datos_corruptos_%", 0.0, 15.0, "%"),
        ("tasa_fallos_%", 0.0, 25.0, "%"),
    ]

    pipeline = random.choice(pipelines)
    tipo, minimo, maximo, unidad = random.choice(
        metricas
    )

    valor = round(
        random.uniform(minimo, maximo),
        2
    )

    estado = clasificar_metrica(tipo, valor)

    recomendacion = None

    if estado != "Normal":
        recomendacion = await asyncio.to_thread(
            generar_recomendacion,
            pipeline,
            tipo,
            valor,
        )

    return await registrar_metrica(
        db=db,
        user_id=user_id,
        pipeline=pipeline,
        metrica=tipo,
        valor=valor,
        enviar_ws=enviar_ws,
        recomendacion=recomendacion,
        guardar_normales=False,
    )
