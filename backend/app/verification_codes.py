
"""Proteccion de codigos temporales de autenticacion."""

import hashlib
import hmac
import re

PREFIJO = "hmac-sha256$v1$"
PROPOSITOS = {"verificacion", "recuperacion"}


def crear_hash_codigo(codigo, correo, proposito, secreto):
    """Protege un codigo de seis digitos con HMAC-SHA256."""

    codigo = str(codigo)

    if re.fullmatch(r"[0-9]{6}", codigo) is None:
        raise ValueError("Formato de codigo invalido")

    if proposito not in PROPOSITOS:
        raise ValueError("Proposito de codigo invalido")

    if not isinstance(correo, str) or not correo.strip():
        raise ValueError("Correo invalido")

    if not isinstance(secreto, str) or not secreto:
        raise ValueError("Secreto no configurado")

    contenido = (
        "plurione/codigo/v1/"
        + proposito
        + "/"
        + correo.strip().casefold()
        + "/"
        + codigo
    )

    firma = hmac.new(
        secreto.encode("utf-8"),
        contenido.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    return PREFIJO + firma


def verificar_codigo_guardado(
    guardado,
    recibido,
    correo,
    proposito,
    secreto,
):
    """Acepta HMAC nuevo o codigo legado aun vigente."""

    if not isinstance(guardado, str):
        return False

    recibido = str(recibido)

    if re.fullmatch(r"[0-9]{6}", recibido) is None:
        return False

    if guardado.startswith(PREFIJO):
        firma = guardado[len(PREFIJO):]

        if re.fullmatch(r"[0-9a-f]{64}", firma) is None:
            return False

        esperado = crear_hash_codigo(
            recibido,
            correo,
            proposito,
            secreto,
        )

        return hmac.compare_digest(guardado, esperado)

    # Compatibilidad temporal con codigos anteriores.
    # La caducidad, el proposito y los intentos se
    # comprueban en el endpoint antes de llamar aqui.
    if re.fullmatch(r"[0-9]{6}", guardado):
        return hmac.compare_digest(guardado, recibido)

    return False
