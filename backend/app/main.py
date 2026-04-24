from flask import Flask, jsonify, request

from app.api.v1.routes import v1_bp
from app.core.db import SessionLocal, engine, ensure_schema
from app.models import AuditLog, Base
from app.models.entities import AuditActorType


def create_app() -> Flask:
    app = Flask(__name__)
    Base.metadata.create_all(bind=engine)
    ensure_schema()

    @app.get("/health")
    def health_check():
        return jsonify({"status": "ok"})

    @app.after_request
    def write_audit_log(response):
        session = SessionLocal()
        try:
            auth_payload = getattr(request, "auth", None) or {}
            user_id = auth_payload.get("user_id")
            role = auth_payload.get("role", "anonymous")
            actor_type = (
                AuditActorType.AUTHENTICATED if user_id is not None else AuditActorType.ANONYMOUS
            )
            ip_address = request.headers.get("X-Forwarded-For", request.remote_addr or "unknown")

            session.add(
                AuditLog(
                    user_id=user_id,
                    actor_type=actor_type,
                    role=role,
                    method=request.method,
                    path=request.path,
                    status_code=response.status_code,
                    ip_address=ip_address,
                )
            )
            session.commit()
        except Exception:
            session.rollback()
        finally:
            session.close()

        return response

    app.register_blueprint(v1_bp, url_prefix="/api/v1")
    return app


app = create_app()
