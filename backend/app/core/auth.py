from functools import wraps

from flask import jsonify, request
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from app.core.config import settings
from app.models.entities import UserRole


serializer = URLSafeTimedSerializer(settings.SECRET_KEY, salt="auth-token")


def _create_token(user_id: int, role: UserRole, email: str, token_type: str) -> str:
    payload = {
        "user_id": user_id,
        "role": role.value,
        "email": email,
        "token_type": token_type,
    }
    return serializer.dumps(payload)


def create_access_token(user_id: int, role: UserRole, email: str) -> str:
    return _create_token(user_id, role, email, "access")


def create_refresh_token(user_id: int, role: UserRole, email: str) -> str:
    return _create_token(user_id, role, email, "refresh")


def decode_token(token: str, max_age: int) -> dict:
    return serializer.loads(token, max_age=max_age)


def get_bearer_token() -> str | None:
    authorization = request.headers.get("Authorization", "")
    if not authorization.startswith("Bearer "):
        return None
    return authorization.split(" ", 1)[1].strip() or None


def require_roles(*allowed_roles: UserRole):
    allowed_values = {role.value for role in allowed_roles}

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            token = get_bearer_token()
            if token is None:
                return jsonify({"error": "Authorization Bearer token gerekli"}), 401

            try:
                payload = decode_token(token, settings.ACCESS_TOKEN_MAX_AGE_SECONDS)
            except SignatureExpired:
                return jsonify({"error": "Token suresi dolmus"}), 401
            except BadSignature:
                return jsonify({"error": "Token gecersiz"}), 401

            if payload.get("token_type") != "access":
                return jsonify({"error": "Access token gerekli"}), 401

            role = payload.get("role")
            if role not in allowed_values:
                return jsonify({"error": "Bu islem icin yetkiniz yok"}), 403

            request.auth = payload
            return func(*args, **kwargs)

        return wrapper

    return decorator
