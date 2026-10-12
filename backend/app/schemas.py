from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# --- ESQUEMAS DE OBSERVABILIDAD (Los que ya tenías) ---
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

# --- NUEVOS ESQUEMAS DE USUARIOS ---
class UserBase(BaseModel):
    nombre_completo: str
    correo: str
    telefono: Optional[str] = None

class UserCreate(UserBase):
    password: str  # Se recibe en texto plano, pero el backend la encriptará antes de guardarla

class UserResponse(UserBase):
    id: int
    is_active: bool
    fecha_registro: datetime
    
    # Nota: No incluimos 'password' aquí por seguridad. Nunca se devuelve al frontend.

    class Config:
        from_attributes = True