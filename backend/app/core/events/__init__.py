"""
Domain Events — Observer + ESB
================================
Sistemdeki önemli olayları temsil eden event sınıfları.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict


@dataclass(frozen=True)
class DomainEvent:
    """Tüm domain event'lerin temel sınıfı."""
    event_type: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    data: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ApplicationCreatedEvent(DomainEvent):
    """Yeni başvuru oluşturulduğunda tetiklenir."""
    event_type: str = "application.created"


@dataclass(frozen=True)
class ScoreCalculatedEvent(DomainEvent):
    """Uyum skoru hesaplandığında tetiklenir."""
    event_type: str = "score.calculated"


@dataclass(frozen=True)
class InvitationSentEvent(DomainEvent):
    """Davet gönderildiğinde tetiklenir."""
    event_type: str = "invitation.sent"


@dataclass(frozen=True)
class UserRegisteredEvent(DomainEvent):
    """Yeni kullanıcı kayıt olduğunda tetiklenir."""
    event_type: str = "user.registered"


@dataclass(frozen=True)
class JobCreatedEvent(DomainEvent):
    """Yeni iş ilanı oluşturulduğunda tetiklenir."""
    event_type: str = "job.created"
