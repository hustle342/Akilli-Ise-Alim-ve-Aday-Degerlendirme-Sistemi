"""
Event Handlers — Behavioural: Observer Pattern
================================================
Sistemde gerçekleşen önemli olaylarda ilgili modüllere
anlık haber veren handler'lar.

Observer Pattern sayesinde:
- Yeni event handler eklemek mevcut kodu değiştirmez
- Modüller loose-coupled kalır
- Her handler bağımsız olarak test edilebilir
"""

import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def on_application_created(event_type: str, data: dict) -> None:
    """
    Yeni başvuru oluşturulduğunda tetiklenir.

    Observer: Bildirim servisi ve log servisi bu olayı dinler.
    """
    candidate_id = data.get("candidate_id")
    job_id = data.get("job_posting_id")
    application_id = data.get("application_id")

    logger.info(
        f"[Observer] Yeni başvuru: application_id={application_id}, "
        f"candidate_id={candidate_id}, job_id={job_id}"
    )


def on_score_calculated(event_type: str, data: dict) -> None:
    """
    Uyum skoru hesaplandığında tetiklenir.

    Observer: Bildirim servisi bu olayı dinler.
    """
    application_id = data.get("application_id")
    score = data.get("score")
    version = data.get("version", "unknown")

    logger.info(
        f"[Observer] Skor hesaplandi: application_id={application_id}, "
        f"score={score}, version={version}"
    )


def on_invitation_sent(event_type: str, data: dict) -> None:
    """
    Davet gönderildiğinde tetiklenir.

    Observer: Email servisi ve bildirim servisi bu olayı dinler.
    """
    application_id = data.get("application_id")
    invitation_type = data.get("invitation_type")

    logger.info(
        f"[Observer] Davet gönderildi: application_id={application_id}, "
        f"type={invitation_type}"
    )


def on_user_registered(event_type: str, data: dict) -> None:
    """
    Yeni kullanıcı kayıt olduğunda tetiklenir.

    Observer: Hoşgeldin email'i ve log kaydı.
    """
    user_id = data.get("user_id")
    role = data.get("role")
    email = data.get("email")

    logger.info(
        f"[Observer] Yeni kullanici: user_id={user_id}, role={role}, email={email}"
    )


def on_job_created(event_type: str, data: dict) -> None:
    """
    Yeni iş ilanı oluşturulduğunda tetiklenir.

    Observer: Aday bildirim sistemi bu olayı dinler.
    """
    job_id = data.get("job_id")
    title = data.get("title")

    logger.info(f"[Observer] Yeni ilan: job_id={job_id}, title={title}")


def register_all_handlers(event_bus) -> None:
    """
    Tüm event handler'ları event bus'a kaydet.

    Uygulama başlatılırken çağrılır.
    """
    event_bus.subscribe("application.created", on_application_created)
    event_bus.subscribe("score.calculated", on_score_calculated)
    event_bus.subscribe("invitation.sent", on_invitation_sent)
    event_bus.subscribe("user.registered", on_user_registered)
    event_bus.subscribe("job.created", on_job_created)

    logger.info("[Observer] Tüm event handler'lar kaydedildi")
