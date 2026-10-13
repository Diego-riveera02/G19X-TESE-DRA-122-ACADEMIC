from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from datetime import datetime
from .database import Base

# --- TABLA DE OBSERVABILIDAD ---
class AnomalyLog(Base):
    __tablename__ = "anomaly_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    pipeline_name = Column(String, index=True)
    metric_type = Column(String)  # Ej: latencia, calidad, disponibilidad
    value = Column(Float)
    status = Column(String)       # Ej: Normal, Alerta, Crítico
    ai_recommendation = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

# --- TABLA DE USUARIOS ---
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nombre_completo = Column(String)
    correo = Column(String, unique=True, index=True) 
    telefono = Column(String, nullable=True)
    hashed_password = Column(String) 
    is_active = Column(Boolean, default=False) # Inactivo hasta verificar correo
    codigo_verificacion = Column(String, nullable=True) # Código de 6 dígitos
    fecha_registro = Column(DateTime, default=datetime.utcnow)