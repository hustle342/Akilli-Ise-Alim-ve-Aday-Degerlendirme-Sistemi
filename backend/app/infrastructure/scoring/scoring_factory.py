"""
ScoringFactory — Creational: Factory Method Pattern
=====================================================
Farklı skorlama stratejilerinin dinamik olarak üretilmesini sağlar.

Factory Method sayesinde:
- İstemci kodu, hangi skorlama stratejisinin kullanıldığını bilmez
- Yeni strateji eklenmesi sadece factory'ye kayıt gerektirir
- Open/Closed Principle uyumu
"""

from app.core.interfaces.services import IScoringStrategy
from app.infrastructure.scoring.rule_based_strategy import RuleBasedScoringStrategy
from app.infrastructure.scoring.semantic_strategy import SemanticScoringStrategy


class ScoringFactory:
    """
    Skorlama strateji fabrikası.

    Kullanım:
        strategy = ScoringFactory.create("rule_based")
        score, reasons = strategy.calculate(candidate, job)
    """

    _strategies = {
        "rule_based": RuleBasedScoringStrategy,
        "semantic": SemanticScoringStrategy,
    }

    @classmethod
    def create(cls, strategy_type: str = "rule_based") -> IScoringStrategy:
        """
        Belirtilen tipteki skorlama stratejisini oluştur.

        Args:
            strategy_type: "rule_based" veya "semantic"

        Returns:
            IScoringStrategy implementasyonu

        Raises:
            ValueError: Bilinmeyen strateji tipi
        """
        strategy_class = cls._strategies.get(strategy_type)
        if strategy_class is None:
            available = ", ".join(cls._strategies.keys())
            raise ValueError(
                f"Bilinmeyen skorlama stratejisi: '{strategy_type}'. "
                f"Mevcut stratejiler: {available}"
            )
        return strategy_class()

    @classmethod
    def register(cls, name: str, strategy_class: type) -> None:
        """
        Yeni bir skorlama stratejisi kaydet.

        Args:
            name: Strateji adı
            strategy_class: IScoringStrategy implementasyonu
        """
        cls._strategies[name] = strategy_class

    @classmethod
    def available_strategies(cls) -> list:
        """Mevcut strateji isimlerini döndür."""
        return list(cls._strategies.keys())
