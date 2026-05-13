"""
Report & Candidate Routes — Presentation Layer
=================================================
Rapor, aday listeleme ve davet endpoint'leri.
"""

from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash

from app.presentation.api.middleware.auth_middleware import require_roles
from app.application.services.facade import RecruitmentFacade
from app.core.enums import UserRole
from app.infrastructure.config import settings
from app.infrastructure.database.db_manager import db_manager
from app.infrastructure.database.repositories.user_repository import UserRepository
from app.infrastructure.database.repositories.invitation_repository import InvitationRepository
from app.infrastructure.database.repositories.audit_log_repository import AuditLogRepository
from app.core.entities.user import User

report_bp = Blueprint("reports", __name__)
facade = RecruitmentFacade()


def _json_error(message: str, status: int = 400):
    return jsonify({"error": message}), status


# ── Candidate CRUD ──

@report_bp.post("/candidates")
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

    session = db_manager.get_session()
    try:
        repo = UserRepository(session)
        if repo.get_by_email(email) is not None:
            return _json_error("bu email ile aday zaten kayitli", 409)

        user = User(
            full_name=full_name, email=email,
            password_hash=generate_password_hash(password),
            role=UserRole.CANDIDATE,
        )
        repo.add(user)
        repo.commit()
        repo.refresh(user)
        return jsonify({
            "id": user.id, "full_name": user.full_name,
            "email": user.email, "role": user.role.value,
        }), 201
    finally:
        session.close()


# ── Job Candidates ──

@report_bp.get("/jobs/<int:job_posting_id>/candidates")
@require_roles(UserRole.HR, UserRole.ADMIN)
def list_job_candidates(job_posting_id: int):
    min_score = request.args.get("min_score", default=None, type=float)
    result = facade.list_job_candidates(job_posting_id, min_score)
    if "error" in result:
        return _json_error(result["error"], 404)
    return jsonify(result)


@report_bp.get("/jobs/<int:job_posting_id>/shortlisted")
@require_roles(UserRole.HR, UserRole.ADMIN)
def list_shortlisted(job_posting_id: int):
    threshold = request.args.get(
        "threshold", default=settings.AUTO_INVITE_SCORE_THRESHOLD, type=float
    )
    result = facade.list_job_candidates(job_posting_id, threshold)
    if "error" in result:
        return _json_error(result["error"], 404)
    # Shortlisted icin farkli format
    candidates = [{
        "application_id": c["application_id"],
        "candidate_id": c["candidate"]["id"],
        "candidate_name": c["candidate"]["full_name"],
        "score": c["match_score"],
    } for c in result.get("candidates", [])]
    return jsonify({
        "job_posting_id": result["job_posting_id"],
        "threshold": threshold,
        "shortlisted_count": len(candidates),
        "candidates": candidates,
    })


# ── Invitations ──

@report_bp.get("/invitations")
@require_roles(UserRole.HR, UserRole.ADMIN)
def list_invitations():
    status_filter = request.args.get("status", default=None, type=str)
    job_posting_id = request.args.get("job_posting_id", default=None, type=int)

    session = db_manager.get_session()
    try:
        repo = InvitationRepository(session)
        rows = repo.get_filtered(status_filter, job_posting_id)
        invitations = [{
            "invitation_id": inv.id,
            "application_id": app.id,
            "candidate_name": user.full_name,
            "candidate_email": user.email,
            "job_posting_id": job.id,
            "job_title": job.title,
            "type": inv.invitation_type.value,
            "status": inv.status.value,
        } for inv, app, user, job in rows]
        return jsonify({"count": len(invitations), "invitations": invitations})
    except ValueError:
        return _json_error("gecersiz invitation status filtresi")
    finally:
        session.close()


# ── Reports ──

@report_bp.get("/reports/jobs/<int:job_posting_id>/summary")
@require_roles(UserRole.HR, UserRole.ADMIN)
def job_report_summary(job_posting_id: int):
    result = facade.get_job_report(job_posting_id)
    if "error" in result:
        return _json_error(result["error"], 404)
    return jsonify(result)


@report_bp.get("/reports/overview")
@require_roles(UserRole.HR, UserRole.ADMIN)
def overview_report():
    return jsonify(facade.get_overview_report())


# ── Audit Logs ──

@report_bp.get("/audit-logs")
@require_roles(UserRole.ADMIN)
def list_audit_logs():
    limit = request.args.get("limit", default=50, type=int)
    path_filter = request.args.get("path", default=None, type=str)
    method_filter = request.args.get("method", default=None, type=str)

    session = db_manager.get_session()
    try:
        repo = AuditLogRepository(session)
        logs = repo.get_filtered(limit, path_filter, method_filter)
        return jsonify({
            "count": len(logs),
            "logs": [{
                "id": log.id, "user_id": log.user_id,
                "actor_type": log.actor_type.value, "role": log.role,
                "method": log.method, "path": log.path,
                "status_code": log.status_code, "ip_address": log.ip_address,
            } for log in logs],
        })
    finally:
        session.close()


# ── Match (public) ──

@report_bp.post("/match")
def match_candidate_to_job():
    from app.core.value_objects import CandidateProfile, JobRequirements
    from app.infrastructure.scoring.scoring_factory import ScoringFactory

    payload = request.get_json(silent=True) or {}
    cp = payload.get("candidate", {})
    jp = payload.get("job", {})

    errors = []
    name = cp.get("name", "")
    if not isinstance(name, str) or len(name.strip()) < 2:
        errors.append("Aday adi en az 2 karakter olmalidir")

    years = cp.get("years_experience", 0)
    if not isinstance(years, int) or years < 0 or years > 50:
        errors.append("Aday deneyim yili 0 ile 50 arasinda olmalidir")

    skills = cp.get("skills", [])
    if not isinstance(skills, list) or not all(isinstance(x, str) for x in skills):
        errors.append("Aday yetenekleri metin listesi olmalidir")

    title = jp.get("title", "")
    if not isinstance(title, str) or len(title.strip()) < 2:
        errors.append("Ilan basligi en az 2 karakter olmalidir")

    req_skills = jp.get("required_skills", [])
    min_exp = jp.get("min_years_experience", 0)

    if errors:
        return jsonify({"errors": errors}), 400

    candidate = CandidateProfile(
        name=name.strip(), years_experience=years,
        skills=skills, education_level=cp.get("education_level", "lisans"),
    )
    job = JobRequirements(
        title=title.strip(), min_years_experience=min_exp,
        required_skills=req_skills,
    )

    strategy = ScoringFactory.create()
    score, reasons = strategy.calculate(candidate, job)
    return jsonify({"score": score, "reasons": reasons})
