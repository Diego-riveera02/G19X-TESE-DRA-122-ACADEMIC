from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel
from pydantic import Field, validator


# Esquemas de observabilidad
class AnomalyLogBase(BaseModel):
    pipeline_name: str
    metric_type: str
    value: float
    status: str
    ai_recommendation: Optional[str] = None


class AnomalyLogCreate(AnomalyLogBase):
    pass


class AnomalyLogResponse(AnomalyLogBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True


# Esquemas de usuarios
class UserBase(BaseModel):
    nombre_completo: str
    correo: str
    telefono: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UserResponse(UserBase):
    id: int
    is_active: bool
    fecha_registro: datetime

    # No devolver contrasenas, hashes ni codigos al frontend.
    class Config:
        from_attributes = True


class MetricaEntrada(BaseModel):
    """Metrica enviada por un usuario autenticado."""

    pipeline: str = Field(min_length=2, max_length=100)
    metrica: Literal[
        "latencia_ms",
        "datos_corruptos_%",
        "tasa_fallos_%"
    ]
    valor: float = Field(ge=0, le=10000, allow_inf_nan=False)

    @validator("pipeline")
    def validar_pipeline(cls, valor):
        if not valor.strip() or any(ord(c) < 32 for c in valor):
            raise ValueError("Nombre de pipeline invalido")
        return valor.strip()

    @validator("valor")
    def validar_valor(cls, valor, values):
        tipo = values.get("metrica")
        if tipo in ("datos_corruptos_%", "tasa_fallos_%"):
            if valor > 100:
                raise ValueError("El porcentaje excede 100")
        return valor

    class Config:
        extra = "forbid"
