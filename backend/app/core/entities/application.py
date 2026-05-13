"""Application Entity — Domain Model."""

from sqlalchemy import Enum as SqlEnum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.entities.base_entity import BaseEntity
from app.core.enums import ApplicationStatus


class Application(BaseEntity):
    """Başvuru domain entity'si."""
    __tablename__ = "applications"

    candidate_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    job_posting_id: Mapped[int] = mapped_column(ForeignKey("job_postings.id"), nullable=False)
    cv_path: Mapped[str] = mapped_column(String(255), nullable=False)
    parsed_summary: Mapped[str] = mapped_column(Text, default="", nullable=False)
    status: Mapped[ApplicationStatus] = mapped_column(
        SqlEnum(ApplicationStatus), default=ApplicationStatus.APPLIED, nullable=False
    )

    # Relationships
    candidate: Mapped["User"] = relationship(back_populates="applications")  # noqa: F821
    job_posting: Mapped["JobPosting"] = relationship(back_populates="applications")  # noqa: F821
    scores: Mapped[list["MatchScore"]] = relationship(back_populates="application")  # noqa: F821
    invitations: Mapped[list["Invitation"]] = relationship(  # noqa: F821
        back_populates="application"
    )
