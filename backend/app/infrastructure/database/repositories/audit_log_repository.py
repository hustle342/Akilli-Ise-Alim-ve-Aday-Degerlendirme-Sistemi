"""
AuditLog Repository — Infrastructure Layer
=============================================
IAuditLogRepository arayüzünün SQLAlchemy implementasyonu.
"""

from typing import Optional

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.core.entities.audit_log import AuditLog
from app.core.interfaces.repositories import IAuditLogRepository


class AuditLogRepository(IAuditLogRepository):
    """SQLAlchemy tabanlı AuditLog repository implementasyonu."""

    def __init__(self, session: Session):
        self._session = session

    def get_by_id(self, entity_id: int):
        return self._session.get(AuditLog, entity_id)

    def get_all(self) -> list:
        return self._session.query(AuditLog).all()

    def get_filtered(
        self,
        limit: int = 50,
        path_filter: Optional[str] = None,
        method_filter: Optional[str] = None,
    ) -> list:
        query = self._session.query(AuditLog)

        if path_filter:
            query = query.filter(AuditLog.path.contains(path_filter))
        if method_filter:
            query = query.filter(AuditLog.method == method_filter.upper())

        return (
            query.order_by(desc(AuditLog.created_at))
            .limit(max(1, min(limit, 200)))
            .all()
        )

    def add(self, entity) -> None:
        self._session.add(entity)

    def delete(self, entity) -> None:
        self._session.delete(entity)

    def commit(self) -> None:
        self._session.commit()
