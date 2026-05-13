"""
Audit Middleware — Presentation Layer
=======================================
HTTP istek loglarini audit_logs tablosuna yazan middleware.
"""

from flask import request

from app.core.entities.audit_log import AuditLog
from app.core.enums import AuditActorType
from app.infrastructure.database.db_manager import db_manager


def write_audit_log(response):
    """After-request hook: her istegi audit log'a yazar."""
    session = db_manager.get_session()
    try:
        auth_payload = getattr(request, "auth", None) or {}
        user_id = auth_payload.get("user_id")
        role = auth_payload.get("role", "anonymous")
        actor_type = (
            AuditActorType.AUTHENTICATED if user_id is not None
            else AuditActorType.ANONYMOUS
        )
        ip_address = request.headers.get(
            "X-Forwarded-For", request.remote_addr or "unknown"
        )

        session.add(
            AuditLog(
                user_id=user_id,
                actor_type=actor_type,
                role=role,
                method=request.method,
                path=request.path,
                status_code=response.status_code,
                ip_address=ip_address,
            )
        )
        session.commit()
    except Exception:
        session.rollback()
    finally:
        session.close()

    return response
