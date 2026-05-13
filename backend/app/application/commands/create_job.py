"""
CreateJobCommand — CQRS: Command (Yazma İşlemi)
==================================================
İş ilanı oluşturma işlemini yöneten command ve handler.
"""

from dataclasses import dataclass, field
from typing import List, Tuple

from app.core.entities.job_posting import JobPosting
from app.application.dtos.dtos import JobDTO


@dataclass
class CreateJobCommand:
    """İş ilanı oluşturma komutu."""
    title: str
    description: str = ""
    min_years_experience: int = 0
    required_skills: List[str] = field(default_factory=list)


class CreateJobHandler:
    """CQRS Command Handler — İş ilanı oluşturma."""

    def __init__(self, job_repository, event_bus=None):
        self._job_repo = job_repository
        self._event_bus = event_bus

    def handle(self, command: CreateJobCommand) -> Tuple[JobDTO | None, str | None]:
        """
        İş ilanı oluştur.

        Returns:
            Tuple[JobDTO | None, str | None]: (sonuç, hata_mesajı)
        """
        title = command.title.strip()
        if len(title) < 2:
            return None, "title en az 2 karakter olmalidir"
        if not isinstance(command.min_years_experience, int) or command.min_years_experience < 0:
            return None, "min_years_experience 0 veya daha buyuk olmalidir"
        if not isinstance(command.required_skills, list) or not all(
            isinstance(x, str) for x in command.required_skills
        ):
            return None, "required_skills metin listesi olmalidir"

        skills_csv = ",".join([s.strip().lower() for s in command.required_skills if s.strip()])

        job = JobPosting(
            title=title,
            description=command.description.strip(),
            min_years_experience=command.min_years_experience,
            required_skills=skills_csv,
        )
        self._job_repo.add(job)
        self._job_repo.commit()
        self._job_repo.refresh(job)

        # Event yayınla (Observer + ESB)
        if self._event_bus:
            self._event_bus.publish("job.created", {
                "job_id": job.id,
                "title": job.title,
            })

        return JobDTO(
            id=job.id,
            title=job.title,
            description=job.description,
            min_years_experience=job.min_years_experience,
            required_skills=command.required_skills,
        ), None
