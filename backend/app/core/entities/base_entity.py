"""
BaseEntity — OOP: Inheritance
==============================
Tüm domain entity'lerinin miras aldığı temel sınıf.
Ortak alanlar (id, created_at) burada tanımlanır.
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """SQLAlchemy DeclarativeBase — tüm modellerin ata sınıfı."""
    pass


class BaseEntity(Base):
    """
    Soyut temel entity sınıfı.

    OOP Prensipleri:
    - Inheritance: Tüm entity'ler bu sınıftan türetilir.
    - Encapsulation: Ortak alanlar merkezi olarak yönetilir.
    """
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
