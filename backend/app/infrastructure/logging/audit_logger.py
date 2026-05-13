"""
AuditLogger — Observer Pattern (Log Servisi)
=============================================
Sistem olaylarını audit log olarak kaydeder.
Event Bus üzerinden gelen olayları dinler.
"""

import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class AuditLogger:
    """
    Observer: Log servisi.

    Event Bus'tan gelen olayları loglar.
    Ayrıca HTTP request audit logging de bu modülden yönetilir.
    """

    def __init__(self):
        self._log_entries = []

    def log_event(self, event_type: str, data: dict) -> None:
        """Domain event'i logla."""
        entry = {
            "event_type": event_type,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._log_entries.append(entry)
        logger.info(f"[AuditLogger] {event_type}: {data}")

    def get_recent(self, count: int = 50) -> list:
        """Son N log kaydını döndür."""
        return self._log_entries[-count:]
