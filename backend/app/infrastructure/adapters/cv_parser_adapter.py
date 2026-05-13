"""
CVParserAdapter — Structural: Adapter Pattern
===============================================
PyPDF kutuphanesini ICVParser arayuzune uyduran adaptor.
Dis kutuphanenin arayuzu ile sistemin bekledigi arayuz arasinda
kopru gorevi gorur.

Cok dilli destek: Turkce ve Ingilizce CV'leri isle.

Adapter Pattern sayesinde:
- PyPDF yerine baska bir PDF kutuphanesi kolayca takilabilir
- Test ortaminda mock adapter kullanilabilir
- Sistem, dis kutuphane degisikliklerinden izole kalir
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


class CVParserAdapter(ICVParser):
    """
    PyPDF → ICVParser Adaptor.

    Adaptee: PyPDF (PdfReader)
    Target: ICVParser arayuzu

    Cok dilli destek: Turkce ve Ingilizce CV'leri otomatik algilar ve isler.
    """

    # Genisletilmis yetenek sozlugu
    SKILL_DICTIONARY = {
        # Programlama dilleri
        "python", "java", "javascript", "typescript", "c#", "c++",
        "go", "rust", "ruby", "php", "swift", "kotlin", "scala", "r",
        "dart", "perl",
        # Frameworks
        "flask", "fastapi", "django", "spring", "react", "angular", "vue",
        "nodejs", "express", "flutter", "nextjs", "rails", "laravel",
        # Veritabanlari
        "sql", "postgresql", "mysql", "mongodb", "redis", "sqlite",
        "elasticsearch",
        # DevOps / Cloud
        "docker", "kubernetes", "aws", "azure", "gcp", "terraform",
        "jenkins", "gitlab", "github", "linux",
        # AI / ML
        "machine learning", "deep learning", "tensorflow", "pytorch",
        "pandas", "numpy", "opencv", "nlp", "spacy",
        # Diger
        "git", "rest api", "graphql", "microservices", "agile", "scrum",
        "figma", "firebase", "html", "css",
    }

    # Turkce → Ingilizce yetenek alias'lari (cok dilli destek)
    SKILL_ALIASES = {
        "yapay zeka": "machine learning",
        "derin ogrenme": "deep learning",
        "makine ogrenimi": "machine learning",
        "veri tabani": "sql",
        "veritabani": "sql",
        "veri bilimi": "data science",
        "web gelistirme": "web development",
        "mobil gelistirme": "mobile development",
    }

    # Egitim seviyesi tespiti (TR + EN)
    EDUCATION_PATTERNS = {
        "doktora": "doktora", "phd": "doktora", "ph.d": "doktora",
        "yuksek lisans": "yuksek_lisans", "yüksek lisans": "yuksek_lisans",
        "master": "yuksek_lisans", "msc": "yuksek_lisans", "m.sc": "yuksek_lisans",
        "lisans": "lisans", "bachelor": "lisans", "bsc": "lisans", "b.sc": "lisans",
        "on lisans": "on_lisans", "ön lisans": "on_lisans", "associate": "on_lisans",
        "lise": "lise", "high school": "lise",
    }

    # Dil algilama anahtar kelimeleri
    TURKISH_INDICATORS = {
        "deneyim", "yil", "yıl", "mezun", "universite", "üniversite",
        "egitim", "eğitim", "beceriler", "yetkinlikler", "is", "iş",
        "calisan", "çalışan", "proje", "gorev", "görev",
    }

    ENGLISH_INDICATORS = {
        "experience", "year", "university", "education", "skills",
        "qualifications", "work", "project", "responsibilities",
    }

    def parse_bytes(self, file_bytes: bytes) -> dict:
        """CV baytlarini parse ederek yapilandirilmis veri dondur."""
        text = self._extract_text(file_bytes)
        normalized = re.sub(r"\s+", " ", text).strip()
        summary = normalized[:600]

        # Dil algilama
        detected_lang = self._detect_language(normalized)

        # Beceri cikarimi
        words = {w.lower().strip(".,;:()[]{}") for w in normalized.split()}
        skills = self._extract_skills(words, normalized.lower())

        # Deneyim yili (cok dilli regex)
        years_experience = self._estimate_years_experience(normalized)

        # Egitim seviyesi
        education_level = self._detect_education(normalized.lower())

        return {
            "summary": summary,
            "skills": sorted(skills),
            "years_experience": years_experience,
            "education_level": education_level,
            "detected_language": detected_lang,
        }

    def save_cv(self, file_bytes: bytes, original_filename: str) -> str:
        """CV dosyasini diske kaydet."""
        storage_dir = Path(settings.CV_STORAGE_DIR)
        storage_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
        target_path = storage_dir / f"{timestamp}_{original_filename}"
        target_path.write_bytes(file_bytes)

        return str(target_path).replace("\\", "/")

    def _extract_text(self, file_bytes: bytes) -> str:
        """PyPDF adaptee — PDF'den metin cikarma."""
        try:
            reader = PdfReader(BytesIO(file_bytes))
            texts = []
            for page in reader.pages:
                texts.append(page.extract_text() or "")
            parsed = "\n".join(texts).strip()
            if parsed:
                return parsed
        except Exception:
            pass

        # Fallback for malformed PDFs used in development/testing.
        return file_bytes.decode("utf-8", errors="ignore")

    def _extract_skills(self, word_set: Set[str], full_text: str) -> List[str]:
        """Yetenek cikarimi — sozluk + alias eslestirme."""
        found = set()

        # Dogrudan eslestirme
        for skill in self.SKILL_DICTIONARY:
            if " " in skill:
                if skill in full_text:
                    found.add(skill)
            elif skill in word_set:
                found.add(skill)

        # Alias eslestirme (cok dilli)
        for alias, canonical in self.SKILL_ALIASES.items():
            if alias in full_text:
                found.add(canonical)

        return list(found)

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

        if all_matches:
            return max(int(m) for m in all_matches)

        # Tarih araligi tabanli tahmin (2018-2023 → 5 yil)
        year_ranges = re.findall(
            r"(20\d{2})\s*[-–—]\s*(20\d{2}|present|gunumuz|günümüz|halen|devam)",
            lower,
        )
        total = 0
        for start, end in year_ranges:
            if end.isdigit():
                total += max(0, int(end) - int(start))
            else:
                total += max(0, 2026 - int(start))

        return total

    def _detect_education(self, text: str) -> str:
        """Egitim seviyesi tespiti — cok dilli."""
        # Oncelikli siraya gore kontrol (doktora > master > lisans ...)
        priority_order = [
            "doktora", "phd", "ph.d",
            "yuksek lisans", "yüksek lisans", "master", "msc", "m.sc",
            "lisans", "bachelor", "bsc", "b.sc",
            "on lisans", "ön lisans", "associate",
            "lise", "high school",
        ]
        for keyword in priority_order:
            if keyword in text:
                return self.EDUCATION_PATTERNS[keyword]
        return "lisans"

    def _detect_language(self, text: str) -> str:
        """CV dilini algilar (tr/en/unknown)."""
        lower = text.lower()
        words = set(lower.split())

        tr_count = len(words.intersection(self.TURKISH_INDICATORS))
        en_count = len(words.intersection(self.ENGLISH_INDICATORS))

        if tr_count > en_count:
            return "tr"
        elif en_count > tr_count:
            return "en"
        return "unknown"
