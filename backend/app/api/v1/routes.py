from flask import Blueprint, jsonify, request
from sqlalchemy import desc, func
from sqlalchemy.orm import Session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from app.api.v1.schemas import parse_candidate, parse_job
from app.core.auth import create_access_token, create_refresh_token, decode_token, require_roles
from app.core.config import settings
from app.core.db import SessionLocal
from app.models.entities import (
    Application,
    AuditLog,
    Invitation,
    InvitationStatus,
    InvitationType,
    JobPosting,
    MatchScore,
    User,
    UserRole,
)
from app.services.cv_parser import CVParserService
from app.services.scoring import ScoringService

v1_bp = Blueprint("v1", __name__)
scoring_service = ScoringService()
cv_parser_service = CVParserService()


def _json_error(message: str, status: int = 400):
    return jsonify({"error": message}), status


def _get_session() -> Session:
    return SessionLocal()


@v1_bp.post("/auth/register")
def register_user():
    payload = request.get_json(silent=True) or {}

    full_name = (payload.get("full_name") or "").strip()
    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password") or ""
    role_raw = (payload.get("role") or "candidate").strip().lower()
    bootstrap_code = (payload.get("bootstrap_code") or "").strip()

    if len(full_name) < 2:
        return _json_error("full_name en az 2 karakter olmalidir")
    if "@" not in email:
        return _json_error("gecerli bir email girilmelidir")
    if not isinstance(password, str) or len(password) < 8:
        return _json_error("password en az 8 karakter olmalidir")

    try:
        role = UserRole(role_raw)
    except ValueError:
        return _json_error("role degeri candidate/hr/admin olmali")

    if role in {UserRole.HR, UserRole.ADMIN} and bootstrap_code != settings.ADMIN_BOOTSTRAP_CODE:
        return _json_error("hr/admin kaydi icin bootstrap code gecersiz", status=403)

    session = _get_session()
    try:
        existing = session.query(User).filter(User.email == email).first()
        if existing is not None:
            return _json_error("bu email zaten kayitli", status=409)

        user = User(
            full_name=full_name,
            email=email,
            password_hash=generate_password_hash(password),
            role=role,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        return jsonify(
            {
                "id": user.id,
                "full_name": user.full_name,
                "email": user.email,
                "role": user.role.value,
            }
        ), 201
    finally:
        session.close()


@v1_bp.post("/auth/token")
def issue_token():
    payload = request.get_json(silent=True) or {}
    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password") or ""
    if "@" not in email:
        return _json_error("gecerli bir email girilmelidir")
    if not isinstance(password, str) or len(password) < 8:
        return _json_error("password en az 8 karakter olmalidir")

    session = _get_session()
    try:
        user = session.query(User).filter(User.email == email).first()
        if user is None:
            return _json_error("kullanici bulunamadi", status=404)
        if not user.password_hash or not check_password_hash(user.password_hash, password):
            return _json_error("email veya password hatali", status=401)

        access_token = create_access_token(user.id, user.role, user.email)
        refresh_token = create_refresh_token(user.id, user.role, user.email)
        return jsonify(
            {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "role": user.role.value,
                },
            }
        )
    finally:
        session.close()


@v1_bp.post("/auth/refresh")
def refresh_access_token():
    payload = request.get_json(silent=True) or {}
    refresh_token = (payload.get("refresh_token") or "").strip()
    if not refresh_token:
        return _json_error("refresh_token zorunludur")

    try:
        token_payload = decode_token(refresh_token, settings.REFRESH_TOKEN_MAX_AGE_SECONDS)
    except Exception:
        return _json_error("refresh token gecersiz", status=401)

    if token_payload.get("token_type") != "refresh":
        return _json_error("refresh token bekleniyor", status=401)

    try:
        role = UserRole(token_payload["role"])
    except ValueError:
        return _json_error("refresh token gecersiz", status=401)

    access_token = create_access_token(token_payload["user_id"], role, token_payload["email"])
    return jsonify({"access_token": access_token, "token_type": "bearer"})


