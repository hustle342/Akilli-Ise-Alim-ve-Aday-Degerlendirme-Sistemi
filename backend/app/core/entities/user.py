"""User Entity — Domain Model."""

from sqlalchemy import Enum as SqlEnum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.entities.base_entity import BaseEntity
from app.core.enums import UserRole


class User(BaseEntity):
    """Kullanıcı domain entity'si (Candidate, HR, Admin)."""
    __tablename__ = "users"

    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(180), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    role: Mapped[UserRole] = mapped_column(SqlEnum(UserRole), nullable=False)

    # Relationships
    applications: Mapped[list["Application"]] = relationship(  # noqa: F821
        back_populates="candidate"
    )
