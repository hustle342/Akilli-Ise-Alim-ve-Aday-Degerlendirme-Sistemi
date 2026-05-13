"""
CQRS Queries — Okuma islemleri.
Veri degisikligi yapmadan sadece okuma yapar.
"""

from dataclasses import dataclass
from typing import Optional, List


@dataclass
class GetJobsQuery:
    """Ilan listeleme sorgusu."""
    pass


class GetJobsHandler:
    """CQRS Query Handler — Ilan listele."""

    def __init__(self, job_repository):
        self._job_repo = job_repository

    def handle(self, query: GetJobsQuery) -> list:
        jobs = self._job_repo.get_all_ordered()
        return [
            {
                "id": j.id,
                "title": j.title,
                "description": j.description,
                "min_years_experience": j.min_years_experience,
                "required_skills": [s.strip() for s in j.required_skills.split(",") if s.strip()],
            }
            for j in jobs
        ]


@dataclass
class GetMyApplicationsQuery:
    """Aday basvuru listeleme sorgusu."""
    candidate_id: int


class GetMyApplicationsHandler:
    """CQRS Query Handler — Aday basvurulari."""

    def __init__(self, application_repository, invitation_repository):
        self._app_repo = application_repository
        self._inv_repo = invitation_repository

    def handle(self, query: GetMyApplicationsQuery) -> list:
        rows = self._app_repo.get_by_candidate(query.candidate_id)
        results = []
        for application, job, match_score in rows:
            invitation = self._inv_repo.get_by_application(application.id)
            results.append({
                "application_id": application.id,
                "job_posting_id": job.id,
                "job_title": job.title,
                "status": application.status.value,
                "parsed_summary": application.parsed_summary,
                "match_score": None if match_score is None else float(match_score.score),
                "invitation": None if invitation is None else {
                    "type": invitation.invitation_type.value,
                    "status": invitation.status.value,
                },
            })
        return results


@dataclass
class GetJobCandidatesQuery:
    """Ilan aday listeleme sorgusu."""
    job_posting_id: int
    min_score: Optional[float] = None


class GetJobCandidatesHandler:
    """CQRS Query Handler — Ilan adaylari."""

    def __init__(self, job_repository, application_repository, invitation_repository):
        self._job_repo = job_repository
        self._app_repo = application_repository
        self._inv_repo = invitation_repository

    def handle(self, query: GetJobCandidatesQuery) -> dict:
        job = self._job_repo.get_by_id(query.job_posting_id)
        if job is None:
            return {"error": "ilan bulunamadi"}

        rows = self._app_repo.get_by_job(query.job_posting_id)
        results = []
        for application, user, match_score in rows:
            score = float(match_score.score)
            if query.min_score is not None and score < query.min_score:
                continue
            invitation = self._inv_repo.get_by_application(application.id)
            results.append({
                "application_id": application.id,
                "candidate": {
                    "id": user.id, "full_name": user.full_name, "email": user.email
                },
                "match_score": score,
                "status": application.status.value,
                "invitation": None if invitation is None else {
                    "id": invitation.id,
                    "type": invitation.invitation_type.value,
                    "status": invitation.status.value,
                },
            })
        return {
            "job_posting_id": job.id,
            "job_title": job.title,
            "candidate_count": len(results),
            "candidates": results,
        }


@dataclass
class GetReportQuery:
    """Rapor sorgusu."""
    job_posting_id: Optional[int] = None


class GetReportHandler:
    """CQRS Query Handler — Raporlar."""

    def __init__(self, job_repo, app_repo, score_repo, inv_repo, user_repo):
        self._job_repo = job_repo
        self._app_repo = app_repo
        self._score_repo = score_repo
        self._inv_repo = inv_repo
        self._user_repo = user_repo

    def handle_job_report(self, job_posting_id: int) -> dict:
        job = self._job_repo.get_by_id(job_posting_id)
        if job is None:
            return {"error": "ilan bulunamadi"}

        app_count = self._app_repo.count_by_job(job_posting_id)
        stats = self._score_repo.get_stats_by_job(job_posting_id)
        inv_count = self._inv_repo.count_by_job(job_posting_id)
        inv_rate = round((inv_count / app_count) * 100, 2) if app_count > 0 else 0.0

        return {
            "job_posting_id": job.id,
            "job_title": job.title,
            "applications_count": int(app_count),
            **stats,
            "invitation_count": int(inv_count),
            "invitation_rate_percent": inv_rate,
        }

    def handle_overview(self) -> dict:
        from sqlalchemy import func
        from app.core.entities.job_posting import JobPosting
        from app.core.entities.application import Application
        from app.core.entities.invitation import Invitation
        from app.core.entities.user import User
        from app.core.enums import UserRole

        total_jobs = len(self._job_repo.get_all())
        total_candidates = self._user_repo.count_by_role(UserRole.CANDIDATE)
        total_applications = len(self._app_repo.get_all())
        total_invitations = len(self._inv_repo.get_all())
        avg_score = self._score_repo.get_avg_score_all()

        return {
            "total_jobs": total_jobs,
            "total_candidates": total_candidates,
            "total_applications": total_applications,
            "total_invitations": total_invitations,
            "avg_score_all": avg_score,
        }
