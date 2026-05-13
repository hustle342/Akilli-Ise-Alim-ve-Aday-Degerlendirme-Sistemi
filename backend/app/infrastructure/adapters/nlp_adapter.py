"""
NLP Adapter — Structural: Adapter Pattern
============================================
spaCy NLP pipeline ile gelismis CV parse islemi.
Lemmatization, Named Entity Recognition (NER), ve token analizi
yaparak daha dogruluklu beceri cikarimi saglar.

spaCy yuklu degilse fallback olarak CVParserAdapter kullanilir.
"""

import re
import logging
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from typing import List, Set

from pypdf import PdfReader

from app.core.interfaces.services import ICVParser
from app.infrastructure.config import settings

logger = logging.getLogger(__name__)

# spaCy opsiyonel bagimlilik
try:
    import spacy
    HAS_SPACY = True
except ImportError:
    HAS_SPACY = False
    spacy = None


class NLPParserAdapter(ICVParser):
    """
    spaCy NLP tabanlı CV parser adaptörü.

    Ozellikler:
    - Lemmatization: Kelimeleri kok haline getirir (calistim -> calis)
    - NER: Isim, kurum, tarih gibi varliklari tanir
    - Token analizi: POS tagging ile beceri cikarimi
    - Cok dilli destek: Turkce ve Ingilizce CV'leri isle

    spaCy yuklu degilse regex tabanlı fallback kullanilir.
    """

    # Genisletilmis yetenek sozlugu — NLP ile normalizasyon
    SKILL_DICTIONARY = {
        # Programlama dilleri
        "python", "java", "javascript", "typescript", "c#", "c++", "c",
        "go", "rust", "ruby", "php", "swift", "kotlin", "scala", "r",
        "dart", "perl", "lua", "haskell", "elixir",
        # Frameworks
        "flask", "fastapi", "django", "spring", "react", "angular", "vue",
        "nodejs", "express", "flutter", "nextjs", "nuxtjs", "rails",
        "laravel", "asp.net", "blazor",
        # Veritabanlari
        "sql", "postgresql", "mysql", "mongodb", "redis", "sqlite",
        "elasticsearch", "cassandra", "oracle", "mariadb",
        # DevOps / Cloud
        "docker", "kubernetes", "aws", "azure", "gcp", "terraform",
        "ansible", "jenkins", "gitlab", "github", "ci/cd", "linux",
        # AI / ML
        "machine learning", "deep learning", "tensorflow", "pytorch",
        "keras", "scikit-learn", "pandas", "numpy", "opencv",
        "nlp", "computer vision", "transformers", "spacy",
        # Diger
        "git", "rest api", "graphql", "microservices", "agile", "scrum",
        "jira", "figma", "firebase", "html", "css",
    }

    # Turkce — Ingilizce yetenek eslestirme (cok dilli destek)
    SKILL_ALIASES = {
        "yapay zeka": "machine learning",
        "derin ogrenme": "deep learning",
        "makine ogrenimi": "machine learning",
        "veri tabani": "sql",
        "veritabani": "sql",
        "bulut": "cloud",
        "konteyner": "docker",
        "sunucu": "linux",
        "mobil": "mobile",
    }

    # Egitim seviyeleri (TR / EN)
    EDUCATION_PATTERNS = {
        "doktora": "doktora",
        "phd": "doktora",
        "yuksek lisans": "yuksek_lisans",
        "master": "yuksek_lisans",
        "msc": "yuksek_lisans",
        "lisans": "lisans",
        "bachelor": "lisans",
        "bsc": "lisans",
        "on lisans": "on_lisans",
        "associate": "on_lisans",
        "lise": "lise",
        "high school": "lise",
    }

    def __init__(self):
        self._nlp = None
        if HAS_SPACY:
            try:
                # Turkce veya Ingilizce model yukle
                for model_name in ["tr_core_news_sm", "en_core_web_sm"]:
                    try:
                        self._nlp = spacy.load(model_name)
                        logger.info(f"[NLP] spaCy modeli yuklendi: {model_name}")
                        break
                    except OSError:
                        continue

                if self._nlp is None:
                    # Minimal pipeline olustur
                    self._nlp = spacy.blank("xx")  # multi-language
                    logger.info("[NLP] spaCy blank pipeline olusturuldu")
            except Exception as e:
                logger.warning(f"[NLP] spaCy baslatilamadi: {e}")
        else:
            logger.info("[NLP] spaCy yuklu degil, regex fallback kullanilacak")

    def parse_bytes(self, file_bytes: bytes) -> dict:
        """CV baytlarini parse ederek yapilandirilmis veri dondur."""
        text = self._extract_text(file_bytes)
        normalized = re.sub(r"\s+", " ", text).strip()

        if self._nlp is not None:
            return self._parse_with_nlp(normalized)
        return self._parse_with_regex(normalized)

    def save_cv(self, file_bytes: bytes, original_filename: str) -> str:
        """CV dosyasini diske kaydet."""
        storage_dir = Path(settings.CV_STORAGE_DIR)
        storage_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
        target_path = storage_dir / f"{timestamp}_{original_filename}"
        target_path.write_bytes(file_bytes)
        return str(target_path).replace("\\", "/")

    def _parse_with_nlp(self, text: str) -> dict:
        """spaCy NLP pipeline ile gelismis parse."""
        doc = self._nlp(text[:5000])  # Performans icin ilk 5000 karakter

        # ── Lemmatization ──
        lemmas = set()
        for token in doc:
            if not token.is_stop and not token.is_punct and len(token.text) > 1:
                lemma = token.lemma_.lower().strip()
                lemmas.add(lemma)
                lemmas.add(token.text.lower().strip())

        # ── NER: Isim, kurum, tarih cikar ──
        entities = {"persons": [], "organizations": [], "dates": []}
        for ent in doc.ents:
            if ent.label_ in ("PERSON", "PER"):
                entities["persons"].append(ent.text)
            elif ent.label_ in ("ORG", "ORGANIZATION"):
                entities["organizations"].append(ent.text)
            elif ent.label_ in ("DATE", "TIME"):
                entities["dates"].append(ent.text)

        # ── Beceri cikarimi (lemma + alias) ──
        skills = self._extract_skills(lemmas, text.lower())

        # ── Deneyim yili ──
        years_experience = self._estimate_years_experience(text)

        # ── Egitim seviyesi ──
        education_level = self._detect_education(text.lower())

        summary = text[:600]

        return {
            "summary": summary,
            "skills": sorted(skills),
            "years_experience": years_experience,
            "education_level": education_level,
            "entities": entities,
            "nlp_engine": "spacy",
        }

    def _parse_with_regex(self, text: str) -> dict:
        """Regex tabanlı fallback parse."""
        words = {w.lower().strip(".,;:()[]{}") for w in text.split()}
        skills = self._extract_skills(words, text.lower())
        years_experience = self._estimate_years_experience(text)
        education_level = self._detect_education(text.lower())

        return {
            "summary": text[:600],
            "skills": sorted(skills),
            "years_experience": years_experience,
            "education_level": education_level,
            "entities": {"persons": [], "organizations": [], "dates": []},
            "nlp_engine": "regex",
        }

    def _extract_skills(self, word_set: Set[str], full_text: str) -> List[str]:
        """Yetenek cikarimi — sozluk + alias eslestirme."""
        found = set()

        # Dogrudan eslestirme
        for skill in self.SKILL_DICTIONARY:
            if " " in skill:
                # Cok kelimeli yetenek (orn: "machine learning")
                if skill in full_text:
                    found.add(skill)
            elif skill in word_set:
                found.add(skill)

        # Alias eslestirme (cok dilli)
        for alias, canonical in self.SKILL_ALIASES.items():
            if alias in full_text:
                found.add(canonical)

        return list(found)

    def _extract_text(self, file_bytes: bytes) -> str:
        """PDF'den metin cikarma."""
        try:
            reader = PdfReader(BytesIO(file_bytes))
            texts = [page.extract_text() or "" for page in reader.pages]
            parsed = "\n".join(texts).strip()
            if parsed:
                return parsed
        except Exception:
            pass
        return file_bytes.decode("utf-8", errors="ignore")

    def _estimate_years_experience(self, text: str) -> int:
        """Deneyim yili tahmini — cok dilli regex."""
        lower = text.lower()
        # Turkce ve Ingilizce patternler
        patterns = [
            r"(\d{1,2})\+?\s*(?:yil|yıl|year|years|yr)",
            r"(\d{1,2})\+?\s*(?:yillik|yıllık|year's)",
            r"(?:deneyim|experience)\s*[:.]?\s*(\d{1,2})",
        ]
        all_matches = []
        for pattern in patterns:
            all_matches.extend(re.findall(pattern, lower))

        if not all_matches:
            # Tarih araligi tabanlı tahmin (2018-2023 → 5 yil)
            year_ranges = re.findall(r"(20\d{2})\s*[-–]\s*(20\d{2}|present|gunumuz|halen)", lower)
            total = 0
            for start, end in year_ranges:
                end_year = 2026 if end in ("present", "gunumuz", "halen") else int(end)
                total += max(0, end_year - int(start))
            return total

        return max(int(m) for m in all_matches)

    def _detect_education(self, text: str) -> str:
        """Egitim seviyesi tespiti — cok dilli."""
        for keyword, level in self.EDUCATION_PATTERNS.items():
            if keyword in text:
                return level
        return "lisans"  # Varsayilan
