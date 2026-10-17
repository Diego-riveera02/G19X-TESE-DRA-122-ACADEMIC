
from sqlalchemy.orm import Session
from . import models


def consultar_anomalias_usuario(
    db: Session,
    user_id: int,
    estado: str = "todos",
    limite: int = 5
) -> dict:
    """
    Consulta de solo lectura para J.A.R.V.I.S.

    Recupera anomalías exclusivamente del usuario autenticado.
    No permite ejecutar SQL arbitrario.
    """

    estados_permitidos = {
        "normal": "Normal",
        "alerta": "Alerta",
        "critico": "Critico",
        "crítico": "Critico",
        "todos": "todos"
    }

    estado_normalizado = estado.strip().lower()

    if estado_normalizado not in estados_permitidos:
        return {
            "error": "Estado no válido. Usa Normal, Alerta, Critico o todos."
        }

    limite = max(1, min(int(limite), 10))

    consulta = db.query(models.AnomalyLog).filter(
        models.AnomalyLog.user_id == user_id
    )

    estado_filtrado = estados_permitidos[estado_normalizado]

    if estado_filtrado == "Critico":
        consulta = consulta.filter(
            models.AnomalyLog.status.in_(["Critico", "Crítico"])
        )

    elif estado_filtrado != "todos":
        consulta = consulta.filter(
            models.AnomalyLog.status == estado_filtrado
        )

    total = consulta.count()

    registros = (
        consulta
        .order_by(
            models.AnomalyLog.timestamp.desc(),
            models.AnomalyLog.id.desc()
        )
        .limit(limite)
        .all()
    )

    resultados = []

    for registro in registros:
        resultados.append({
            "id": registro.id,
            "pipeline": registro.pipeline_name,
            "metrica": registro.metric_type,
            "valor": registro.value,
            "estado": registro.status,
            "fecha_utc": (
                registro.timestamp.isoformat() + "Z"
                if registro.timestamp else None
            ),
            "recomendacion": registro.ai_recommendation
        })

    return {
        "estado_consultado": estado_filtrado,
        "total_registros": total,
        "ultimos_registros": resultados,
        "nota": "La telemetría de PluriOne es simulada."
    }

# Descripción de herramientas disponibles para J.A.R.V.I.S.
HERRAMIENTAS_JARVIS = [
    {
        "type": "function",
        "function": {
            "name": "consultar_anomalias_usuario",
            "description": (
                "Consulta las anomalías reales registradas en PluriOne "
                "para el usuario autenticado. Permite contar registros, "
                "consultar anomalías por estado, revisar las más recientes "
                "y obtener información para diagnósticos técnicos. "
                "Los datos provienen de telemetría simulada."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "estado": {
                        "type": "string",
                        "enum": [
                            "normal",
                            "alerta",
                            "critico",
                            "todos"
                        ],
                        "description": (
                            "Estado de las anomalías que se desea consultar."
                        )
                    },
                    "limite": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 10,
                        "description": (
                            "Cantidad máxima de registros recientes "
                            "que se desean recuperar."
                        )
                    }
                }
            }
        }
    }
]
