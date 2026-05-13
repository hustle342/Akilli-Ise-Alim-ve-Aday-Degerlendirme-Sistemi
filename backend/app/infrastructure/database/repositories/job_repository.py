"""
Job Repository — Infrastructure Layer
=======================================
IJobRepository arayüzünün SQLAlchemy implementasyonu.
"""

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.core.entities.job_posting import JobPosting
from app.core.interfaces.repositories import IJobRepository


class JobRepository(IJobRepository):
    """SQLAlchemy tabanlı Job repository implementasyonu."""

    def __init__(self, session: Session):
        self._session = session

    def get_by_id(self, entity_id: int):
        return self._session.get(JobPosting, entity_id)

    def get_all(self) -> list:
        return self._session.query(JobPosting).all()

    def get_all_ordered(self) -> list:
        return (
            self._session.query(JobPosting)
            .order_by(desc(JobPosting.created_at), desc(JobPosting.id))
            .all()
        )

    def add(self, entity) -> None:
        self._session.add(entity)

    def delete(self, entity) -> None:
        self._session.delete(entity)

    def commit(self) -> None:
        self._session.commit()

    def refresh(self, entity) -> None:
        self._session.refresh(entity)
