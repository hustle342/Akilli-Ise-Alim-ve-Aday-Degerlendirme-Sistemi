"""
Geriye Donuk Uyumluluk Modulu
==============================
Eski import path'lerini yeni Onion Architecture'a yonlendirir.
Bu modul sayesinde mevcut testler ve diger moduller calismaya devam eder.
"""

from app.core.entities.base_entity import Base
from app.core.entities.user import User
from app.core.entities.job_posting import JobPosting
from app.core.entities.application import Application
from app.core.entities.match_score import MatchScore
from app.core.entities.invitation import Invitation
from app.core.entities.audit_log import AuditLog

__all__ = [
    "Base",
    "Application",
    "AuditLog",
    "Invitation",
    "JobPosting",
    "MatchScore",
    "User",
]
