"""
InMemoryEventBus — ESB (Enterprise Service Bus) Implementasyonu
================================================================
Servisler arası asenkron iletişim için in-memory event bus.
Observer Pattern ile event handler'ları yönetir.

Redis Pub/Sub desteği gelecekte eklenebilir.
Bu implementasyon sayesinde modüller birbirine sıkı sıkıya bağlı olmaz (loose coupling).
"""

import logging
import threading
from collections import defaultdict
from typing import Callable, List

from app.core.interfaces.event_bus import IEventBus

logger = logging.getLogger(__name__)


class InMemoryEventBus(IEventBus):
    """
    In-Memory Event Bus — ESB prensibi ile servisler arası mesajlaşma.

    Singleton olarak kullanılır.
    Observer Pattern: subscribe/publish mekanizması.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._subscribers: dict[str, List[Callable]] = defaultdict(list)
        self._event_log: List[dict] = []

    def publish(self, event_type: str, data: dict) -> None:
        """
        Bir olayı yayınla — tüm abonelere bildir.

        Args:
            event_type: Olay tipi (örn: "application.created")
            data: Olay verisi
        """
        event_record = {"event_type": event_type, "data": data}
        self._event_log.append(event_record)

        handlers = self._subscribers.get(event_type, [])
        for handler in handlers:
            try:
                handler(event_type, data)
                logger.info(
                    f"[ESB] Event '{event_type}' → Handler '{handler.__name__}' başarılı"
                )
            except Exception as e:
                logger.error(
                    f"[ESB] Event '{event_type}' → Handler '{handler.__name__}' hata: {e}"
                )

    def subscribe(self, event_type: str, handler: Callable) -> None:
        """
        Bir olay tipine abone ol.

        Args:
            event_type: Dinlenecek olay tipi
            handler: Olay gerçekleştiğinde çağrılacak fonksiyon
        """
        self._subscribers[event_type].append(handler)
        logger.info(
            f"[ESB] '{handler.__name__}' → '{event_type}' olayına abone oldu"
        )

    def get_subscribers(self, event_type: str) -> List[Callable]:
        """Belirli bir olay tipinin abonelerini döndür."""
        return self._subscribers.get(event_type, [])

    def get_event_log(self) -> List[dict]:
        """Olay geçmişini döndür (debug/audit)."""
        return list(self._event_log)

    def clear(self) -> None:
        """Tüm abonelikleri ve log'u temizle (test için)."""
        self._subscribers.clear()
        self._event_log.clear()

    @classmethod
    def reset(cls):
        """Singleton'ı sıfırla (test için)."""
        with cls._lock:
            cls._instance = None
