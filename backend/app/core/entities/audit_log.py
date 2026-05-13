"""AuditLog Entity — Domain Model."""

from sqlalchemy import Enum as SqlEnum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.entities.base_entity import BaseEntity
from app.core.enums import AuditActorType


class AuditLog(BaseEntity):
    """Audit log domain entity'si."""
    __tablename__ = "audit_logs"

    user_id: Mapped[int] = mapped_column(Integer, nullable=True)
    actor_type: Mapped[AuditActorType] = mapped_column(
        SqlEnum(AuditActorType), default=AuditActorType.ANONYMOUS, nullable=False
    )
    role: Mapped[str] = mapped_column(String(40), default="anonymous", nullable=False)
    method: Mapped[str] = mapped_column(String(12), nullable=False)
    path: Mapped[str] = mapped_column(String(255), nullable=False)
    status_code: Mapped[int] = mapped_column(Integer, nullable=False)
    ip_address: Mapped[str] = mapped_column(String(64), default="unknown", nullable=False)
