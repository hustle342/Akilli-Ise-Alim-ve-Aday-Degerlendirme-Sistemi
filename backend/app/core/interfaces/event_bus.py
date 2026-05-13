"""
Event Bus Interface — ESB (Enterprise Service Bus)
====================================================
Servisler arası asenkron iletişim için soyut arayüz.
Modüller birbirine sıkı sıkıya bağlı olmadan iletişim kurar.
"""

from abc import ABC, abstractmethod
from typing import Callable, List


class IEventBus(ABC):
    """
    Enterprise Service Bus arayüzü.

    Observer + ESB prensibi:
    - publish: Olay yayınla
    - subscribe: Olaya abone ol
    """

    @abstractmethod
    def publish(self, event_type: str, data: dict) -> None:
        """
        Bir olayı event bus üzerinden yayınla.

        Args:
            event_type: Olay tipi (EventType enum değeri)
            data: Olay verisi
        """
        pass

    @abstractmethod
    def subscribe(self, event_type: str, handler: Callable) -> None:
        """
        Bir olay tipine abone ol.

        Args:
            event_type: Dinlenecek olay tipi
            handler: Olay gerçekleştiğinde çağrılacak fonksiyon
        """
        pass

    @abstractmethod
    def get_subscribers(self, event_type: str) -> List[Callable]:
        """Belirli bir olay tipinin abonelerini döndür."""
        pass
