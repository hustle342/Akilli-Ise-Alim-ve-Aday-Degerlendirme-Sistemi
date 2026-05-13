"""
Value Objects — Domain Layer
==============================
Kimliğe sahip olmayan, değeri ile tanımlanan objeler.
Encapsulation prensibi ile veri bütünlüğü korunur.
"""

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class CandidateProfile:
    """Aday profili value object'i."""
    name: str
    years_experience: int
    skills: List[str]
    education_level: str


@dataclass(frozen=True)
class JobRequirements:
    """İlan gereksinimleri value object'i."""
    title: str
    min_years_experience: int
    required_skills: List[str]


@dataclass(frozen=True)
class ScoreResult:
    """Skor sonucu value object'i."""
    score: float
    reasons: List[str]
    version: str
