"""
Data Transfer Objects — OOP: Encapsulation
============================================
Domain entity'lerini doğrudan API'ye expose etmek yerine
DTO'lar üzerinden veri transferi sağlanır.
Encapsulation: İç yapı saklanır, dışarıya sadece gerekli veri sunulur.
"""

from dataclasses import dataclass, field
from typing import Optional, List


# ──────── User DTOs ────────

@dataclass
class UserDTO:
    """Kullanıcı bilgisi DTO."""
    id: int
    full_name: str
    email: str
    role: str


@dataclass
class RegisterUserDTO:
    """Kullanıcı kayıt istemi DTO."""
    full_name: str
    email: str
    password: str
    role: str = "candidate"
    bootstrap_code: str = ""


@dataclass
class TokenDTO:
    """Token yanıtı DTO."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: Optional[UserDTO] = None


# ──────── Job DTOs ────────

@dataclass
class JobDTO:
    """İş ilanı DTO."""
    id: int
    title: str
    description: str
    min_years_experience: int
    required_skills: List[str]


@dataclass
class CreateJobDTO:
    """İş ilanı oluşturma istemi DTO."""
    title: str
    description: str = ""
    min_years_experience: int = 0
    required_skills: List[str] = field(default_factory=list)


# ──────── Application DTOs ────────

@dataclass
class ApplicationDTO:
    """Başvuru DTO."""
    application_id: int
    candidate_id: int
    job_posting_id: int
    cv_path: str
    parsed_summary: str
    status: str
    match_score: Optional[float] = None
    invitation: Optional[dict] = None


@dataclass
class UploadResultDTO:
    """CV yükleme sonucu DTO."""
    application_id: int
    candidate_id: int
    job_posting_id: int
    cv_path: str
    parsed_summary: str
    extracted_skills: List[str]
    estimated_years_experience: int
    match_score: float
    score_reasons: List[str]
    auto_invite_threshold: float
    invitation_created: bool


# ──────── Report DTOs ────────

@dataclass
class JobReportDTO:
    """İlan raporu DTO."""
    job_posting_id: int
    job_title: str
    applications_count: int
    scored_count: int
    avg_score: float
    max_score: float
    min_score: float
    invitation_count: int
    invitation_rate_percent: float


@dataclass
class OverviewReportDTO:
    """Genel bakış raporu DTO."""
    total_jobs: int
    total_candidates: int
    total_applications: int
    total_invitations: int
    avg_score_all: float
