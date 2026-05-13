"""
Core Domain Enumerations
========================
Tüm domain enum tanımları bu modülde yer alır.
Dış katmanlardan bağımsızdır.
"""

from enum import Enum


class UserRole(str, Enum):
    """Kullanıcı rolleri."""
    CANDIDATE = "candidate"
    HR = "hr"
    ADMIN = "admin"


class ApplicationStatus(str, Enum):
    """Başvuru durumları."""
    APPLIED = "applied"
    SHORTLISTED = "shortlisted"
    REJECTED = "rejected"
    HIRED = "hired"


class InvitationType(str, Enum):
    """Davet türleri."""
    TEST = "test"
    INTERVIEW = "interview"


class InvitationStatus(str, Enum):
    """Davet durumları."""
    PENDING = "pending"
    SENT = "sent"
    COMPLETED = "completed"
    CANCELED = "canceled"


class AuditActorType(str, Enum):
    """Audit log aktör tipleri."""
    ANONYMOUS = "anonymous"
    AUTHENTICATED = "authenticated"


class ScoringStrategyType(str, Enum):
    """Skorlama strateji tipleri (Strategy Pattern)."""
    RULE_BASED = "rule_based"
    SEMANTIC = "semantic"


class EventType(str, Enum):
    """Domain event tipleri (Observer/ESB)."""
    APPLICATION_CREATED = "application.created"
    SCORE_CALCULATED = "score.calculated"
    INVITATION_SENT = "invitation.sent"
    USER_REGISTERED = "user.registered"
    JOB_CREATED = "job.created"
