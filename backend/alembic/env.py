"""
Alembic Environment Configuration
====================================
SQLAlchemy model metadata'sini Alembic ile entegre eder.
Onion Architecture'daki Core katmanindaki entity'leri kullanir.
"""

import sys
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Backend dizinini Python path'e ekle
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Core katmanindaki tum entity'leri import et (metadata icin)
from app.core.entities import Base  # noqa: E402
from app.core.entities import (  # noqa: E402, F401
    User, JobPosting, Application, MatchScore, Invitation, AuditLog
)
from app.infrastructure.config import settings  # noqa: E402

# Alembic Config objesi
config = context.config

# logging konfigurasyonu
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# SQLAlchemy metadata — otomatik migration uretimi icin
target_metadata = Base.metadata

# DATABASE_URL'yi ortam degiskeninden al (alembic.ini'yi ezer)
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)


def run_migrations_offline() -> None:
    """
    Offline modda migration calistir.
    Veritabani baglantisi olmadan SQL script uretir.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Online modda migration calistir.
    Veritabanina baglanarak migration uygular.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
