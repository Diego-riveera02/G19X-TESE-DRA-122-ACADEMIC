"""Configuracion compartida de origenes HTTP y WebSocket."""

import os
from urllib.parse import urlsplit


DEFAULT_CORS_ORIGINS = (
    "http://localhost:5173",
    "http://127.0.0.1:5173",
)


def get_cors_origins():
    """Obtener una lista explicita de origenes autorizados."""

    configuracion = os.getenv("CORS_ORIGINS")

    if configuracion is None or not configuracion.strip():
        return list(DEFAULT_CORS_ORIGINS)

    permitidos = []

    for elemento in configuracion.split(","):
        origen = elemento.strip()

        if not origen or "*" in origen:
            raise ValueError(
                "CORS_ORIGINS contiene un origen vacio o comodin."
            )

        try:
            partes = urlsplit(origen)
            puerto = partes.port
        except ValueError as error:
            raise ValueError(
                f"Origen CORS invalido: {origen}"
            ) from error

        if (
            partes.scheme not in ("http", "https")
            or not partes.hostname
            or partes.username is not None
            or partes.password is not None
            or partes.path
            or partes.query
            or partes.fragment
        ):
            raise ValueError(
                f"Origen CORS invalido: {origen}"
            )

        if origen not in permitidos:
            permitidos.append(origen)

    return permitidos
