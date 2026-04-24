from dataclasses import dataclass


@dataclass
class CandidateProfile:
    name: str
    years_experience: int
    skills: list[str]
    education_level: str


@dataclass
class JobPosting:
    title: str
    min_years_experience: int
    required_skills: list[str]


def parse_candidate(payload: dict) -> tuple[CandidateProfile | None, list[str]]:
    errors = []

    name = payload.get("name", "")
    years_experience = payload.get("years_experience", 0)
    skills = payload.get("skills", [])
    education_level = payload.get("education_level", "lisans")

    if not isinstance(name, str) or len(name.strip()) < 2:
        errors.append("Aday adi en az 2 karakter olmalidir")
    if not isinstance(years_experience, int) or years_experience < 0 or years_experience > 50:
        errors.append("Aday deneyim yili 0 ile 50 arasinda olmalidir")
    if not isinstance(skills, list) or not all(isinstance(x, str) for x in skills):
        errors.append("Aday yetenekleri metin listesi olmalidir")
    if not isinstance(education_level, str):
        errors.append("Egitim seviyesi metin olmalidir")

    if errors:
        return None, errors

    return (
        CandidateProfile(
            name=name.strip(),
            years_experience=years_experience,
            skills=skills,
            education_level=education_level.strip() or "lisans",
        ),
        [],
    )


def parse_job(payload: dict) -> tuple[JobPosting | None, list[str]]:
    errors = []

    title = payload.get("title", "")
    min_years_experience = payload.get("min_years_experience", 0)
    required_skills = payload.get("required_skills", [])

    if not isinstance(title, str) or len(title.strip()) < 2:
        errors.append("Ilan basligi en az 2 karakter olmalidir")
    if (
        not isinstance(min_years_experience, int)
        or min_years_experience < 0
        or min_years_experience > 30
    ):
        errors.append("Ilan minimum deneyim 0 ile 30 arasinda olmalidir")
    if not isinstance(required_skills, list) or not all(isinstance(x, str) for x in required_skills):
        errors.append("Ilan yetenekleri metin listesi olmalidir")

    if errors:
        return None, errors

    return (
        JobPosting(
            title=title.strip(),
            min_years_experience=min_years_experience,
            required_skills=required_skills,
        ),
        [],
    )
