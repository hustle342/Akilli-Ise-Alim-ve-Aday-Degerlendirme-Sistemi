"""
Invitation Repository — Infrastructure Layer
===============================================
IInvitationRepository arayüzünün SQLAlchemy implementasyonu.
"""

from typing import Optional

from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.core.entities.application import Application
from app.core.entities.invitation import Invitation
from app.core.entities.job_posting import JobPosting
from app.core.entities.user import User
from app.core.enums import InvitationStatus
from app.core.interfaces.repositories import IInvitationRepository


class InvitationRepository(IInvitationRepository):
    """SQLAlchemy tabanlı Invitation repository implementasyonu."""

    def __init__(self, session: Session):
        self._session = session

    def get_by_id(self, entity_id: int):
        return self._session.get(Invitation, entity_id)

    def get_all(self) -> list:
        return self._session.query(Invitation).all()

    def get_by_application(self, application_id: int):
        return (
            self._session.query(Invitation)
            .filter(Invitation.application_id == application_id)
            .order_by(desc(Invitation.created_at))
            .first()
        )

    def get_filtered(
        self, status: Optional[str] = None, job_posting_id: Optional[int] = None
    ) -> list:
        """Filtreli davet listesi — Application, User, JobPosting ile birlikte."""
        query = (
            self._session.query(Invitation, Application, User, JobPosting)
            .join(Application, Application.id == Invitation.application_id)
            .join(User, User.id == Application.candidate_id)
            .join(JobPosting, JobPosting.id == Application.job_posting_id)
        )

        if status:
            query = query.filter(Invitation.status == InvitationStatus(status))
        if job_posting_id:
            query = query.filter(JobPosting.id == job_posting_id)

        return query.order_by(desc(Invitation.created_at)).all()

    def count_by_job(self, job_posting_id: int) -> int:
        return (
            self._session.query(func.count(Invitation.id))
            .join(Application, Application.id == Invitation.application_id)
            .filter(Application.job_posting_id == job_posting_id)
            .scalar()
            or 0
        )

    def add(self, entity) -> None:
        self._session.add(entity)

    def delete(self, entity) -> None:
        self._session.delete(entity)

    def commit(self) -> None:
        self._session.commit()
