"""
NotificationService — Behavioural: Observer Pattern
=====================================================
Sistem olaylarında bildirim gönderen servis.
INotificationService arayüzünü implemente eder.
"""

import logging
from datetime import datetime, timezone
from typing import List, Dict, Any

from app.core.interfaces.services import INotificationService

logger = logging.getLogger(__name__)


class NotificationService(INotificationService):
    """
    Bildirim servisi — Observer Pattern ile çalışır.

    Gelen olayları loglar ve gelecekte WebSocket üzerinden
    real-time bildirim gönderecektir.
    """

    def __init__(self):
        self._notifications: List[Dict[str, Any]] = []

    def notify(self, event_type: str, data: dict) -> None:
        """
        Bildirim oluştur ve kaydet.

        Args:
            event_type: Olay tipi
            data: Olay verisi
        """
        notification = {
            "event_type": event_type,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "delivered": False,
        }
        self._notifications.append(notification)

        logger.info(f"[Notification] {event_type}: {data}")

    def get_pending(self) -> List[Dict[str, Any]]:
        """Teslim edilmemiş bildirimleri döndür."""
        return [n for n in self._notifications if not n["delivered"]]

    def mark_delivered(self, index: int) -> None:
        """Bildirimi teslim edildi olarak işaretle."""
        if 0 <= index < len(self._notifications):
            self._notifications[index]["delivered"] = True
