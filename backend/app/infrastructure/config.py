"""
ConfigurationManager — Creational: Singleton Pattern
======================================================
Uygulama ayarlarının tekil instance üzerinden yönetilmesini sağlar.
Tüm konfigürasyon değerleri merkezi bir noktadan erişilir.
Thread-safe Singleton implementasyonu.
"""

import os
import threading


class ConfigurationManager:
    """
    Singleton Configuration Manager.

    Tekil nesne garantisi ile uygulama ayarlarını yönetir.
    Thread-safe: Çoklu iş parçacıklarında güvenli çalışır.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                # Double-checked locking
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._load_settings()

    def _load_settings(self):
        """Ortam değişkenlerinden ayarları yükle."""
        self.DATABASE_URL: str = os.getenv(
            "DATABASE_URL", "sqlite+pysqlite:///./recruitment.db"
        )
        self.CV_STORAGE_DIR: str = os.getenv("CV_STORAGE_DIR", "backend/storage/cv")
        self.AUTO_INVITE_SCORE_THRESHOLD: float = float(
            os.getenv("AUTO_INVITE_SCORE_THRESHOLD", "70")
        )
        self.SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
        self.ACCESS_TOKEN_MAX_AGE_SECONDS: int = int(
            os.getenv("ACCESS_TOKEN_MAX_AGE_SECONDS", "86400")
        )
        self.REFRESH_TOKEN_MAX_AGE_SECONDS: int = int(
            os.getenv("REFRESH_TOKEN_MAX_AGE_SECONDS", "604800")
        )
        self.ADMIN_BOOTSTRAP_CODE: str = os.getenv(
            "ADMIN_BOOTSTRAP_CODE", "dev-bootstrap-code"
        )

        # ── PostgreSQL bağlantı havuzu ayarları ──
        self.DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "5"))
        self.DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))
        self.DB_POOL_RECYCLE: int = int(os.getenv("DB_POOL_RECYCLE", "3600"))

        # ── Redis önbellek ayarları ──
        self.REDIS_URL: str = os.getenv("REDIS_URL", "")
        self.REDIS_CACHE_TTL: int = int(os.getenv("REDIS_CACHE_TTL", "300"))
        self.REDIS_CACHE_ENABLED: bool = os.getenv("REDIS_CACHE_ENABLED", "true").lower() == "true"

        # ── Diğer ayarlar ──
        self.SCORING_STRATEGY: str = os.getenv("SCORING_STRATEGY", "rule_based")
        self.ENV: str = os.getenv("FLASK_ENV", "development")

    @property
    def is_production(self) -> bool:
        """Üretim ortamında mı çalışıyor?"""
        return self.ENV == "production"

    @property
    def is_postgresql(self) -> bool:
        """PostgreSQL mu kullanılıyor?"""
        return "postgresql" in self.DATABASE_URL

    @classmethod
    def reset(cls):
        """Test ortamında singleton'ı sıfırla."""
        with cls._lock:
            cls._instance = None


# Modül seviyesinde tekil instance — Singleton erişim noktası
settings = ConfigurationManager()
