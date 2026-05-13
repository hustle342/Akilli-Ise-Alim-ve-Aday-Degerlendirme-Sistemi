"""
Geriye Donuk Uyumluluk — db.py
=================================
DB erisim noktasi artik infrastructure.database.db_manager'da (Singleton).
"""

from app.infrastructure.database.db_manager import (  # noqa: F401
    engine,
    SessionLocal,
    ensure_schema,
    get_db_session,
)
