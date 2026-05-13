"""
Core Domain Entities
====================
Tüm domain entity sınıfları burada tanımlanır.
BaseEntity'den kalıtım alırlar (OOP: Inheritance).
"""

from app.core.entities.base_entity import Base, BaseEntity
from app.core.entities.user import User
from app.core.entities.job_posting import JobPosting
from app.core.entities.application import Application
from app.core.entities.match_score import MatchScore
from app.core.entities.invitation import Invitation
from app.core.entities.audit_log import AuditLog

__all__ = [
    "Base",
    "BaseEntity",
    "User",
    "JobPosting",
    "Application",
    "MatchScore",
    "Invitation",
    "AuditLog",
]
