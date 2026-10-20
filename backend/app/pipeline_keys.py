
"""Claves de alta entropia para fuentes externas."""

import hashlib
import hmac
import secrets

from . import models


def emitir_clave(pipeline_id: int) -> str:
    secreto = secrets.token_urlsafe(32)
    return "plr_" + str(pipeline_id) + "_" + secreto


def calcular_hash(clave: str) -> str:
    return hashlib.sha256(
        clave.encode("utf-8")
    ).hexdigest()


def autenticar_clave(db, clave):
    if (
        not isinstance(clave, str)
        or len(clave) > 128
    ):
        return None

    partes = clave.split("_", 2)

    if (
        len(partes) != 3
        or partes[0] != "plr"
        or not partes[1].isascii()
        or not partes[1].isdecimal()
        or len(partes[1]) > 18
        or len(partes[2]) != 43
    ):
        return None

    pipeline = db.query(models.Pipeline).filter(
        models.Pipeline.id == int(partes[1]),
        models.Pipeline.revocado.is_(False)
    ).first()

    if pipeline is None:
        return None

    recibido = calcular_hash(clave)

    if not hmac.compare_digest(
        recibido,
        pipeline.clave_hash
    ):
        return None

    return pipeline
