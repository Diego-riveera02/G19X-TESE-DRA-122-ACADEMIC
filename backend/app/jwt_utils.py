"""Generacion de tokens JWT."""

from datetime import timedelta
from .tiempo import ahora_utc
from jose import jwt


def encode_access_token(data: dict, expires_delta: timedelta | None=None, *, secret_key: str, algorithm: str):
    to_encode = data.copy()
    expire = ahora_utc() + (expires_delta if expires_delta else timedelta(minutes=15))
    to_encode.update({'exp': expire})
    return jwt.encode(to_encode, secret_key, algorithm=algorithm)
