"""
Auth Routes — Presentation Layer
===================================
Kimlik dogrulama endpoint'leri.
"""

from flask import Blueprint, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

from app.presentation.api.middleware.auth_middleware import (
    create_access_token, create_refresh_token, decode_token, require_roles,
)
from app.infrastructure.config import settings
from app.infrastructure.database.db_manager import db_manager
from app.infrastructure.database.repositories.user_repository import UserRepository
from app.infrastructure.event_bus.in_memory_event_bus import InMemoryEventBus
from app.application.commands.register_user import RegisterUserCommand, RegisterUserHandler
from app.core.enums import UserRole

auth_bp = Blueprint("auth", __name__)


def _json_error(message: str, status: int = 400):
    return jsonify({"error": message}), status


@auth_bp.post("/register")
def register_user():
    payload = request.get_json(silent=True) or {}
    session = db_manager.get_session()
    try:
        handler = RegisterUserHandler(UserRepository(session), InMemoryEventBus())
        cmd = RegisterUserCommand(
            full_name=(payload.get("full_name") or ""),
            email=(payload.get("email") or ""),
            password=payload.get("password") or "",
            role=(payload.get("role") or "candidate"),
            bootstrap_code=(payload.get("bootstrap_code") or ""),
        )
        result, error = handler.handle(cmd)
        if error:
            status = 403 if "bootstrap" in error else (409 if "kayitli" in error else 400)
            return _json_error(error, status)
        return jsonify({
            "id": result.id, "full_name": result.full_name,
            "email": result.email, "role": result.role,
        }), 201
    finally:
        session.close()


@auth_bp.post("/token")
def issue_token():
    payload = request.get_json(silent=True) or {}
    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password") or ""
    if "@" not in email:
        return _json_error("gecerli bir email girilmelidir")
    if not isinstance(password, str) or len(password) < 8:
        return _json_error("password en az 8 karakter olmalidir")

    session = db_manager.get_session()
    try:
        repo = UserRepository(session)
        user = repo.get_by_email(email)
        if user is None:
            return _json_error("kullanici bulunamadi", 404)
        if not user.password_hash or not check_password_hash(user.password_hash, password):
            return _json_error("email veya password hatali", 401)

        access_token = create_access_token(user.id, user.role, user.email)
        refresh_token = create_refresh_token(user.id, user.role, user.email)
        return jsonify({
            "access_token": access_token, "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {"id": user.id, "email": user.email, "role": user.role.value},
        })
    finally:
        session.close()


@auth_bp.post("/refresh")
def refresh_access_token():
    payload = request.get_json(silent=True) or {}
    refresh_token = (payload.get("refresh_token") or "").strip()
    if not refresh_token:
        return _json_error("refresh_token zorunludur")

    try:
        token_payload = decode_token(refresh_token, settings.REFRESH_TOKEN_MAX_AGE_SECONDS)
    except Exception:
        return _json_error("refresh token gecersiz", 401)

    if token_payload.get("token_type") != "refresh":
        return _json_error("refresh token bekleniyor", 401)

    try:
        role = UserRole(token_payload["role"])
    except ValueError:
        return _json_error("refresh token gecersiz", 401)

    access_token = create_access_token(
        token_payload["user_id"], role, token_payload["email"]
    )
    return jsonify({"access_token": access_token, "token_type": "bearer"})
