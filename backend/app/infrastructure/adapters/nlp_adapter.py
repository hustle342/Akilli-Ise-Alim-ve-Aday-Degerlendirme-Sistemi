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

    # Turkce — Ingilizce yetenek eslestirme + teknoloji synonym'lari
    SKILL_ALIASES = {
        # Turkce karsiliklari
        "yapay zeka": "machine learning",
        "derin ogrenme": "deep learning",
        "derin öğrenme": "deep learning",
        "makine ogrenimi": "machine learning",
        "makine öğrenimi": "machine learning",
        "veri tabani": "sql",
        "veritabani": "sql",
        "veri tabanı": "sql",
        "veritabanı": "sql",
        "bulut": "cloud",
        "konteyner": "docker",
        "sunucu": "linux",
        "mobil": "mobile",
        "yapay sinir agi": "deep learning",
        "yapay sinir ağı": "deep learning",
        "dogal dil isleme": "nlp",
        "doğal dil işleme": "nlp",
        # JavaScript varyasyonlari
        "js": "javascript",
        "es6": "javascript",
        "ecmascript": "javascript",
        "ts": "typescript",
        # Framework varyasyonlari
        "react.js": "react",
        "reactjs": "react",
        "react js": "react",
        "vue.js": "vue",
        "vuejs": "vue",
        "vue js": "vue",
        "angular.js": "angular",
        "angularjs": "angular",
        "next.js": "nextjs",
        "next js": "nextjs",
        "nuxt.js": "nuxtjs",
        "node.js": "nodejs",
        "node js": "nodejs",
        "node": "nodejs",
        "express.js": "express",
        "expressjs": "express",
        "ruby on rails": "rails",
        "asp.net core": "asp.net",
        "dotnet": "asp.net",
        ".net": "asp.net",
        "spring boot": "spring",
        "springboot": "spring",
        # Veritabani varyasyonlari
        "postgres": "postgresql",
        "postgre": "postgresql",
        "pg": "postgresql",
        "mongo": "mongodb",
        "mssql": "sql",
        "sql server": "sql",
        "maria": "mariadb",
        # DevOps varyasyonlari
        "k8s": "kubernetes",
        "kube": "kubernetes",
        "amazon web services": "aws",
        "google cloud": "gcp",
        "google cloud platform": "gcp",
        "microsoft azure": "azure",
        "ci cd": "ci/cd",
        "cicd": "ci/cd",
        "continuous integration": "ci/cd",
        "github actions": "ci/cd",
        "gitlab ci": "ci/cd",
        # AI/ML varyasyonlari
        "ml": "machine learning",
        "dl": "deep learning",
        "tf": "tensorflow",
        "sklearn": "scikit-learn",
        "sk-learn": "scikit-learn",
        "scikit learn": "scikit-learn",
        "cv": "computer vision",
        "goruntu isleme": "computer vision",
        "görüntü işleme": "computer vision",
        # Diger varyasyonlar
        "restful": "rest api",
        "rest": "rest api",
        "restful api": "rest api",
        "graphql api": "graphql",
        "mikro servis": "microservices",
        "mikroservis": "microservices",
        "micro service": "microservices",
    }

    # Beceri ailesi eslestirmesi — kismi eslestirme icin
    # Bir aday "postgresql" biliyorsa "sql" de kismen eslesmeli
    SKILL_FAMILIES = {
        "sql": {"postgresql", "mysql", "sqlite", "oracle", "mariadb", "sql"},
        "cloud": {"aws", "azure", "gcp"},
        "javascript": {"typescript", "javascript"},
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

    # Egitim baglami anahtar kelimeleri — deneyim hesabindan haric tutulacak
    EDUCATION_CONTEXT_KEYWORDS = {
        "egitim", "eğitim", "universite", "üniversite", "fakulte", "fakülte",
        "lisans", "on lisans", "ön lisans", "yuksek lisans", "yüksek lisans",
        "master", "doktora", "phd", "okul", "ogrenci", "öğrenci", "student",
        "mezun", "graduation", "university", "college", "school", "faculty",
        "bachelor", "degree", "diploma", "akademik", "academic", "bölüm",
        "bolum", "department", "muhendislik", "mühendislik", "engineering",
    }

    def _estimate_years_experience(self, text: str) -> int:
        """
        Deneyim yili tahmini — cok dilli regex.

        Egitim tarihlerini ve egitimle ilgili 'X yil' ifadelerini
        filtreler, sadece is deneyimini hesaba katar.
        """
        lower = text.lower()

        # ── 1. Acik deneyim ifadeleri (en guvenilir) ──
        # "3 yil deneyim", "5 years experience" gibi dogrudan ifadeler
        explicit_patterns = [
            r"(\d{1,2})\+?\s*(?:yil|yıl|year|years|yr)\s*(?:deneyim|experience|tecrube|tecrübe)",
            r"(?:deneyim|experience|tecrube|tecrübe)\s*[:.]?\s*(\d{1,2})\s*(?:yil|yıl|year|years|yr)?",
        ]
        explicit_matches = []
        for pattern in explicit_patterns:
            explicit_matches.extend(re.findall(pattern, lower))

        if explicit_matches:
            return max(int(m) for m in explicit_matches)

        # ── 2. Genel "X yil/year" ifadeleri (egitim filtreli) ──
        general_patterns = [
            r"(\d{1,2})\+?\s*(?:yil|yıl|year|years|yr)",
            r"(\d{1,2})\+?\s*(?:yillik|yıllık|year's)",
        ]
        filtered_matches = []
        for pattern in general_patterns:
            for match in re.finditer(pattern, lower):
                # Eslesmenin etrafindaki 60 karakterlik baglamı kontrol et
                start = max(0, match.start() - 60)
                end = min(len(lower), match.end() + 60)
                context = lower[start:end]

                # Egitim baglaminda mi kontrol et
                is_education_context = any(
                    kw in context for kw in self.EDUCATION_CONTEXT_KEYWORDS
                )
                if not is_education_context:
                    filtered_matches.append(int(match.group(1)))

        if filtered_matches:
            return max(filtered_matches)

        # ── 3. Tarih araligi tahmini (egitim filtrelemeli) ──
        # "2018-2023" gibi araliklari bul, egitim bolumleri haric tut
        year_range_pattern = r"(20\d{2})\s*[-–]\s*(20\d{2}|present|gunumuz|günümüz|halen|devam)"
        total = 0
        for match in re.finditer(year_range_pattern, lower):
            start_pos = max(0, match.start() - 80)
            end_pos = min(len(lower), match.end() + 80)
            context = lower[start_pos:end_pos]

            # Egitim baglamindaki tarih araligini atla
            is_education_context = any(
                kw in context for kw in self.EDUCATION_CONTEXT_KEYWORDS
            )
            if is_education_context:
                continue

            start_year = int(match.group(1))
            end_raw = match.group(2)
            end_year = 2026 if end_raw in ("present", "gunumuz", "günümüz", "halen", "devam") else int(end_raw)
            total += max(0, end_year - start_year)

        return total

    def _detect_education(self, text: str) -> str:
        """Egitim seviyesi tespiti — cok dilli."""
        for keyword, level in self.EDUCATION_PATTERNS.items():
            if keyword in text:
                return level
        return "lisans"  # Varsayilan
