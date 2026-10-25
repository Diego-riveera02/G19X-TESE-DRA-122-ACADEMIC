"""Gestor y rutas WebSocket de anomal?as de PluriOne."""

import asyncio
import time

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from jose import JWTError, jwt

from . import models
from .origin_utils import get_cors_origins


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

def crear_router_websocket(
    manager,
    SessionLocal,
    SECRET_KEY,
    ALGORITHM,
):
    router = APIRouter()

    @router.websocket("/ws/anomalias")
    async def websocket_endpoint(websocket: WebSocket):
        origen = websocket.headers.get("origin")
        permitidos = set(get_cors_origins())

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

    return router
