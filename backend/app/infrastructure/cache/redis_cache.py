"""
Redis Cache Manager — Infrastructure Layer
=============================================
Redis onbellek entegrasyonu.
Sik okunan verileri (ilan listesi, raporlar) onbellekte tutar.
Redis baglantisi yoksa in-memory fallback kullanir.

Singleton Pattern ile tek bir Redis baglantisi yonetilir.
"""

import json
import logging
import threading
from datetime import datetime, timezone
from typing import Any, Optional

from app.infrastructure.config import settings

logger = logging.getLogger(__name__)

# redis opsiyonel bagimlilik
try:
    import redis
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False
    redis = None


class RedisCacheManager:
    """
    Singleton Redis Cache Manager.

    Ozellikler:
    - Redis baglantisindan bagimsiz in-memory fallback
    - TTL (Time To Live) destegi
    - JSON serialization
    - Cache invalidation (key veya prefix bazli)
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

        self._redis_client = None
        self._memory_cache: dict[str, dict] = {}
        self._default_ttl = settings.REDIS_CACHE_TTL
        self._enabled = settings.REDIS_CACHE_ENABLED

        if HAS_REDIS and settings.REDIS_URL:
            try:
                self._redis_client = redis.from_url(
                    settings.REDIS_URL,
                    decode_responses=True,
                    socket_connect_timeout=3,
                    socket_timeout=3,
                )
                # Baglanti testi
                self._redis_client.ping()
                logger.info(
                    f"[Cache] Redis baglantisi basarili: {settings.REDIS_URL}"
                )
            except Exception as e:
                logger.warning(
                    f"[Cache] Redis baglantisi basarisiz, in-memory fallback: {e}"
                )
                self._redis_client = None
        else:
            if not HAS_REDIS:
                logger.info("[Cache] redis-py yuklu degil, in-memory fallback")
            elif not settings.REDIS_URL:
                logger.info("[Cache] REDIS_URL bos, in-memory fallback")

    @property
    def is_redis_connected(self) -> bool:
        """Redis'e baglanilmis mi?"""
        return self._redis_client is not None

    def get(self, key: str) -> Optional[Any]:
        """
        Onbellekten deger oku.

        Returns:
            Deger varsa deserialize edilmis JSON, yoksa None
        """
        if not self._enabled:
            return None

        if self._redis_client:
            try:
                value = self._redis_client.get(key)
                if value is not None:
                    logger.debug(f"[Cache] HIT (Redis): {key}")
                    return json.loads(value)
                logger.debug(f"[Cache] MISS (Redis): {key}")
                return None
            except Exception as e:
                logger.warning(f"[Cache] Redis okuma hatasi: {e}")
                return None

        # In-memory fallback
        entry = self._memory_cache.get(key)
        if entry is None:
            logger.debug(f"[Cache] MISS (memory): {key}")
            return None

        # TTL kontrolu
        if entry["expires_at"] < datetime.now(timezone.utc).timestamp():
            del self._memory_cache[key]
            logger.debug(f"[Cache] EXPIRED (memory): {key}")
            return None

        logger.debug(f"[Cache] HIT (memory): {key}")
        return entry["value"]

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Onbellege deger yaz.

        Args:
            key: Anahtar
            value: JSON serializable deger
            ttl: Yasam suresi (saniye), None ise default TTL
        """
        if not self._enabled:
            return

        ttl = ttl or self._default_ttl

        if self._redis_client:
            try:
                self._redis_client.setex(key, ttl, json.dumps(value, default=str))
                logger.debug(f"[Cache] SET (Redis): {key} TTL={ttl}s")
                return
            except Exception as e:
                logger.warning(f"[Cache] Redis yazma hatasi: {e}")

        # In-memory fallback
        self._memory_cache[key] = {
            "value": value,
            "expires_at": datetime.now(timezone.utc).timestamp() + ttl,
        }
        logger.debug(f"[Cache] SET (memory): {key} TTL={ttl}s")

    def delete(self, key: str) -> None:
        """Belirli bir anahtari onbellekten sil."""
        if self._redis_client:
            try:
                self._redis_client.delete(key)
            except Exception:
                pass

        self._memory_cache.pop(key, None)
        logger.debug(f"[Cache] DELETE: {key}")

    def invalidate_prefix(self, prefix: str) -> None:
        """
        Belirli bir prefix ile baslayan tum anahtarlari sil.
        Ornegin: "jobs:" ile baslayan tum kayitlari temizle.
        """
        if self._redis_client:
            try:
                keys = self._redis_client.keys(f"{prefix}*")
                if keys:
                    self._redis_client.delete(*keys)
                    logger.info(
                        f"[Cache] INVALIDATE (Redis): {prefix}* ({len(keys)} anahtar)"
                    )
            except Exception as e:
                logger.warning(f"[Cache] Redis invalidate hatasi: {e}")

        # In-memory fallback
        to_delete = [k for k in self._memory_cache if k.startswith(prefix)]
        for k in to_delete:
            del self._memory_cache[k]
        if to_delete:
            logger.info(
                f"[Cache] INVALIDATE (memory): {prefix}* ({len(to_delete)} anahtar)"
            )

    def clear(self) -> None:
        """Tum onbellegi temizle."""
        if self._redis_client:
            try:
                self._redis_client.flushdb()
            except Exception:
                pass

        self._memory_cache.clear()
        logger.info("[Cache] Tum onbellek temizlendi")

    def get_stats(self) -> dict:
        """Onbellek istatistiklerini dondur."""
        stats = {
            "backend": "redis" if self._redis_client else "memory",
            "enabled": self._enabled,
        }

        if self._redis_client:
            try:
                info = self._redis_client.info("stats")
                stats.update({
                    "hits": info.get("keyspace_hits", 0),
                    "misses": info.get("keyspace_misses", 0),
                    "keys": self._redis_client.dbsize(),
                })
            except Exception:
                stats["error"] = "Redis istatistik alinamadi"
        else:
            stats["keys"] = len(self._memory_cache)

        return stats

    @classmethod
    def reset(cls):
        """Singleton'i sifirla (test icin)."""
        with cls._lock:
            cls._instance = None


# Modul seviyesinde tekil instance
cache_manager = RedisCacheManager()
