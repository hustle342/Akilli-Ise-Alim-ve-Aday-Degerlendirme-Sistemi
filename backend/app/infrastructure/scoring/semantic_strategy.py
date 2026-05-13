"""
SemanticScoringStrategy — Behavioural: Strategy Pattern
=========================================================
Semantik benzerlik tabanli skorlama stratejisi.
sentence-transformers (BERT/RoBERTa) kullanilarak aday profili
ile ilan gereksinimleri arasindaki semantik benzerlik hesaplanir.

sentence-transformers yuklu degilse TF-IDF tabanlı cosine
similarity fallback kullanilir.
"""

import logging
import math
from collections import Counter
from typing import List, Set, Tuple

from app.core.interfaces.services import IScoringStrategy

logger = logging.getLogger(__name__)

# sentence-transformers opsiyonel
try:
    from sentence_transformers import SentenceTransformer, util as st_util
    HAS_SBERT = True
except ImportError:
    HAS_SBERT = False


class SemanticScoringStrategy(IScoringStrategy):
    """
    Semantik skorlama stratejisi.

    Skor bilesenleri:
    - Semantik benzerlik: %50 (BERT veya TF-IDF cosine)
    - Beceri eslesmesi: %30
    - Deneyim uyumu: %20

    sentence-transformers yuklu degilse TF-IDF cosine similarity
    fallback olarak kullanilir.
    """

    VERSION = "v2-semantic"
    SEMANTIC_WEIGHT = 50
    SKILL_WEIGHT = 30
    EXPERIENCE_WEIGHT = 20

    _model = None
    _model_loaded = False

    def __init__(self):
        if HAS_SBERT and not SemanticScoringStrategy._model_loaded:
            try:
                SemanticScoringStrategy._model = SentenceTransformer(
                    "all-MiniLM-L6-v2"
                )
                SemanticScoringStrategy._model_loaded = True
                logger.info("[Semantic] SBERT modeli yuklendi: all-MiniLM-L6-v2")
            except Exception as e:
                logger.warning(f"[Semantic] SBERT yuklenemedi, TF-IDF fallback: {e}")
                SemanticScoringStrategy._model_loaded = True

    def calculate(self, candidate, job) -> Tuple[float, List[str]]:
        """Semantik benzerlik tabanli skor hesapla."""
        reasons = []
        score = 0.0

        # ── 1. Semantik Benzerlik (%50) ──
        candidate_text = self._build_candidate_text(candidate)
        job_text = self._build_job_text(job)

        if self._model is not None:
            sim_score = self._sbert_similarity(candidate_text, job_text)
            reasons.append(f"SBERT semantik benzerlik: {sim_score:.3f}")
        else:
            sim_score = self._tfidf_cosine_similarity(candidate_text, job_text)
            reasons.append(f"TF-IDF cosine benzerlik: {sim_score:.3f}")

        score += sim_score * self.SEMANTIC_WEIGHT

        # ── 2. Beceri Eslesmesi (%30) ──
        required = {s.strip().lower() for s in job.required_skills}
        candidate_skills = {s.strip().lower() for s in candidate.skills}

        if required:
            overlap = required.intersection(candidate_skills)
            skill_ratio = len(overlap) / len(required)
            score += skill_ratio * self.SKILL_WEIGHT
            reasons.append(f"Skill eslesme orani: {skill_ratio:.2f}")
        else:
            score += 15
            reasons.append("Ilan zorunlu yetenek tanimi yok")

        # ── 3. Deneyim Uyumu (%20) ──
        min_exp = job.min_years_experience
        candidate_exp = candidate.years_experience
        if min_exp == 0:
            score += self.EXPERIENCE_WEIGHT
            reasons.append("Minimum deneyim sarti yok")
        else:
            exp_ratio = min(candidate_exp / min_exp, 1.0)
            score += exp_ratio * self.EXPERIENCE_WEIGHT
            reasons.append(f"Deneyim uygunluk orani: {exp_ratio:.2f}")

        return round(score, 2), reasons

    def get_version(self) -> str:
        engine = "sbert" if self._model is not None else "tfidf"
        return f"{self.VERSION}-{engine}"

    def _build_candidate_text(self, candidate) -> str:
        """Aday profilinden metin olustur."""
        parts = [candidate.name]
        if candidate.skills:
            parts.append("Skills: " + ", ".join(candidate.skills))
        if candidate.years_experience:
            parts.append(f"{candidate.years_experience} years experience")
        if hasattr(candidate, "education_level") and candidate.education_level:
            parts.append(f"Education: {candidate.education_level}")
        return " ".join(parts)

    def _build_job_text(self, job) -> str:
        """Ilan gereksinimlerinden metin olustur."""
        parts = [job.title]
        if job.required_skills:
            parts.append("Required: " + ", ".join(job.required_skills))
        if job.min_years_experience:
            parts.append(f"Minimum {job.min_years_experience} years experience")
        return " ".join(parts)

    def _sbert_similarity(self, text_a: str, text_b: str) -> float:
        """BERT/RoBERTa ile semantik benzerlik hesapla (0-1)."""
        try:
            embeddings = self._model.encode([text_a, text_b])
            similarity = st_util.cos_sim(embeddings[0], embeddings[1])
            return max(0.0, float(similarity[0][0]))
        except Exception as e:
            logger.warning(f"[Semantic] SBERT hatasi, TF-IDF fallback: {e}")
            return self._tfidf_cosine_similarity(text_a, text_b)

    def _tfidf_cosine_similarity(self, text_a: str, text_b: str) -> float:
        """
        TF-IDF tabanli cosine similarity — sentence-transformers
        yokken fallback olarak kullanilir.
        """
        words_a = self._tokenize(text_a)
        words_b = self._tokenize(text_b)

        if not words_a or not words_b:
            return 0.0

        # Terim frekansi
        counter_a = Counter(words_a)
        counter_b = Counter(words_b)

        # Ortak kelimeler uzerinden cosine hesapla
        all_words = set(counter_a.keys()) | set(counter_b.keys())

        dot_product = sum(counter_a.get(w, 0) * counter_b.get(w, 0) for w in all_words)
        magnitude_a = math.sqrt(sum(v ** 2 for v in counter_a.values()))
        magnitude_b = math.sqrt(sum(v ** 2 for v in counter_b.values()))

        if magnitude_a == 0 or magnitude_b == 0:
            return 0.0

        return dot_product / (magnitude_a * magnitude_b)

    def _tokenize(self, text: str) -> List[str]:
        """Basit tokenizasyon — stopword cikarimi ile."""
        stopwords = {
            "the", "a", "an", "is", "are", "was", "were", "in", "on", "at",
            "to", "for", "of", "with", "and", "or", "but", "not", "this",
            "that", "it", "be", "have", "has", "had", "do", "does", "did",
            "will", "would", "could", "should", "can", "may", "might",
            "ve", "ile", "bir", "bu", "su", "o", "de", "da", "den", "dan",
            "icin", "olan", "ile", "olarak", "uzerinde", "gibi",
        }
        words = text.lower().split()
        return [
            w.strip(".,;:()[]{}\"'")
            for w in words
            if w.strip(".,;:()[]{}\"'") not in stopwords and len(w) > 1
        ]
