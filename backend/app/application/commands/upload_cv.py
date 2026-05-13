"""
UploadCVCommand — CQRS: Command (Yazma İşlemi)
=================================================
CV yükleme, parse etme ve skorlama işlemlerini yöneten command ve handler.
Bu handler en karmaşık iş akışını içerir: parse → skor → otomatik davet.
"""

from dataclasses import dataclass
from typing import Tuple

from app.core.entities.application import Application
from app.core.entities.match_score import MatchScore
from app.core.entities.invitation import Invitation
from app.core.enums import InvitationStatus, InvitationType, UserRole
from app.core.value_objects import CandidateProfile, JobRequirements
from app.application.dtos.dtos import UploadResultDTO
from app.infrastructure.config import settings


@dataclass
class UploadCVCommand:
    """CV yükleme komutu."""
    candidate_id: int
    job_posting_id: int
    file_bytes: bytes
    filename: str
    auth_user_id: int
    auth_role: str


class UploadCVHandler:
    """CQRS Command Handler — CV yükleme + parse + skorlama."""

    def __init__(
        self,
        user_repository,
        job_repository,
        application_repository,
        cv_parser,
        scoring_strategy,
        event_bus=None,
    ):
        self._user_repo = user_repository
        self._job_repo = job_repository
        self._app_repo = application_repository
        self._cv_parser = cv_parser
        self._scoring = scoring_strategy
        self._event_bus = event_bus

    def handle(self, command: UploadCVCommand) -> Tuple[UploadResultDTO | None, str | None, int]:
        """
        CV yükleme akışını gerçekleştir.

        Returns:
            Tuple[UploadResultDTO | None, str | None, int]: (sonuç, hata, http_status)
        """
        # Yetki kontrolü
        if command.auth_role == UserRole.CANDIDATE.value and command.auth_user_id != command.candidate_id:
            return None, "aday yalnizca kendi basvurusunu yukleyebilir", 403

        # Entity kontrolleri
        candidate = self._user_repo.get_by_id(command.candidate_id)
        if candidate is None or candidate.role != UserRole.CANDIDATE:
            return None, "aday bulunamadi", 404

        job = self._job_repo.get_by_id(command.job_posting_id)
        if job is None:
            return None, "ilan bulunamadi", 404

        # CV parse et
        parsed = self._cv_parser.parse_bytes(command.file_bytes)

        # CV dosyasını kaydet
        storage_path = self._cv_parser.save_cv(command.file_bytes, command.filename)

        # Başvuru oluştur
        application = Application(
            candidate_id=command.candidate_id,
            job_posting_id=command.job_posting_id,
            cv_path=storage_path,
            parsed_summary=parsed["summary"],
        )
        self._app_repo.add(application)
        self._app_repo.commit()
        self._app_repo.refresh(application)

        # Event yayınla: Başvuru oluşturuldu
        if self._event_bus:
            self._event_bus.publish("application.created", {
                "application_id": application.id,
                "candidate_id": command.candidate_id,
                "job_posting_id": command.job_posting_id,
            })

        # Skor hesapla (Strategy Pattern)
        candidate_profile = CandidateProfile(
            name=candidate.full_name,
            years_experience=parsed["years_experience"],
            skills=parsed["skills"],
            education_level="lisans",
        )
        job_skills = [s.strip() for s in job.required_skills.split(",") if s.strip()]
        job_requirements = JobRequirements(
            title=job.title,
            min_years_experience=job.min_years_experience,
            required_skills=job_skills,
        )

        score = 0.0
        reasons = ["Skorlama icin veri dogrulanamadi"]
        try:
            score, reasons = self._scoring.calculate(candidate_profile, job_requirements)
        except Exception:
            pass

        # Skor kaydet
        match_score = MatchScore(
            application_id=application.id,
            score=score,
            scoring_version=self._scoring.get_version(),
            rationale=" | ".join(reasons),
        )
        self._app_repo.add(match_score)

        # Event yayınla: Skor hesaplandı
        if self._event_bus:
            self._event_bus.publish("score.calculated", {
                "application_id": application.id,
                "score": score,
                "version": self._scoring.get_version(),
            })

        # Otomatik davet kontrolü
        invitation_created = False
        if score >= settings.AUTO_INVITE_SCORE_THRESHOLD:
            invitation = Invitation(
                application_id=application.id,
                invitation_type=InvitationType.TEST,
                status=InvitationStatus.SENT,
            )
            self._app_repo.add(invitation)
            invitation_created = True

            # Event yayınla: Davet gönderildi
            if self._event_bus:
                self._event_bus.publish("invitation.sent", {
                    "application_id": application.id,
                    "invitation_type": "test",
                })

        self._app_repo.commit()

        return UploadResultDTO(
            application_id=application.id,
            candidate_id=application.candidate_id,
            job_posting_id=application.job_posting_id,
            cv_path=application.cv_path,
            parsed_summary=application.parsed_summary,
            extracted_skills=parsed["skills"],
            estimated_years_experience=parsed["years_experience"],
            match_score=score,
            score_reasons=reasons,
            auto_invite_threshold=settings.AUTO_INVITE_SCORE_THRESHOLD,
            invitation_created=invitation_created,
        ), None, 201
