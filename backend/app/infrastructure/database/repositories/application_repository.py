"""
Application Repository — Infrastructure Layer
================================================
IApplicationRepository arayüzünün SQLAlchemy implementasyonu.
"""

from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.core.entities.application import Application
from app.core.entities.match_score import MatchScore
from app.core.entities.user import User
from app.core.entities.job_posting import JobPosting
from app.core.entities.invitation import Invitation
from app.core.interfaces.repositories import IApplicationRepository


class ApplicationRepository(IApplicationRepository):
    """SQLAlchemy tabanlı Application repository implementasyonu."""

    def __init__(self, session: Session):
        self._session = session

    def get_by_id(self, entity_id: int):
        return self._session.get(Application, entity_id)

    def get_all(self) -> list:
        return self._session.query(Application).all()

    def get_by_candidate(self, candidate_id: int) -> list:
        """Adayın başvurularını job ve score bilgisiyle döndür."""
        return (
            self._session.query(Application, JobPosting, MatchScore)
            .join(JobPosting, JobPosting.id == Application.job_posting_id)
            .outerjoin(MatchScore, MatchScore.application_id == Application.id)
            .filter(Application.candidate_id == candidate_id)
            .order_by(desc(Application.created_at))
            .all()
        )

    def get_by_job(self, job_posting_id: int) -> list:
        """İlana yapılan başvuruları aday ve skor bilgisiyle döndür."""
        return (
            self._session.query(Application, User, MatchScore)
            .join(User, User.id == Application.candidate_id)
            .join(MatchScore, MatchScore.application_id == Application.id)
            .filter(Application.job_posting_id == job_posting_id)
            .order_by(desc(MatchScore.score), desc(Application.created_at))
            .all()
        )

    def count_by_job(self, job_posting_id: int) -> int:
        return (
            self._session.query(func.count(Application.id))
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

    def refresh(self, entity) -> None:
        self._session.refresh(entity)
