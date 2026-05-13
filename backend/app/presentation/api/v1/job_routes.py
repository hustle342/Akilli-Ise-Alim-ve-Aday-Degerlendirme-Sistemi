"""
Job Routes — Presentation Layer
==================================
Ilan endpoint'leri.
"""

from flask import Blueprint, jsonify, request

from app.presentation.api.middleware.auth_middleware import require_roles
from app.application.services.facade import RecruitmentFacade
from app.core.enums import UserRole

job_bp = Blueprint("jobs", __name__)
facade = RecruitmentFacade()


def _json_error(message: str, status: int = 400):
    return jsonify({"error": message}), status


@job_bp.post("")
@require_roles(UserRole.HR, UserRole.ADMIN)
def create_job_posting():
    payload = request.get_json(silent=True) or {}
    result, error = facade.create_job(
        title=(payload.get("title") or ""),
        description=(payload.get("description") or ""),
        min_years_experience=payload.get("min_years_experience", 0),
        required_skills=payload.get("required_skills", []),
    )
    if error:
        return _json_error(error)
    return jsonify({
        "id": result.id, "title": result.title,
        "min_years_experience": result.min_years_experience,
        "required_skills": result.required_skills,
    }), 201


@job_bp.get("")
@require_roles(UserRole.CANDIDATE, UserRole.HR, UserRole.ADMIN)
def list_jobs():
    jobs = facade.list_jobs()
    return jsonify({"count": len(jobs), "jobs": jobs})
