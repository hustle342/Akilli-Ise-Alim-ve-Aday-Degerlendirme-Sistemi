class ScoringService:
    def calculate(self, candidate, job):
        reasons = []

        score = 0.0

        # Skill overlap contributes up to 70 points.
        required = {skill.strip().lower() for skill in job.required_skills}
        candidate_skills = {skill.strip().lower() for skill in candidate.skills}

        if required:
            overlap = required.intersection(candidate_skills)
            skill_ratio = len(overlap) / len(required)
            score += skill_ratio * 70
            reasons.append(f"Skill eslesme orani: {skill_ratio:.2f}")
        else:
            score += 35
            reasons.append("Ilanda zorunlu yetenek tanimi yok, varsayilan puan verildi")

        # Experience contributes up to 30 points.
        min_exp = job.min_years_experience
        candidate_exp = candidate.years_experience
        if min_exp == 0:
            score += 30
            reasons.append("Minimum deneyim sarti yok")
        else:
            exp_ratio = min(candidate_exp / min_exp, 1.0)
            score += exp_ratio * 30
            reasons.append(f"Deneyim uygunluk orani: {exp_ratio:.2f}")

        return round(score, 2), reasons
