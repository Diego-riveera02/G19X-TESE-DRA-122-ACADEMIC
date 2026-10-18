"""Compatibilidad de esquemas PostgreSQL anteriores a la seguridad de codigos.

La instalacion nueva sigue creandose con models.Base.metadata.create_all().
Las instalaciones que ya tienen `users` reciben solamente las columnas faltantes.
Todas las operaciones se ejecutan dentro de la transaccion que proporciona el llamador.

Este modulo cubre exclusivamente las columnas de autenticacion incorporadas en 2026.
Los futuros cambios de esquema deberan agregarse como migraciones nuevas/versionadas.
"""

import re

from sqlalchemy import inspect, text
from sqlalchemy.engine import Connection


def migrate_legacy_auth_schema(conexion: Connection, schema: str = "public") -> None:
    """Actualiza sin borrar datos una tabla `users` anterior a las columnas de codigos.

    Para probar aisladamente, `schema` acepta el nombre de un esquema temporal
    compuesto solo por letras minusculas, numeros y guiones bajos.
    """
    if conexion.dialect.name != "postgresql":
        raise RuntimeError("La migracion de PluriOne requiere PostgreSQL")

    if not re.fullmatch(r"[a-z_][a-z0-9_]*", schema):
        raise ValueError("Nombre de esquema no permitido")

    # Serializar cambios concurrentes en la misma base de datos.
    conexion.execute(text("SELECT pg_advisory_xact_lock(4710, 1)"))

    # Una BD completamente nueva sera creada por SQLAlchemy despues de esto.
    if not inspect(conexion).has_table("users", schema=schema):
        return

    tabla = f'"{schema}"."users"'
    conexion.execute(text(
        f"ALTER TABLE {tabla} ADD COLUMN IF NOT EXISTS "
        "codigo_expira_en TIMESTAMP WITHOUT TIME ZONE"
    ))
    conexion.execute(text(
        f"ALTER TABLE {tabla} ADD COLUMN IF NOT EXISTS "
        "codigo_intentos INTEGER DEFAULT 0"
    ))
    conexion.execute(text(
        f"ALTER TABLE {tabla} ADD COLUMN IF NOT EXISTS "
        "codigo_proposito VARCHAR"
    ))

    # Los usuarios existentes mantienen sus datos; cualquier contador antiguo
    # nulo se normaliza a cero y se evita que aparezcan nuevos valores nulos.
    conexion.execute(text(
        f"UPDATE {tabla} SET codigo_intentos = 0 WHERE codigo_intentos IS NULL"
    ))
    conexion.execute(text(
        f"ALTER TABLE {tabla} ALTER COLUMN codigo_intentos SET DEFAULT 0"
    ))
    conexion.execute(text(
        f"ALTER TABLE {tabla} ALTER COLUMN codigo_intentos SET NOT NULL"
    ))
