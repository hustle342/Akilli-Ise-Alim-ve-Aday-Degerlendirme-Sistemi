"""
RecruitmentFacade — Structural: Facade Pattern
================================================
Birden fazla alt servisi tek bir basit arayuz uzerinden sunar.
Frontend (Presentation katmani), karmasik is akislarini
bilmeden tek bir noktadan erisir.

Facade arkasindaki servisler:
- UserRepository, JobRepository, ApplicationRepository
- ScoringFactory (Strategy), CVParserAdapter (Adapter)
- EventBus (ESB/Observer)
- RedisCacheManager (Redis Onbellek)
"""

from app.infrastructure.database.db_manager import db_manager
from app.infrastructure.database.repositories.user_repository import UserRepository
from app.infrastructure.database.repositories.job_repository import JobRepository
from app.infrastructure.database.repositories.application_repository import ApplicationRepository
from app.infrastructure.database.repositories.match_score_repository import MatchScoreRepository
from app.infrastructure.database.repositories.invitation_repository import InvitationRepository
from app.infrastructure.database.repositories.audit_log_repository import AuditLogRepository
from app.infrastructure.adapters.cv_parser_adapter import CVParserAdapter
from app.infrastructure.scoring.scoring_factory import ScoringFactory
from app.infrastructure.event_bus.in_memory_event_bus import InMemoryEventBus
from app.infrastructure.cache.redis_cache import cache_manager
from app.infrastructure.config import settings

from app.application.commands.register_user import RegisterUserCommand, RegisterUserHandler
from app.application.commands.create_job import CreateJobCommand, CreateJobHandler
from app.application.commands.upload_cv import UploadCVCommand, UploadCVHandler
from app.application.queries.queries import (
    GetJobsQuery, GetJobsHandler,
    GetMyApplicationsQuery, GetMyApplicationsHandler,
    GetJobCandidatesQuery, GetJobCandidatesHandler,
    GetReportQuery, GetReportHandler,
)


class RecruitmentFacade:
    """
    Facade: Ise alim sisteminin tum islemlerini tek arayuzden sunar.

    Istemci kodu (route handler'lar) bu facade uzerinden calisir.
    Arkadaki karmasik bagimliliklar gizlenir.
    """

    def __init__(self):
        self._event_bus = InMemoryEventBus()
        self._cv_parser = CVParserAdapter()
        self._scoring = ScoringFactory.create(settings.SCORING_STRATEGY)
        self._cache = cache_manager

    def _get_session(self):
        return db_manager.get_session()

    # ═══════ COMMANDS (Yazma) ═══════

    def register_user(self, full_name, email, password, role="candidate", bootstrap_code=""):
        session = self._get_session()
        try:
            handler = RegisterUserHandler(UserRepository(session), self._event_bus)
            cmd = RegisterUserCommand(full_name, email, password, role, bootstrap_code)
            return handler.handle(cmd)
        finally:
            session.close()

    def create_job(self, title, description="", min_years_experience=0, required_skills=None):
        session = self._get_session()
        try:
            handler = CreateJobHandler(JobRepository(session), self._event_bus)
            cmd = CreateJobCommand(title, description, min_years_experience, required_skills or [])
            result = handler.handle(cmd)
            # Yeni ilan olusturulunca ilan cache'ini invalidate et
            self._cache.invalidate_prefix("jobs:")
            return result
        finally:
            session.close()

    def upload_cv(self, candidate_id, job_posting_id, file_bytes, filename, auth_user_id, auth_role):
        session = self._get_session()
        try:
            handler = UploadCVHandler(
                UserRepository(session),
                JobRepository(session),
                ApplicationRepository(session),
                self._cv_parser,
                self._scoring,
                self._event_bus,
            )
            cmd = UploadCVCommand(
                candidate_id, job_posting_id, file_bytes, filename, auth_user_id, auth_role
            )
            result = handler.handle(cmd)
            # Basvuru sonrasi ilgili cache'leri invalidate et
            self._cache.invalidate_prefix(f"candidates:{job_posting_id}:")
            self._cache.invalidate_prefix(f"reports:{job_posting_id}:")
            self._cache.delete("reports:overview")
            return result
        finally:
            session.close()

    # ═══════ QUERIES (Okuma) ═══════

    def list_jobs(self):
        # Redis onbellek kontrolu
        cached = self._cache.get("jobs:list")
        if cached is not None:
            return cached

        session = self._get_session()
        try:
            handler = GetJobsHandler(JobRepository(session))
            result = handler.handle(GetJobsQuery())
            self._cache.set("jobs:list", result)
            return result
        finally:
            session.close()

    def list_my_applications(self, candidate_id):
        session = self._get_session()
        try:
            handler = GetMyApplicationsHandler(
                ApplicationRepository(session), InvitationRepository(session)
            )
            return handler.handle(GetMyApplicationsQuery(candidate_id))
        finally:
            session.close()

    def list_job_candidates(self, job_posting_id, min_score=None):
        session = self._get_session()
        try:
            handler = GetJobCandidatesHandler(
                JobRepository(session), ApplicationRepository(session), InvitationRepository(session)
            )
            return handler.handle(GetJobCandidatesQuery(job_posting_id, min_score))
        finally:
            session.close()

    def get_job_report(self, job_posting_id):
        cache_key = f"reports:{job_posting_id}:summary"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        session = self._get_session()
        try:
            handler = GetReportHandler(
                JobRepository(session), ApplicationRepository(session),
                MatchScoreRepository(session), InvitationRepository(session),
                UserRepository(session),
            )
            result = handler.handle_job_report(job_posting_id)
            if "error" not in result:
                self._cache.set(cache_key, result, ttl=120)
            return result
        finally:
            session.close()

    def get_overview_report(self):
        cached = self._cache.get("reports:overview")
        if cached is not None:
            return cached

        session = self._get_session()
        try:
            handler = GetReportHandler(
                JobRepository(session), ApplicationRepository(session),
                MatchScoreRepository(session), InvitationRepository(session),
                UserRepository(session),
            )
            result = handler.handle_overview()
            self._cache.set("reports:overview", result, ttl=120)
            return result
        finally:
            session.close()
