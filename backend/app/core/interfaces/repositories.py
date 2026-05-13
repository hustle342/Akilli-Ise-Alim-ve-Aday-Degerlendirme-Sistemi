"""
Repository Interfaces — OOP: Abstraction + Polymorphism
========================================================
Soyut repository arayüzleri.
Infrastructure katmanında implementasyonları sağlanır.
Farklı veritabanı sağlayıcıları bu arayüzleri implemente ederek
çalışma zamanında yer değiştirebilir (Polymorphism).
"""

from abc import ABC, abstractmethod
from typing import List, Optional


class IRepository(ABC):
    """Genel repository arayüzü (Generic)."""

    @abstractmethod
    def get_by_id(self, entity_id: int):
        """ID ile entity getir."""
        pass

    @abstractmethod
    def get_all(self) -> list:
        """Tüm entity'leri getir."""
        pass

    @abstractmethod
    def add(self, entity) -> None:
        """Yeni entity ekle."""
        pass

    @abstractmethod
    def delete(self, entity) -> None:
        """Entity sil."""
        pass

    @abstractmethod
    def commit(self) -> None:
        """İşlemi onayla."""
        pass


class IUserRepository(IRepository):
    """Kullanıcı repository arayüzü."""

    @abstractmethod
    def get_by_email(self, email: str):
        """Email ile kullanıcı bul."""
        pass

    @abstractmethod
    def count_by_role(self, role) -> int:
        """Belirli roldeki kullanıcı sayısını döndür."""
        pass


class IJobRepository(IRepository):
    """İş ilanı repository arayüzü."""

    @abstractmethod
    def get_all_ordered(self) -> list:
        """Tüm ilanları tarih sırasıyla getir."""
        pass


class IApplicationRepository(IRepository):
    """Başvuru repository arayüzü."""

    @abstractmethod
    def get_by_candidate(self, candidate_id: int) -> list:
        """Adayın başvurularını getir."""
        pass

    @abstractmethod
    def get_by_job(self, job_posting_id: int) -> list:
        """İlana yapılan başvuruları getir."""
        pass

    @abstractmethod
    def count_by_job(self, job_posting_id: int) -> int:
        """İlana başvuru sayısını döndür."""
        pass


class IMatchScoreRepository(IRepository):
    """Uyum skoru repository arayüzü."""

    @abstractmethod
    def get_by_application(self, application_id: int):
        """Başvuruya ait skoru getir."""
        pass

    @abstractmethod
    def get_stats_by_job(self, job_posting_id: int) -> dict:
        """İlan bazlı istatistikleri döndür."""
        pass


class IInvitationRepository(IRepository):
    """Davet repository arayüzü."""

    @abstractmethod
    def get_by_application(self, application_id: int):
        """Başvuruya ait davetleri getir."""
        pass

    @abstractmethod
    def get_filtered(
        self, status: Optional[str] = None, job_posting_id: Optional[int] = None
    ) -> list:
        """Filtreli davet listesi getir."""
        pass

    @abstractmethod
    def count_by_job(self, job_posting_id: int) -> int:
        """İlan bazlı davet sayısını döndür."""
        pass


class IAuditLogRepository(IRepository):
    """Audit log repository arayüzü."""

    @abstractmethod
    def get_filtered(
        self,
        limit: int = 50,
        path_filter: Optional[str] = None,
        method_filter: Optional[str] = None,
    ) -> list:
        """Filtreli audit log listesi getir."""
        pass
