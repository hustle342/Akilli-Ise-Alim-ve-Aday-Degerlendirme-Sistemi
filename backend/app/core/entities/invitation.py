"""Invitation Entity — Domain Model."""

from datetime import datetime

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.entities.base_entity import BaseEntity
from app.core.enums import InvitationStatus, InvitationType


class Invitation(BaseEntity):
    """Davet domain entity'si."""
    __tablename__ = "invitations"

    application_id: Mapped[int] = mapped_column(ForeignKey("applications.id"), nullable=False)
    invitation_type: Mapped[InvitationType] = mapped_column(
        SqlEnum(InvitationType), nullable=False
    )
    status: Mapped[InvitationStatus] = mapped_column(
        SqlEnum(InvitationStatus), default=InvitationStatus.PENDING, nullable=False
    )
    scheduled_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # Relationships
    application: Mapped["Application"] = relationship(  # noqa: F821
        back_populates="invitations"
    )
