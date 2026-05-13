"""
DatabaseManager — Creational: Singleton Pattern
=================================================
Veritabanı bağlantı yönetiminin tekil instance üzerinden yapılmasını sağlar.
Engine ve SessionLocal bir kez oluşturulur ve tüm uygulamada paylaşılır.
"""

import threading

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

from app.infrastructure.config import settings


class DatabaseManager:
    """
    Singleton Database Manager.

    Veritabanı engine ve session factory'sini tek noktadan yönetir.
    Thread-safe Singleton implementasyonu.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        # PostgreSQL: bağlantı havuzu ile optimize edilmiş engine
        # SQLite: basit engine (havuz desteklemez)
        engine_kwargs = {"future": True}
        if settings.is_postgresql:
            engine_kwargs.update({
                "pool_size": settings.DB_POOL_SIZE,
                "max_overflow": settings.DB_MAX_OVERFLOW,
                "pool_recycle": settings.DB_POOL_RECYCLE,
                "pool_pre_ping": True,  # Bağlantı canlılık kontrolü
            })

        self.engine = create_engine(settings.DATABASE_URL, **engine_kwargs)
        self.SessionLocal = sessionmaker(
            bind=self.engine, autoflush=False, autocommit=False, future=True
        )

    def get_session(self):
        """Yeni bir veritabanı session'ı oluştur."""
        return self.SessionLocal()

    def get_session_generator(self):
        """Context manager tarzı session generator."""
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()

    def ensure_schema(self) -> None:
        """Şema uyumluluk kontrolü (migration fallback)."""
        inspector = inspect(self.engine)
        if "users" not in inspector.get_table_names():
            return

        user_columns = {column["name"] for column in inspector.get_columns("users")}
        if "password_hash" not in user_columns:
            with self.engine.begin() as connection:
                connection.execute(
                    text(
                        "ALTER TABLE users ADD COLUMN password_hash VARCHAR(255) NOT NULL DEFAULT ''"
                    )
                )

    def create_tables(self, base) -> None:
        """Tüm tabloları oluştur."""
        base.metadata.create_all(bind=self.engine)

    @classmethod
    def reset(cls):
        """Test ortamında singleton'ı sıfırla."""
        with cls._lock:
            cls._instance = None


# Geriye dönük uyumluluk için modül seviyesinde erişim noktaları
db_manager = DatabaseManager()
engine = db_manager.engine
SessionLocal = db_manager.SessionLocal


def ensure_schema() -> None:
    """Geriye dönük uyumluluk."""
    db_manager.ensure_schema()


def get_db_session():
    """Geriye dönük uyumluluk."""
    return db_manager.get_session()
