"""
Application Routes — Presentation Layer
==========================================
Basvuru endpoint'leri (CV upload, listeleme).
"""

from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

from app.presentation.api.middleware.auth_middleware import require_roles
from app.application.services.facade import RecruitmentFacade
from app.core.enums import UserRole
from app.infrastructure.config import settings

application_bp = Blueprint("applications", __name__)
facade = RecruitmentFacade()


def _json_error(message: str, status: int = 400):
    return jsonify({"error": message}), status


@application_bp.post("/upload")
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
    auth_user_id = int(request.auth.get("user_id"))
    auth_role = request.auth.get("role")

    result, error, status = facade.upload_cv(
        candidate_id, job_posting_id, file_bytes, safe_name,
        auth_user_id, auth_role,
    )
    if error:
        return _json_error(error, status)

    return jsonify({
        "application_id": result.application_id,
        "candidate_id": result.candidate_id,
        "job_posting_id": result.job_posting_id,
        "cv_path": result.cv_path,
        "parsed_summary": result.parsed_summary,
        "extracted_skills": result.extracted_skills,
        "estimated_years_experience": result.estimated_years_experience,
        "match_score": result.match_score,
        "score_reasons": result.score_reasons,
        "auto_invite_threshold": result.auto_invite_threshold,
        "invitation_created": result.invitation_created,
        "storage_dir": settings.CV_STORAGE_DIR,
    }), 201


@application_bp.get("/me")
@require_roles(UserRole.CANDIDATE, UserRole.ADMIN)
def list_my_applications():
    auth_user_id = int(request.auth.get("user_id"))
    apps = facade.list_my_applications(auth_user_id)
    return jsonify({"count": len(apps), "applications": apps})
