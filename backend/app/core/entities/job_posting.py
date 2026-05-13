"""JobPosting Entity — Domain Model."""

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.entities.base_entity import BaseEntity


class JobPosting(BaseEntity):
    """İş ilanı domain entity'si."""
    __tablename__ = "job_postings"

    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    min_years_experience: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    required_skills: Mapped[str] = mapped_column(Text, default="", nullable=False)

    # Relationships
    applications: Mapped[list["Application"]] = relationship(  # noqa: F821
        back_populates="job_posting"
    )
