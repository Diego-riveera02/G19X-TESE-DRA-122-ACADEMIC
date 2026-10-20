from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint

from .database import Base


# Tabla de observabilidad
class AnomalyLog(Base):
    __tablename__ = "anomaly_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    pipeline_name = Column(String, index=True)
    metric_type = Column(String)
    value = Column(Float)
    status = Column(String)
    ai_recommendation = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    archived = Column(Boolean, nullable=False, server_default="false")
    archived_at = Column(DateTime(timezone=True), nullable=True)


# Tabla de usuarios
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nombre_completo = Column(String)
    correo = Column(String, unique=True, index=True)
    telefono = Column(String, nullable=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=False)
    codigo_verificacion = Column(String, nullable=True)

    # Columnas existentes en PostgreSQL para proteger los codigos.
    codigo_expira_en = Column(DateTime, nullable=True)
    codigo_intentos = Column(Integer, nullable=False, default=0)
    codigo_proposito = Column(String, nullable=True)

    fecha_registro = Column(DateTime, default=datetime.utcnow)


# Cuotas por origen y endpoint; persistentes en PostgreSQL.
class AuthRateLimit(Base):
    __tablename__ = "auth_rate_limits"

    clave = Column(String(64), primary_key=True)
    inicio_ventana = Column(DateTime, nullable=False)
    cantidad = Column(Integer, nullable=False, default=0)


class Pipeline(Base):
    __tablename__ = "pipelines"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "nombre",
            name="uq_pipeline_user_name"
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    nombre = Column(String(100), nullable=False)
    clave_hash = Column(String(64), nullable=False)
    revocado = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false"
    )
    creado_en = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )
