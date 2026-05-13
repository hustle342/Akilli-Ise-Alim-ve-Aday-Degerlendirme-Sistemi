"""
Service Interfaces — OOP: Abstraction
=======================================
Karmaşık iş mantıkları ve dış bağımlılıklar soyutlanarak
sistemin diğer parçalarından izole edilmiştir.
"""

from abc import ABC, abstractmethod
from typing import List, Tuple


class IScoringStrategy(ABC):
    """
    Skorlama strateji arayüzü (Behavioural: Strategy Pattern).

    Farklı skorlama algoritmaları bu arayüzü implemente eder.
    Çalışma zamanında strateji değiştirilebilir.
    """

    @abstractmethod
    def calculate(self, candidate, job) -> Tuple[float, List[str]]:
        """
        Aday-iş uyum skorunu hesapla.

        Returns:
            Tuple[float, List[str]]: (skor, açıklama listesi)
        """
        pass

    @abstractmethod
    def get_version(self) -> str:
        """Strateji versiyonunu döndür."""
        pass


class ICVParser(ABC):
    """
    CV Parser arayüzü (Structural: Adapter Pattern için temel).

    Dış kütüphaneler bu arayüze adapt edilir.
    """

    @abstractmethod
    def parse_bytes(self, file_bytes: bytes) -> dict:
        """
        CV dosyasını parse et.

        Returns:
            dict: {"summary": str, "skills": list, "years_experience": int}
        """
        pass

    @abstractmethod
    def save_cv(self, file_bytes: bytes, original_filename: str) -> str:
        """
        CV dosyasını sakla.

        Returns:
            str: Kayıt yolu
        """
        pass


class INotificationService(ABC):
    """
    Bildirim servisi arayüzü (Behavioural: Observer Pattern).

    Sistem olaylarında bildirim gönderir.
    """

    @abstractmethod
    def notify(self, event_type: str, data: dict) -> None:
        """Bildirim gönder."""
        pass
