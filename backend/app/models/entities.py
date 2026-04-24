from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import DateTime, Enum as SqlEnum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class UserRole(str, Enum):
    CANDIDATE = "candidate"
    HR = "hr"
    ADMIN = "admin"


class ApplicationStatus(str, Enum):
    APPLIED = "applied"
    SHORTLISTED = "shortlisted"
    REJECTED = "rejected"
    HIRED = "hired"


class InvitationType(str, Enum):
    TEST = "test"
    INTERVIEW = "interview"


class InvitationStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    COMPLETED = "completed"
    CANCELED = "canceled"


class AuditActorType(str, Enum):
    ANONYMOUS = "anonymous"
    AUTHENTICATED = "authenticated"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(180), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    role: Mapped[UserRole] = mapped_column(SqlEnum(UserRole), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    applications: Mapped[list["Application"]] = relationship(back_populates="candidate")


class JobPosting(Base):
    __tablename__ = "job_postings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    min_years_experience: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    required_skills: Mapped[str] = mapped_column(Text, default="", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    applications: Mapped[list["Application"]] = relationship(back_populates="job_posting")


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    job_posting_id: Mapped[int] = mapped_column(ForeignKey("job_postings.id"), nullable=False)
    cv_path: Mapped[str] = mapped_column(String(255), nullable=False)
    parsed_summary: Mapped[str] = mapped_column(Text, default="", nullable=False)
    status: Mapped[ApplicationStatus] = mapped_column(
        SqlEnum(ApplicationStatus), default=ApplicationStatus.APPLIED, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    candidate: Mapped[User] = relationship(back_populates="applications")
    job_posting: Mapped[JobPosting] = relationship(back_populates="applications")
    scores: Mapped[list["MatchScore"]] = relationship(back_populates="application")
    invitations: Mapped[list["Invitation"]] = relationship(back_populates="application")


class MatchScore(Base):
    __tablename__ = "match_scores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    application_id: Mapped[int] = mapped_column(ForeignKey("applications.id"), nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    scoring_version: Mapped[str] = mapped_column(String(40), default="v1-rule-based", nullable=False)
    rationale: Mapped[str] = mapped_column(Text, default="", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    application: Mapped[Application] = relationship(back_populates="scores")


class Invitation(Base):
    __tablename__ = "invitations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    application_id: Mapped[int] = mapped_column(ForeignKey("applications.id"), nullable=False)
    invitation_type: Mapped[InvitationType] = mapped_column(SqlEnum(InvitationType), nullable=False)
    status: Mapped[InvitationStatus] = mapped_column(
        SqlEnum(InvitationStatus), default=InvitationStatus.PENDING, nullable=False
    )
    scheduled_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    application: Mapped[Application] = relationship(back_populates="invitations")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=True)
    actor_type: Mapped[AuditActorType] = mapped_column(
        SqlEnum(AuditActorType), default=AuditActorType.ANONYMOUS, nullable=False
    )
    role: Mapped[str] = mapped_column(String(40), default="anonymous", nullable=False)
    method: Mapped[str] = mapped_column(String(12), nullable=False)
    path: Mapped[str] = mapped_column(String(255), nullable=False)
    status_code: Mapped[int] = mapped_column(Integer, nullable=False)
    ip_address: Mapped[str] = mapped_column(String(64), default="unknown", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
