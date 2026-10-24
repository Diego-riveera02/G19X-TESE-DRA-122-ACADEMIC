"""Rutas del chat de observabilidad con inteligencia artificial."""

import json
from typing import List

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from . import models
from .database import get_db
from .jarvis_tools import (
    HERRAMIENTAS_JARVIS,
    consultar_anomalias_usuario,
)


class ChatRequest(BaseModel):
    anomaly_id: int
    pregunta: str
    contexto_anomalia: str
    historial: List[dict] = Field(default_factory=list)

def crear_router_chat(
    get_current_user,
    limitar_chat_por_usuario,
    client,
):
    router = APIRouter()

    @router.post("/chat/")
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

    return router
