"""
RuleBasedScoringStrategy — Behavioural: Strategy Pattern
=========================================================
Kural tabanlı skorlama stratejisi.
IScoringStrategy arayüzünü implemente eder.

Strategy Pattern sayesinde:
- Farklı skorlama algoritmaları çalışma zamanında değiştirilebilir
- Yeni strateji eklemek mevcut kodu değiştirmeyi gerektirmez
- Open/Closed Principle'a uygun yapı
"""

from typing import List, Set, Tuple

from app.core.interfaces.services import IScoringStrategy


class RuleBasedScoringStrategy(IScoringStrategy):
    """
    Kural tabanlı skorlama stratejisi.

    Beceri eşleşme oranı (%60 ağırlık) + Deneyim uyumu (%25 ağırlık)
    + Eğitim seviyesi (%15 ağırlık)
    """

    SKILL_WEIGHT = 60
    EXPERIENCE_WEIGHT = 25
    EDUCATION_WEIGHT = 15
    VERSION = "v1.1-rule-based"

    # Beceri ailesi eslestirmesi — kismi eslestirme icin
    SKILL_FAMILIES = {
        "sql": {"postgresql", "mysql", "sqlite", "oracle", "mariadb", "sql"},
        "cloud": {"aws", "azure", "gcp"},
        "javascript": {"typescript", "javascript"},
    }

    # Egitim seviyesi puanlari (0.0 - 1.0)
    EDUCATION_SCORES = {
        "doktora": 1.0,
        "yuksek_lisans": 0.85,
        "lisans": 0.65,
        "on_lisans": 0.45,
        "lise": 0.25,
    }

    def calculate(self, candidate, job) -> Tuple[float, List[str]]:
        """Kural tabanlı skor hesapla."""
        reasons = []
        score = 0.0

        # ── 1. Skill Eslesmesi (%60) ──
        required = {skill.strip().lower() for skill in job.required_skills}
        candidate_skills = {skill.strip().lower() for skill in candidate.skills}

        if required:
            matched, partial = self._match_skills(required, candidate_skills)
            total_matched = len(matched) + len(partial) * 0.5
            skill_ratio = min(total_matched / len(required), 1.0)
            skill_score = skill_ratio * self.SKILL_WEIGHT
            reasons.append(f"Skill eslesme orani: {skill_ratio:.2f}")
            if matched:
                reasons.append(f"  Tam eslesen: {', '.join(sorted(matched))}")
            if partial:
                reasons.append(f"  Kismi eslesen (aile): {', '.join(sorted(partial))}")
        else:
            skill_score = self.SKILL_WEIGHT * 0.5
            reasons.append("Ilanda zorunlu yetenek tanimi yok, varsayilan puan verildi")

        score += skill_score

        # ── 2. Deneyim Uyumu (%25) ──
        min_exp = job.min_years_experience
        candidate_exp = candidate.years_experience
        if min_exp == 0:
            score += self.EXPERIENCE_WEIGHT
            reasons.append("Minimum deneyim sarti yok")
        else:
            exp_ratio = min(candidate_exp / min_exp, 1.0)
            exp_score = exp_ratio * self.EXPERIENCE_WEIGHT
            score += exp_score
            reasons.append(f"Deneyim uygunluk orani: {exp_ratio:.2f}")

            # Deneyim yetersizlik cezasi
            if candidate_exp < min_exp:
                deficiency = 1.0 - (candidate_exp / min_exp)
                penalty = deficiency * 0.5 * skill_score
                score -= penalty
                reasons.append(
                    f"Deneyim yetersizlik cezasi: -{penalty:.1f} puan "
                    f"(istenen: {min_exp} yil, aday: {candidate_exp} yil)"
                )

        # ── 3. Egitim Seviyesi (%15) ──
        edu_level = getattr(candidate, "education_level", "lisans") or "lisans"
        edu_score_ratio = self.EDUCATION_SCORES.get(edu_level, 0.5)
        edu_score = edu_score_ratio * self.EDUCATION_WEIGHT
        score += edu_score
        reasons.append(f"Egitim seviyesi: {edu_level} ({edu_score_ratio:.2f})")

        return round(score, 2), reasons

    def get_version(self) -> str:
        return self.VERSION

    def _match_skills(
        self, required: Set[str], candidate_skills: Set[str]
    ) -> Tuple[Set[str], Set[str]]:
        """
        Beceri eslestirmesi — tam + aile bazli kismi eslestirme.

        Returns:
            (tam_eslesen, kismi_eslesen) skill setleri
        """
        exact_matches = required.intersection(candidate_skills)
        remaining = required - exact_matches
        partial_matches = set()

        for req_skill in remaining:
            # Aile bazli eslestirme: "sql" isteniyor, aday "postgresql" biliyor
            for family_key, family_members in self.SKILL_FAMILIES.items():
                if req_skill == family_key or req_skill in family_members:
                    # Adayin skill'lerinden biri bu aileye ait mi?
                    if candidate_skills.intersection(family_members):
                        partial_matches.add(req_skill)
                        break

        return exact_matches, partial_matches
