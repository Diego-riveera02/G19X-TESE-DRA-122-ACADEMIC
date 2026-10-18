from datetime import datetime
from typing import Optional

from pydantic import BaseModel


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
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    fecha_registro: datetime

    # No devolver contrasenas, hashes ni codigos al frontend.
    class Config:
        from_attributes = True
