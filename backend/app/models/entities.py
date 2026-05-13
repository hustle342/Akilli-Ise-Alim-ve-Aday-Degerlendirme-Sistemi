"""
Geriye Donuk Uyumluluk — entities.py
======================================
Eski import path'lerini yeni Core katmanina yonlendirir.
Tum enum ve entity siniflarini re-export eder.
"""

# Enum'lar
from app.core.enums import (  # noqa: F401
    UserRole,
    ApplicationStatus,
    InvitationType,
    InvitationStatus,
    AuditActorType,
)

# Entity'ler
from app.core.entities.user import User  # noqa: F401
from app.core.entities.job_posting import JobPosting  # noqa: F401
from app.core.entities.application import Application  # noqa: F401
from app.core.entities.match_score import MatchScore  # noqa: F401
from app.core.entities.invitation import Invitation  # noqa: F401
from app.core.entities.audit_log import AuditLog  # noqa: F401
