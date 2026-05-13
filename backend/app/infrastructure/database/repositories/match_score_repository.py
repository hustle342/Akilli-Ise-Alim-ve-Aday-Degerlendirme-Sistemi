"""
MatchScore Repository — Infrastructure Layer
===============================================
IMatchScoreRepository arayüzünün SQLAlchemy implementasyonu.
"""

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.entities.application import Application
from app.core.entities.match_score import MatchScore
from app.core.interfaces.repositories import IMatchScoreRepository


class MatchScoreRepository(IMatchScoreRepository):
    """SQLAlchemy tabanlı MatchScore repository implementasyonu."""

    def __init__(self, session: Session):
        self._session = session

    def get_by_id(self, entity_id: int):
        return self._session.get(MatchScore, entity_id)

    def get_all(self) -> list:
        return self._session.query(MatchScore).all()

    def get_by_application(self, application_id: int):
        return (
            self._session.query(MatchScore)
            .filter(MatchScore.application_id == application_id)
            .first()
        )

    def get_stats_by_job(self, job_posting_id: int) -> dict:
        """İlan bazlı skor istatistikleri."""
        row = (
            self._session.query(
                func.count(MatchScore.id),
                func.avg(MatchScore.score),
                func.max(MatchScore.score),
                func.min(MatchScore.score),
            )
            .join(Application, Application.id == MatchScore.application_id)
            .filter(Application.job_posting_id == job_posting_id)
            .first()
        )
        return {
            "scored_count": int(row[0] or 0),
            "avg_score": round(float(row[1]), 2) if row[1] is not None else 0.0,
            "max_score": round(float(row[2]), 2) if row[2] is not None else 0.0,
            "min_score": round(float(row[3]), 2) if row[3] is not None else 0.0,
        }

    def get_avg_score_all(self) -> float:
        """Genel ortalama skor."""
        result = self._session.query(func.avg(MatchScore.score)).scalar()
        return round(float(result), 2) if result is not None else 0.0

    def add(self, entity) -> None:
        self._session.add(entity)

    def delete(self, entity) -> None:
        self._session.delete(entity)

    def commit(self) -> None:
        self._session.commit()
