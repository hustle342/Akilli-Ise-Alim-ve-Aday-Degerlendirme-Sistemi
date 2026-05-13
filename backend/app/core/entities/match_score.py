"""MatchScore Entity — Domain Model."""

from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.entities.base_entity import BaseEntity


class MatchScore(BaseEntity):
    """Uyum skoru domain entity'si."""
    __tablename__ = "match_scores"

    application_id: Mapped[int] = mapped_column(ForeignKey("applications.id"), nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    scoring_version: Mapped[str] = mapped_column(
        String(40), default="v1-rule-based", nullable=False
    )
    rationale: Mapped[str] = mapped_column(Text, default="", nullable=False)

    # Relationships
    application: Mapped["Application"] = relationship(back_populates="scores")  # noqa: F821