@v1_bp.post("/candidates")
def create_candidate():
    payload = request.get_json(silent=True) or {}

    full_name = (payload.get("full_name") or "").strip()
    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password") or ""

    if len(full_name) < 2:
        return _json_error("full_name en az 2 karakter olmalidir")
    if "@" not in email:
        return _json_error("gecerli bir email girilmelidir")
    if not isinstance(password, str) or len(password) < 8:
        return _json_error("password en az 8 karakter olmalidir")

    session = _get_session()
    try:
        if session.query(User).filter(User.email == email).first() is not None:
            return _json_error("bu email ile aday zaten kayitli", status=409)

        user = User(
            full_name=full_name,
            email=email,
            password_hash=generate_password_hash(password),
            role=UserRole.CANDIDATE,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        return jsonify(
            {
                "id": user.id,
                "full_name": user.full_name,
                "email": user.email,
                "role": user.role.value,
            }
        ), 201
    finally:
        session.close()


@v1_bp.post("/jobs")
@require_roles(UserRole.HR, UserRole.ADMIN)
def create_job_posting():
    payload = request.get_json(silent=True) or {}

    title = (payload.get("title") or "").strip()
    description = (payload.get("description") or "").strip()
    min_years_experience = payload.get("min_years_experience", 0)
    required_skills = payload.get("required_skills", [])

    if len(title) < 2:
        return _json_error("title en az 2 karakter olmalidir")
    if not isinstance(min_years_experience, int) or min_years_experience < 0:
        return _json_error("min_years_experience 0 veya daha buyuk olmalidir")
    if not isinstance(required_skills, list) or not all(isinstance(x, str) for x in required_skills):
        return _json_error("required_skills metin listesi olmalidir")

    session = _get_session()
    try:
        job = JobPosting(
            title=title,
            description=description,
            min_years_experience=min_years_experience,
            required_skills=",".join([s.strip().lower() for s in required_skills if s.strip()]),
        )
        session.add(job)
        session.commit()
        session.refresh(job)

        return jsonify(
            {
                "id": job.id,
                "title": job.title,
                "min_years_experience": job.min_years_experience,
                "required_skills": required_skills,
            }
        ), 201
    finally:
        session.close()


@v1_bp.get("/jobs")
@require_roles(UserRole.CANDIDATE, UserRole.HR, UserRole.ADMIN)
def list_jobs():
    session = _get_session()
    try:
        jobs = (
            session.query(JobPosting)
            .order_by(desc(JobPosting.created_at), desc(JobPosting.id))
            .all()
        )

        return jsonify(
            {
                "count": len(jobs),
                "jobs": [
                    {
                        "id": job.id,
                        "title": job.title,
                        "description": job.description,
                        "min_years_experience": job.min_years_experience,
                        "required_skills": [
                            skill.strip()
                            for skill in job.required_skills.split(",")
                            if skill.strip()
                        ],
                    }
                    for job in jobs
                ],
            }
        )
    finally:
        session.close()


@v1_bp.post("/applications/upload")
@require_roles(UserRole.CANDIDATE, UserRole.ADMIN)
def upload_application_cv():
    form = request.form

    candidate_id = form.get("candidate_id", type=int)
    job_posting_id = form.get("job_posting_id", type=int)
    cv_file = request.files.get("cv_file")

    if not candidate_id or not job_posting_id:
        return _json_error("candidate_id ve job_posting_id zorunludur")
    if cv_file is None or not cv_file.filename:
        return _json_error("cv_file zorunludur")

    safe_name = secure_filename(cv_file.filename)
    if not safe_name.lower().endswith(".pdf"):
        return _json_error("yalnizca PDF dosya kabul edilir")

    file_bytes = cv_file.read()
    parsed = cv_parser_service.parse_bytes(file_bytes)

    session = _get_session()
    try:
        auth_user_id = int(request.auth.get("user_id"))
        auth_role = request.auth.get("role")

        if auth_role == UserRole.CANDIDATE.value and auth_user_id != candidate_id:
            return _json_error("aday yalnizca kendi basvurusunu yukleyebilir", status=403)

        candidate = session.get(User, candidate_id)
        if candidate is None or candidate.role != UserRole.CANDIDATE:
            return _json_error("aday bulunamadi", status=404)

        job = session.get(JobPosting, job_posting_id)
        if job is None:
            return _json_error("ilan bulunamadi", status=404)

        storage_path = cv_parser_service.save_cv(file_bytes, safe_name)

        application = Application(
            candidate_id=candidate_id,
            job_posting_id=job_posting_id,
            cv_path=storage_path,
            parsed_summary=parsed["summary"],
        )
        session.add(application)
        session.commit()
        session.refresh(application)

        candidate_payload = {
            "name": candidate.full_name,
            "years_experience": parsed["years_experience"],
            "skills": parsed["skills"],
            "education_level": "lisans",
        }
        job_skills = [s.strip() for s in job.required_skills.split(",") if s.strip()]
        job_payload = {
            "title": job.title,
            "min_years_experience": job.min_years_experience,
            "required_skills": job_skills,
        }

        candidate_obj, candidate_errors = parse_candidate(candidate_payload)
        job_obj, job_errors = parse_job(job_payload)

        score = 0.0
        reasons = ["Skorlama icin veri dogrulanamadi"]
        if not (candidate_errors or job_errors):
            score, reasons = scoring_service.calculate(candidate_obj, job_obj)

        match_score = MatchScore(
            application_id=application.id,
            score=score,
            rationale=" | ".join(reasons),
        )
        session.add(match_score)

        invitation_created = False
        if score >= settings.AUTO_INVITE_SCORE_THRESHOLD:
            invitation = Invitation(
                application_id=application.id,
                invitation_type=InvitationType.TEST,
                status=InvitationStatus.SENT,
            )
            session.add(invitation)
            invitation_created = True

        session.commit()

        return jsonify(
            {
                "application_id": application.id,
                "candidate_id": application.candidate_id,
                "job_posting_id": application.job_posting_id,
                "cv_path": application.cv_path,
                "parsed_summary": application.parsed_summary,
                "extracted_skills": parsed["skills"],
                "estimated_years_experience": parsed["years_experience"],
                "match_score": score,
                "score_reasons": reasons,
                "auto_invite_threshold": settings.AUTO_INVITE_SCORE_THRESHOLD,
                "invitation_created": invitation_created,
                "storage_dir": settings.CV_STORAGE_DIR,
            }
        ), 201
    finally:
        session.close()


@v1_bp.get("/applications/me")
@require_roles(UserRole.CANDIDATE, UserRole.ADMIN)
def list_my_applications():
    session = _get_session()
    try:
        auth_user_id = int(request.auth.get("user_id"))
        rows = (
            session.query(Application, JobPosting, MatchScore)
            .join(JobPosting, JobPosting.id == Application.job_posting_id)
            .outerjoin(MatchScore, MatchScore.application_id == Application.id)
            .filter(Application.candidate_id == auth_user_id)
            .order_by(desc(Application.created_at))
            .all()
        )

        applications = []
        for application, job, match_score in rows:
            invitation = (
                session.query(Invitation)
                .filter(Invitation.application_id == application.id)
                .order_by(desc(Invitation.created_at))
                .first()
            )

            applications.append(
                {
                    "application_id": application.id,
                    "job_posting_id": job.id,
                    "job_title": job.title,
                    "status": application.status.value,
                    "parsed_summary": application.parsed_summary,
                    "match_score": None if match_score is None else float(match_score.score),
                    "invitation": None
                    if invitation is None
                    else {
                        "type": invitation.invitation_type.value,
                        "status": invitation.status.value,
                    },
                }
            )

        return jsonify({"count": len(applications), "applications": applications})
    finally:
        session.close()


@v1_bp.get("/jobs/<int:job_posting_id>/candidates")
@require_roles(UserRole.HR, UserRole.ADMIN)
def list_job_candidates(job_posting_id: int):
    min_score = request.args.get("min_score", default=None, type=float)

    session = _get_session()
    try:
        job = session.get(JobPosting, job_posting_id)
        if job is None:
            return _json_error("ilan bulunamadi", status=404)

        rows = (
            session.query(Application, User, MatchScore)
            .join(User, User.id == Application.candidate_id)
            .join(MatchScore, MatchScore.application_id == Application.id)
            .filter(Application.job_posting_id == job_posting_id)
            .order_by(desc(MatchScore.score), desc(Application.created_at))
            .all()
        )

        results = []
        for application, user, match_score in rows:
            score = float(match_score.score)
            if min_score is not None and score < min_score:
                continue

            invitation = (
                session.query(Invitation)
                .filter(Invitation.application_id == application.id)
                .order_by(desc(Invitation.created_at))
                .first()
            )

            results.append(
                {
                    "application_id": application.id,
                    "candidate": {
                        "id": user.id,
                        "full_name": user.full_name,
                        "email": user.email,
                    },
                    "match_score": score,
                    "status": application.status.value,
                    "invitation": None
                    if invitation is None
                    else {
                        "id": invitation.id,
                        "type": invitation.invitation_type.value,
                        "status": invitation.status.value,
                    },
                }
            )

        return jsonify(
            {
                "job_posting_id": job.id,
                "job_title": job.title,
                "candidate_count": len(results),
                "candidates": results,
            }
        )
    finally:
        session.close()


@v1_bp.get("/jobs/<int:job_posting_id>/shortlisted")
@require_roles(UserRole.HR, UserRole.ADMIN)
def list_shortlisted_candidates(job_posting_id: int):
    threshold = request.args.get(
        "threshold", default=settings.AUTO_INVITE_SCORE_THRESHOLD, type=float
    )
    return list_job_candidates_with_threshold(job_posting_id, threshold)


def list_job_candidates_with_threshold(job_posting_id: int, threshold: float):
    session = _get_session()
    try:
        job = session.get(JobPosting, job_posting_id)
        if job is None:
            return _json_error("ilan bulunamadi", status=404)

        rows = (
            session.query(Application, User, MatchScore)
            .join(User, User.id == Application.candidate_id)
            .join(MatchScore, MatchScore.application_id == Application.id)
            .filter(Application.job_posting_id == job_posting_id)
            .filter(MatchScore.score >= threshold)
            .order_by(desc(MatchScore.score), desc(Application.created_at))
            .all()
        )

        candidates = []
        for application, user, match_score in rows:
            candidates.append(
                {
                    "application_id": application.id,
                    "candidate_id": user.id,
                    "candidate_name": user.full_name,
                    "score": float(match_score.score),
                }
            )

        return jsonify(
            {
                "job_posting_id": job.id,
                "threshold": threshold,
                "shortlisted_count": len(candidates),
                "candidates": candidates,
            }
        )
    finally:
        session.close()


@v1_bp.get("/invitations")
@require_roles(UserRole.HR, UserRole.ADMIN)
def list_invitations():
    status_filter = request.args.get("status", default=None, type=str)
    job_posting_id = request.args.get("job_posting_id", default=None, type=int)

    session = _get_session()
    try:
        query = (
            session.query(Invitation, Application, User, JobPosting)
            .join(Application, Application.id == Invitation.application_id)
            .join(User, User.id == Application.candidate_id)
            .join(JobPosting, JobPosting.id == Application.job_posting_id)
        )

        if status_filter:
            query = query.filter(Invitation.status == InvitationStatus(status_filter))
        if job_posting_id:
            query = query.filter(JobPosting.id == job_posting_id)

        rows = query.order_by(desc(Invitation.created_at)).all()

        invitations = []
        for invitation, application, user, job in rows:
            invitations.append(
                {
                    "invitation_id": invitation.id,
                    "application_id": application.id,
                    "candidate_name": user.full_name,
                    "candidate_email": user.email,
                    "job_posting_id": job.id,
                    "job_title": job.title,
                    "type": invitation.invitation_type.value,
                    "status": invitation.status.value,
                }
            )

        return jsonify({"count": len(invitations), "invitations": invitations})
    except ValueError:
        return _json_error("gecersiz invitation status filtresi")
    finally:
        session.close()


@v1_bp.get("/audit-logs")
@require_roles(UserRole.ADMIN)
def list_audit_logs():
    limit = request.args.get("limit", default=50, type=int)
    path_filter = request.args.get("path", default=None, type=str)
    method_filter = request.args.get("method", default=None, type=str)

    session = _get_session()
    try:
        query = session.query(AuditLog)

        if path_filter:
            query = query.filter(AuditLog.path.contains(path_filter))
        if method_filter:
            query = query.filter(AuditLog.method == method_filter.upper())

        logs = query.order_by(desc(AuditLog.created_at)).limit(max(1, min(limit, 200))).all()

        return jsonify(
            {
                "count": len(logs),
                "logs": [
                    {
                        "id": log.id,
                        "user_id": log.user_id,
                        "actor_type": log.actor_type.value,
                        "role": log.role,
                        "method": log.method,
                        "path": log.path,
                        "status_code": log.status_code,
                        "ip_address": log.ip_address,
                    }
                    for log in logs
                ],
            }
        )
    finally:
        session.close()


@v1_bp.get("/reports/jobs/<int:job_posting_id>/summary")
@require_roles(UserRole.HR, UserRole.ADMIN)
def job_report_summary(job_posting_id: int):
    session = _get_session()
    try:
        job = session.get(JobPosting, job_posting_id)
        if job is None:
            return _json_error("ilan bulunamadi", status=404)

        application_count = (
            session.query(func.count(Application.id))
            .filter(Application.job_posting_id == job_posting_id)
            .scalar()
            or 0
        )

        score_row = (
            session.query(
                func.count(MatchScore.id),
                func.avg(MatchScore.score),
                func.max(MatchScore.score),
                func.min(MatchScore.score),
            )
            .join(Application, Application.id == MatchScore.application_id)
            .filter(Application.job_posting_id == job_posting_id)
            .first()
        )

        invitation_count = (
            session.query(func.count(Invitation.id))
            .join(Application, Application.id == Invitation.application_id)
            .filter(Application.job_posting_id == job_posting_id)
            .scalar()
            or 0
        )

        scored_count = int(score_row[0] or 0)
        avg_score = round(float(score_row[1]), 2) if score_row[1] is not None else 0.0
        max_score = round(float(score_row[2]), 2) if score_row[2] is not None else 0.0
        min_score = round(float(score_row[3]), 2) if score_row[3] is not None else 0.0

        invitation_rate = (
            round((invitation_count / application_count) * 100, 2)
            if application_count > 0
            else 0.0
        )

        return jsonify(
            {
                "job_posting_id": job.id,
                "job_title": job.title,
                "applications_count": int(application_count),
                "scored_count": scored_count,
                "avg_score": avg_score,
                "max_score": max_score,
                "min_score": min_score,
                "invitation_count": int(invitation_count),
                "invitation_rate_percent": invitation_rate,
            }
        )
    finally:
        session.close()


@v1_bp.get("/reports/overview")
@require_roles(UserRole.HR, UserRole.ADMIN)
def overview_report():
    session = _get_session()
    try:
        total_jobs = session.query(func.count(JobPosting.id)).scalar() or 0
        total_candidates = (
            session.query(func.count(User.id)).filter(User.role == UserRole.CANDIDATE).scalar() or 0
        )
        total_applications = session.query(func.count(Application.id)).scalar() or 0
        total_invitations = session.query(func.count(Invitation.id)).scalar() or 0
        avg_score_all = session.query(func.avg(MatchScore.score)).scalar()

        return jsonify(
            {
                "total_jobs": int(total_jobs),
                "total_candidates": int(total_candidates),
                "total_applications": int(total_applications),
                "total_invitations": int(total_invitations),
                "avg_score_all": round(float(avg_score_all), 2) if avg_score_all is not None else 0.0,
            }
        )
    finally:
        session.close()


@v1_bp.post("/match")
def match_candidate_to_job():
    payload = request.get_json(silent=True) or {}
    candidate_payload = payload.get("candidate", {})
    job_payload = payload.get("job", {})

    candidate, candidate_errors = parse_candidate(candidate_payload)
    job, job_errors = parse_job(job_payload)

    errors = candidate_errors + job_errors
    if errors:
        return jsonify({"errors": errors}), 400

    score, reasons = scoring_service.calculate(candidate, job)
    return jsonify({"score": score, "reasons": reasons})
