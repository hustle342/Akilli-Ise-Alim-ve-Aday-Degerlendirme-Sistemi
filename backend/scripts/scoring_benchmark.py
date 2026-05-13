"""
Model Dogruluk Olcumleri ve Optimizasyonu
==========================================
Skorlama stratejilerinin dogrulugunu olcen benchmark scripti.
Onceden tanimli test senaryolari uzerinde her stratejiyi calistirir
ve precision, recall, F1 metrikleri uretir.

Kullanim:
  $env:PYTHONPATH='backend'; py backend/scripts/scoring_benchmark.py
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dataclasses import dataclass
from typing import List

from app.infrastructure.scoring.scoring_factory import ScoringFactory
from app.core.value_objects import CandidateProfile, JobRequirements


# ─────── Test Senaryolari ───────

@dataclass
class BenchmarkCase:
    """Tek bir test senaryosu."""
    name: str
    candidate: CandidateProfile
    job: JobRequirements
    expected_min: float   # Beklenen minimum skor
    expected_max: float   # Beklenen maksimum skor
    should_invite: bool   # Davet esigini (70) gecmeli mi?


BENCHMARK_CASES = [
    # ── Tam uyum (yuksek skor beklenir) ──
    BenchmarkCase(
        name="Tam uyum — Python Backend",
        candidate=CandidateProfile(
            name="Ali Yilmaz", years_experience=5,
            skills=["python", "flask", "sql", "docker"],
            education_level="lisans",
        ),
        job=JobRequirements(
            title="Backend Python Gelistirici",
            min_years_experience=3,
            required_skills=["python", "flask", "sql", "docker"],
        ),
        expected_min=90, expected_max=100, should_invite=True,
    ),
    # ── Kismi uyum ──
    BenchmarkCase(
        name="Kismi uyum — eksik yetenek",
        candidate=CandidateProfile(
            name="Fatma Sahin", years_experience=4,
            skills=["python", "django"],
            education_level="yuksek_lisans",
        ),
        job=JobRequirements(
            title="Backend Python Gelistirici",
            min_years_experience=3,
            required_skills=["python", "flask", "sql", "docker"],
        ),
        expected_min=40, expected_max=70, should_invite=False,
    ),
    # ── Deneyim eksikligi ──
    BenchmarkCase(
        name="Deneyim eksikligi — yeni mezun",
        candidate=CandidateProfile(
            name="Can Ozturk", years_experience=1,
            skills=["python", "flask", "sql", "docker"],
            education_level="lisans",
        ),
        job=JobRequirements(
            title="Senior Python Gelistirici",
            min_years_experience=5,
            required_skills=["python", "flask", "sql", "docker"],
        ),
        expected_min=70, expected_max=85, should_invite=True,
    ),
    # ── Uyumsuz aday ──
    BenchmarkCase(
        name="Uyumsuz aday — farkli alan",
        candidate=CandidateProfile(
            name="Zeynep Arslan", years_experience=2,
            skills=["flutter", "dart", "firebase"],
            education_level="lisans",
        ),
        job=JobRequirements(
            title="Backend Python Gelistirici",
            min_years_experience=3,
            required_skills=["python", "flask", "sql", "docker"],
        ),
        expected_min=0, expected_max=30, should_invite=False,
    ),
    # ── Asiri nitelikli ──
    BenchmarkCase(
        name="Asiri nitelikli aday",
        candidate=CandidateProfile(
            name="Emre Demir", years_experience=10,
            skills=["python", "flask", "sql", "docker", "kubernetes", "aws"],
            education_level="doktora",
        ),
        job=JobRequirements(
            title="Junior Python Gelistirici",
            min_years_experience=1,
            required_skills=["python", "flask"],
        ),
        expected_min=90, expected_max=100, should_invite=True,
    ),
    # ── Yetenek gereksizimi yok ──
    BenchmarkCase(
        name="Ilan yetenek gereksizimi yok",
        candidate=CandidateProfile(
            name="Test Aday", years_experience=3,
            skills=["python"],
            education_level="lisans",
        ),
        job=JobRequirements(
            title="Genel Pozisyon",
            min_years_experience=0,
            required_skills=[],
        ),
        expected_min=50, expected_max=100, should_invite=False,
    ),
]


# ─────── Metrikler ───────

def evaluate_strategy(strategy_name: str, cases: List[BenchmarkCase]) -> dict:
    """Bir stratejiyi tum test senaryolarinda degerlendir."""
    try:
        strategy = ScoringFactory.create(strategy_name)
    except (ValueError, NotImplementedError):
        return {"strategy": strategy_name, "error": "Strateji olusturulamadi"}

    results = []
    tp = fp = fn = tn = 0

    for case in cases:
        try:
            score, reasons = strategy.calculate(case.candidate, case.job)
        except NotImplementedError:
            return {"strategy": strategy_name, "error": "Strateji implemente edilmemis"}

        predicted_invite = score >= 70
        in_range = case.expected_min <= score <= case.expected_max

        # Confusion matrix
        if predicted_invite and case.should_invite:
            tp += 1
        elif predicted_invite and not case.should_invite:
            fp += 1
        elif not predicted_invite and case.should_invite:
            fn += 1
        else:
            tn += 1

        results.append({
            "name": case.name,
            "score": score,
            "expected_range": f"{case.expected_min}-{case.expected_max}",
            "in_range": in_range,
            "predicted_invite": predicted_invite,
            "expected_invite": case.should_invite,
            "correct": predicted_invite == case.should_invite,
            "reasons": reasons,
        })

    # Metrikler
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
    accuracy = (tp + tn) / len(cases) if cases else 0.0
    range_accuracy = sum(1 for r in results if r["in_range"]) / len(results) if results else 0.0

    return {
        "strategy": strategy_name,
        "version": strategy.get_version(),
        "total_cases": len(cases),
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
        "range_accuracy": round(range_accuracy, 4),
        "confusion_matrix": {"tp": tp, "fp": fp, "fn": fn, "tn": tn},
        "results": results,
    }


def run_benchmark():
    """Tum stratejileri benchmark'a tabi tut."""
    strategies = ScoringFactory.available_strategies()

    print("\n" + "=" * 70)
    print("   SKORLAMA STRATEJISI BENCHMARK RAPORU")
    print("=" * 70)

    for strategy_name in strategies:
        report = evaluate_strategy(strategy_name, BENCHMARK_CASES)

        if "error" in report:
            print(f"\n--- {strategy_name} ---")
            print(f"  HATA: {report['error']}\n")
            continue

        print(f"\n--- {report['strategy']} (version: {report['version']}) ---")
        print(f"  Toplam senaryo:    {report['total_cases']}")
        print(f"  Dogruluk:          {report['accuracy']:.2%}")
        print(f"  Precision:         {report['precision']:.2%}")
        print(f"  Recall:            {report['recall']:.2%}")
        print(f"  F1 Score:          {report['f1_score']:.2%}")
        print(f"  Aralik dogrulugu:  {report['range_accuracy']:.2%}")
        cm = report['confusion_matrix']
        print(f"  Confusion Matrix:  TP={cm['tp']} FP={cm['fp']} FN={cm['fn']} TN={cm['tn']}")
        print()

        for r in report["results"]:
            status = "[OK]" if r["correct"] else "[FAIL]"
            range_ok = "[IN]" if r["in_range"] else "[OUT]"
            print(f"    {status} {range_ok} {r['name']}")
            print(f"        Skor: {r['score']}  (beklenen: {r['expected_range']})")
            print(f"        Nedenler: {' | '.join(r['reasons'][:2])}")

    print("\n" + "=" * 70)
    print("   BENCHMARK TAMAMLANDI")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    run_benchmark()
