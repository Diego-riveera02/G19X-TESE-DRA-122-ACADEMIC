from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from datetime import datetime
from .database import Base

# --- TABLA DE OBSERVABILIDAD (La que ya tenías) ---
class AnomalyLog(Base):
    __tablename__ = "anomaly_logs"

    id = Column(Integer, primary_key=True, index=True)
    pipeline_name = Column(String, index=True)
    metric_type = Column(String)  # Ej: latencia, calidad, disponibilidad
    value = Column(Float)
    status = Column(String)       # Ej: Normal, Alerta, Crítico
    ai_recommendation = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

# --- NUEVA TABLA DE USUARIOS (Sistema de Login y Alertas) ---
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nombre_completo = Column(String)
    correo = Column(String, unique=True, index=True) # Se usa para Iniciar Sesión y enviar alertas
    telefono = Column(String, nullable=True)
    hashed_password = Column(String) # Contraseña encriptada por seguridad
    is_active = Column(Boolean, default=True) # Para saber si el usuario tiene acceso
    fecha_registro = Column(DateTime, default=datetime.utcnow)