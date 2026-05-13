"""
Geriye Donuk Uyumluluk — services/scoring.py
===============================================
ScoringService artik infrastructure.scoring.rule_based_strategy'de.
"""

from app.infrastructure.scoring.rule_based_strategy import RuleBasedScoringStrategy


class ScoringService:
    """Geriye donuk uyumluluk wrapper."""

    def __init__(self):
        self._strategy = RuleBasedScoringStrategy()

    def calculate(self, candidate, job):
        return self._strategy.calculate(candidate, job)
