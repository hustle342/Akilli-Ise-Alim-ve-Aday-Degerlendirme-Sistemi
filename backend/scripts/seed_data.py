"""
Demo seed data script.
Creates admin, 2 HR users, 5 candidates, 3 job postings and sample applications.

Usage (from project root):
  $env:PYTHONPATH='backend'; & ".venv\Scripts\python.exe" backend/scripts/seed_data.py
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from werkzeug.security import generate_password_hash

from app.core.db import SessionLocal, engine
from app.models.base import Base
from app.models.entities import (
    Application,
    ApplicationStatus,
    Invitation,
    InvitationStatus,
    InvitationType,
    JobPosting,
    MatchScore,
    User,
    UserRole,
)
from app.services.scoring import ScoringService

# ---------------------------------------------------------------------------
# Demo veri tanimlari
# ---------------------------------------------------------------------------

ADMIN = {
    "full_name": "Admin Kullanici",
    "email": "admin@demo.com",
    "password": "AdminPass123!",
    "role": UserRole.ADMIN,
}

HR_USERS = [
    {
        "full_name": "Ayse Kaya",
        "email": "ayse.hr@demo.com",
        "password": "HrPass123!",
        "role": UserRole.HR,
    },
    {
        "full_name": "Mehmet Celik",
        "email": "mehmet.hr@demo.com",
        "password": "HrPass123!",
        "role": UserRole.HR,
    },
]

CANDIDATES = [
    {
        "full_name": "Ali Yilmaz",
        "email": "ali@demo.com",
        "password": "Candidate123!",
        "role": UserRole.CANDIDATE,
        "skills": ["python", "flask", "sql", "docker"],
        "years_experience": 4,
        "summary": "Backend gelistirici, Python ve Flask konusunda deneyimli.",
    },
    {
        "full_name": "Fatma Sahin",
        "email": "fatma@demo.com",
        "password": "Candidate123!",
        "role": UserRole.CANDIDATE,
        "skills": ["java", "spring", "sql", "docker", "kubernetes"],
        "years_experience": 6,
        "summary": "Java Spring Boot ile kurumsal uygulama gelistiricisi.",
    },
    {
        "full_name": "Emre Demir",
        "email": "emre@demo.com",
        "password": "Candidate123!",
        "role": UserRole.CANDIDATE,
        "skills": ["python", "machine learning", "tensorflow", "pandas"],
        "years_experience": 3,
        "summary": "Makine ogrenimi ve veri bilimi alaninda calisan arastirmaci.",
    },
    {
        "full_name": "Zeynep Arslan",
        "email": "zeynep@demo.com",
        "password": "Candidate123!",
        "role": UserRole.CANDIDATE,
        "skills": ["flutter", "dart", "firebase", "rest api"],
        "years_experience": 2,
        "summary": "Flutter ile cross-platform mobil uygulama gelistiricisi.",
    },
    {
        "full_name": "Can Ozturk",
        "email": "can@demo.com",
        "password": "Candidate123!",
        "role": UserRole.CANDIDATE,
        "skills": ["python", "flask", "docker", "postgresql"],
        "years_experience": 1,
        "summary": "Yeni mezun Python backend gelistiricisi.",
    },
]

JOB_POSTINGS = [
    {
        "title": "Backend Python Gelistirici",
        "description": "Flask veya FastAPI ile RESTful servisler gelistirecek deneyimli backend gelistirici aranmaktadir.",
        "required_skills": ["python", "flask", "sql", "docker"],
        "min_years_experience": 3,
    },
    {
        "title": "Makine Ogrenimi Muhendisi",
        "description": "NLP ve derin ogrenme modellerini uretim ortamina tasiyacak ML muhendisi aranmaktadir.",
        "required_skills": ["python", "machine learning", "tensorflow", "pandas"],
        "min_years_experience": 2,
    },
    {
        "title": "Flutter Mobil Gelistirici",
        "description": "iOS ve Android icin Flutter uygulamalari gelistirecek mobil gelistirici aranmaktadir.",
        "required_skills": ["flutter", "dart", "firebase", "rest api"],
        "min_years_experience": 1,
    },
]

# Her aday hangi ilanlara basvurdu (candidate index, job index)
APPLICATION_PAIRS = [
    (0, 0),  # Ali -> Backend Python
    (1, 0),  # Fatma -> Backend Python
    (2, 1),  # Emre -> ML Muhendisi
    (3, 2),  # Zeynep -> Flutter
    (4, 0),  # Can -> Backend Python
    (0, 1),  # Ali -> ML Muhendisi
    (2, 0),  # Emre -> Backend Python
]

# ---------------------------------------------------------------------------
# Yardimci sinif: skorlama icin hafif sarici
# ---------------------------------------------------------------------------

class _CandidateProxy:
    def __init__(self, skills, years_experience):
        self.skills = skills
        self.years_experience = years_experience


class _JobProxy:
    def __init__(self, required_skills, min_years_experience):
        self.required_skills = required_skills
        self.min_years_experience = min_years_experience


# ---------------------------------------------------------------------------
# Ana seed fonksiyonu
# ---------------------------------------------------------------------------

def seed():
    Base.metadata.create_all(bind=engine)

    session = SessionLocal()
    scoring = ScoringService()

    try:
        # ----- Kullanicilar -----
        def _upsert_user(data: dict) -> User:
            existing = session.query(User).filter(User.email == data["email"]).first()
            if existing:
                print(f"  [skip] kullanici zaten mevcut: {data['email']}")
                return existing
            user = User(
                full_name=data["full_name"],
                email=data["email"],
                password_hash=generate_password_hash(data["password"]),
                role=data["role"],
            )
            session.add(user)
            session.flush()
            print(f"  [ok]   kullanici olusturuldu: {data['email']} ({data['role'].value})")
            return user

        print("\n--- Kullanicilar ---")
        admin_user = _upsert_user(ADMIN)
        hr_users = [_upsert_user(d) for d in HR_USERS]
        candidate_users = [_upsert_user(d) for d in CANDIDATES]

        # ----- Ilanlar -----
        print("\n--- Ilanlar ---")
        job_records = []
        for jd in JOB_POSTINGS:
            existing = session.query(JobPosting).filter(JobPosting.title == jd["title"]).first()
            if existing:
                print(f"  [skip] ilan zaten mevcut: {jd['title']}")
                job_records.append(existing)
                continue
            job = JobPosting(
                title=jd["title"],
                description=jd["description"],
                required_skills=",".join(jd["required_skills"]),
                min_years_experience=jd["min_years_experience"],
            )
            session.add(job)
            session.flush()
            print(f"  [ok]   ilan olusturuldu: {jd['title']}")
            job_records.append(job)

        # ----- Basvurular ve skorlar -----
        print("\n--- Basvurular ---")
        threshold = 70.0

        for cand_idx, job_idx in APPLICATION_PAIRS:
            cand_user = candidate_users[cand_idx]
            cand_data = CANDIDATES[cand_idx]
            job = job_records[job_idx]
            job_data = JOB_POSTINGS[job_idx]

            # Daha once basvurmus mu?
            existing_app = (
                session.query(Application)
                .filter(
                    Application.candidate_id == cand_user.id,
                    Application.job_posting_id == job.id,
                )
                .first()
            )
            if existing_app:
                print(f"  [skip] basvuru zaten mevcut: {cand_data['email']} -> {job_data['title']}")
                continue

            # Skor hesapla
            cand_proxy = _CandidateProxy(cand_data["skills"], cand_data["years_experience"])
            job_proxy = _JobProxy(job_data["required_skills"], job_data["min_years_experience"])
            score, reasons = scoring.calculate(cand_proxy, job_proxy)

            # Basvuru
            status = ApplicationStatus.SHORTLISTED if score >= threshold else ApplicationStatus.APPLIED
            app = Application(
                candidate_id=cand_user.id,
                job_posting_id=job.id,
                cv_path="storage/cv/demo_cv.pdf",
                parsed_summary=cand_data["summary"],
                status=status,
            )
            session.add(app)
            session.flush()

            # MatchScore
            match = MatchScore(
                application_id=app.id,
                score=score,
                rationale="; ".join(reasons),
            )
            session.add(match)

            # Oto-davet
            if score >= threshold:
                invitation = Invitation(
                    application_id=app.id,
                    invitation_type=InvitationType.INTERVIEW,
                    status=InvitationStatus.SENT,
                )
                session.add(invitation)
                print(
                    f"  [ok]   basvuru+skor+davet: {cand_data['email']} -> {job_data['title']} "
                    f"(skor={score})"
                )
            else:
                print(
                    f"  [ok]   basvuru+skor: {cand_data['email']} -> {job_data['title']} "
                    f"(skor={score})"
                )

        session.commit()
        print("\nSeed tamamlandi.\n")
        print("Demo giris bilgileri:")
        print("  admin@demo.com      / AdminPass123!  (admin)")
        print("  ayse.hr@demo.com    / HrPass123!     (hr)")
        print("  mehmet.hr@demo.com  / HrPass123!     (hr)")
        print("  ali@demo.com        / Candidate123!  (candidate)")
        print("  fatma@demo.com      / Candidate123!  (candidate)")
        print("  emre@demo.com       / Candidate123!  (candidate)")
        print("  zeynep@demo.com     / Candidate123!  (candidate)")
        print("  can@demo.com        / Candidate123!  (candidate)\n")

    finally:
        session.close()


if __name__ == "__main__":
    seed()
