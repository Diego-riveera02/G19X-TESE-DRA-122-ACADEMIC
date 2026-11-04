"""Utilidades compartidas para fechas UTC."""

from datetime import datetime, timezone


def ahora_utc() -> datetime:
    """Obtener UTC sin tzinfo para columnas existentes DateTime."""
    return datetime.now(timezone.utc).replace(tzinfo=None)
