"""
Akilli Ise Alim ve Aday Degerlendirme Sistemi — Application Entry Point
==========================================================================
Onion Architecture:
  Core (Domain) → Application → Infrastructure → Presentation

Design Patterns:
  - Singleton: ConfigurationManager, DatabaseManager
  - Factory Method: ScoringFactory
  - Facade: RecruitmentFacade
  - Adapter: CVParserAdapter
  - Strategy: RuleBasedScoringStrategy
  - Observer: Event Handlers (ESB)

Ek Yapilar:
  - CQRS: Command/Query Separation
  - ESB: InMemoryEventBus (Redis Pub/Sub hazir)
  - Real-Time: WebSocket (flask-socketio)
"""

from flask import Flask, jsonify
from flask_cors import CORS

# ── Core Layer ──
from app.core.entities import Base

# ── Infrastructure Layer ──
from app.infrastructure.database.db_manager import db_manager
from app.infrastructure.event_bus.in_memory_event_bus import InMemoryEventBus
from app.infrastructure.event_bus.event_handlers import register_all_handlers

# ── Presentation Layer ──
from app.presentation.api.v1.auth_routes import auth_bp
from app.presentation.api.v1.job_routes import job_bp
from app.presentation.api.v1.application_routes import application_bp
from app.presentation.api.v1.report_routes import report_bp
from app.presentation.api.middleware.audit_middleware import write_audit_log
from app.presentation.websocket.ws_handler import init_websocket

# ── Geriye Donuk Uyumluluk: eski import path'leri calismaya devam etsin ──
from app.api.v1.routes import v1_bp


def create_app() -> Flask:
    """Flask uygulama fabrikasi — Onion Architecture."""
    app = Flask(__name__)
    CORS(app)

    # ── 1. Veritabani (Infrastructure: Singleton) ──
    db_manager.create_tables(Base)
    db_manager.ensure_schema()

    # ── 2. ESB & Observer Pattern ──
    event_bus = InMemoryEventBus()
    register_all_handlers(event_bus)

    # ── 3. Health Check (Presentation) ──
    @app.get("/health")
    def health_check():
        return jsonify({"status": "ok"})

    # ── 4. Audit Middleware (Presentation) ──
    app.after_request(write_audit_log)

    # ── 5. Blueprint Kayitlari (Presentation) ──
    # Yeni modüler route'lar
    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
    app.register_blueprint(job_bp, url_prefix="/api/v1/jobs")
    app.register_blueprint(application_bp, url_prefix="/api/v1/applications")
    app.register_blueprint(report_bp, url_prefix="/api/v1")

    # Eski monolitik route'lar (geriye donuk uyumluluk)
    app.register_blueprint(v1_bp, url_prefix="/api/v1")

    # ── 6. WebSocket — Real-Time Communication ──
    init_websocket(app)

    return app


app = create_app()
