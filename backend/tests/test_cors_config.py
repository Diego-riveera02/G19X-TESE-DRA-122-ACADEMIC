"""Pruebas aisladas de configuracion CORS."""

import asyncio

import pytest

from app.origin_utils import (
    DEFAULT_CORS_ORIGINS,
    get_cors_origins,
)


@pytest.mark.parametrize(
    ("configuracion", "esperados"),
    [
        (None, list(DEFAULT_CORS_ORIGINS)),
        ("", list(DEFAULT_CORS_ORIGINS)),
        (
            "http://localhost:5175,http://127.0.0.1:5175",
            [
                "http://localhost:5175",
                "http://127.0.0.1:5175",
            ],
        ),
        (
            "http://localhost:5173,http://localhost:5173",
            ["http://localhost:5173"],
        ),
    ],
)
def test_origenes_configurables(
    monkeypatch,
    configuracion,
    esperados,
):
    if configuracion is None:
        monkeypatch.delenv("CORS_ORIGINS", raising=False)
    else:
        monkeypatch.setenv("CORS_ORIGINS", configuracion)

    assert get_cors_origins() == esperados


@pytest.mark.parametrize(
    "configuracion",
    [
        "*",
        "http://localhost:5173,*",
        "ftp://localhost:5173",
        "http://localhost:5173/ruta",
        "http://usuario:clave@localhost:5173",
        "http://localhost:5173,",
        "http://localhost:99999",
    ],
)
def test_rechaza_configuraciones_invalidas(
    monkeypatch,
    configuracion,
):
    monkeypatch.setenv("CORS_ORIGINS", configuracion)

    with pytest.raises(ValueError):
        get_cors_origins()


@pytest.mark.parametrize(
    ("configuracion", "origen", "permitido"),
    [
        (None, "http://localhost:5173", True),
        (None, "http://localhost:5175", False),
        (
            "http://localhost:5175,http://127.0.0.1:5175",
            "http://localhost:5175",
            True,
        ),
        (
            "http://localhost:5175,http://127.0.0.1:5175",
            "http://127.0.0.1:5175",
            True,
        ),
        (
            "http://localhost:5175,http://127.0.0.1:5175",
            "http://localhost:5173",
            False,
        ),
        (
            "http://localhost:5175,http://127.0.0.1:5175",
            "https://externo.example.invalid",
            False,
        ),
    ],
)
def test_http_preflight_configurable(
    monkeypatch,
    configuracion,
    origen,
    permitido,
):
    from starlette.middleware.cors import CORSMiddleware

    if configuracion is None:
        monkeypatch.delenv("CORS_ORIGINS", raising=False)
    else:
        monkeypatch.setenv("CORS_ORIGINS", configuracion)

    async def aplicacion_falsa(scope, recibir, enviar):
        await enviar({
            "type": "http.response.start",
            "status": 200,
            "headers": [],
        })
        await enviar({
            "type": "http.response.body",
            "body": b"OK",
        })

    middleware = CORSMiddleware(
        app=aplicacion_falsa,
        allow_origins=get_cors_origins(),
        allow_credentials=True,
        allow_methods=["GET"],
        allow_headers=["*"],
    )

    async def ejecutar():
        mensajes = []

        scope = {
            "type": "http",
            "asgi": {"version": "3.0"},
            "http_version": "1.1",
            "method": "OPTIONS",
            "scheme": "http",
            "path": "/prueba-cors",
            "root_path": "",
            "query_string": b"",
            "server": ("localhost", 8000),
            "client": ("127.0.0.1", 12345),
            "headers": [
                (b"origin", origen.encode("ascii")),
                (
                    b"access-control-request-method",
                    b"GET",
                ),
            ],
        }

        async def recibir():
            return {
                "type": "http.request",
                "body": b"",
                "more_body": False,
            }

        async def enviar(mensaje):
            mensajes.append(mensaje)

        await middleware(scope, recibir, enviar)

        respuesta = next(
            mensaje
            for mensaje in mensajes
            if mensaje["type"] == "http.response.start"
        )

        encabezados = {
            nombre.decode("ascii").lower(): valor.decode("ascii")
            for nombre, valor in respuesta["headers"]
        }

        return respuesta["status"], encabezados

    estado, encabezados = asyncio.run(ejecutar())

    autorizado = encabezados.get(
        "access-control-allow-origin"
    )

    if permitido:
        assert estado == 200
        assert autorizado == origen
    else:
        assert estado == 400
        assert autorizado != origen


def test_websocket_rechaza_origen_no_autorizado(monkeypatch):
    from app.websocket_router import crear_router_websocket

    monkeypatch.setenv(
        "CORS_ORIGINS",
        "http://localhost:5175",
    )

    class WebSocketFalso:
        headers = {"origin": "https://no-autorizado.example.invalid"}

        def __init__(self):
            self.codigos = []

        async def close(self, code):
            self.codigos.append(code)

        async def accept(self):
            raise AssertionError(
                "No debe aceptar un origen no autorizado."
            )

    router = crear_router_websocket(
        manager=None,
        SessionLocal=None,
        SECRET_KEY="clave_ficticia",
        ALGORITHM="HS256",
    )

    ruta = next(
        ruta
        for ruta in router.routes
        if getattr(ruta, "path", None) == "/ws/anomalias"
    )

    conexion = WebSocketFalso()

    asyncio.run(ruta.endpoint(conexion))

    assert conexion.codigos == [1008]
