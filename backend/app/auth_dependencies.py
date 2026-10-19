"""Validacion de usuarios autenticados."""

from fastapi import HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from . import models


def resolve_current_user(
    token: str,
    db: Session,
    *,
    secret_key: str,
    algorithm: str,
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        correo: str = payload.get("sub")
        if correo is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.correo == correo).first()
    if user is None or not user.is_active:
        raise credentials_exception
    return user
