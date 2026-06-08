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
from typing import Dict, List, Set

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
        "yüksek lisans": "yuksek_lisans",
        "master": "yuksek_lisans",
        "msc": "yuksek_lisans",
        "lisans": "lisans",
        "bachelor": "lisans",
        "bsc": "lisans",
        "on lisans": "on_lisans",
        "ön lisans": "on_lisans",
        "associate": "on_lisans",
        "lise": "lise",
        "high school": "lise",
    }

    # ── CV Bolum Basliklari (TR / EN) ──
    SECTION_HEADINGS = {
        "work": {
            "is deneyimi", "iş deneyimi", "deneyim", "is tecrubesi", "iş tecrübesi",
            "work experience", "experience", "professional experience",
            "employment history", "work history", "kariyer", "career",
            "calisma gecmisi", "çalışma geçmişi",
        },
        "education": {
            "egitim", "eğitim", "egitim bilgileri", "eğitim bilgileri",
            "education", "academic background", "akademik gecmis",
            "akademik geçmiş", "okul bilgileri",
        },
        "projects": {
            "projeler", "projects", "kisisel projeler", "kişisel projeler",
            "personal projects", "side projects", "open source",
        },
        "skills": {
            "yetenekler", "beceriler", "teknik beceriler", "teknik yetenekler",
            "skills", "technical skills", "technologies", "teknolojiler",
        },
        "certifications": {
            "sertifikalar", "sertifika", "certifications", "certificates",
            "belgeler", "lisanslar", "licenses",
        },
    }

    # ── Sertifika Sozlugu ──
    CERTIFICATE_PATTERNS = {
        # Cloud sertifikalari
        r"aws\s+(?:certified|solutions?\s+architect|developer|sysops|cloud\s+practitioner)": "AWS Certified",
        r"aws\s+sertifika": "AWS Certified",
        r"azure\s+(?:fundamentals|administrator|developer|solutions?\s+architect)": "Azure Certified",
        r"az-\d{3}": "Azure Certified",
        r"google\s+cloud\s+(?:certified|professional|associate)": "GCP Certified",
        r"gcp\s+sertifika": "GCP Certified",
        # Proje yonetimi
        r"pmp": "PMP",
        r"project\s+management\s+professional": "PMP",
        r"prince2": "PRINCE2",
        # Agile / Scrum
        r"scrum\s+master": "Scrum Master",
        r"csm": "Scrum Master",
        r"psm\s*[i1]": "Scrum Master",
        r"product\s+owner": "Product Owner",
        r"cspo": "Product Owner",
        # Yazilim kalite
        r"istqb": "ISTQB",
        r"ctfl": "ISTQB",
        # Veri bilimi
        r"tensorflow\s+(?:developer\s+)?certificate": "TensorFlow Certified",
        r"databricks": "Databricks Certified",
        # Guvenlik
        r"cissp": "CISSP",
        r"ceh": "CEH",
        r"comptia\s+security": "CompTIA Security+",
        r"security\+": "CompTIA Security+",
        # Aglar
        r"ccna": "Cisco CCNA",
        r"ccnp": "Cisco CCNP",
        # Kubernetes
        r"cka": "CKA",
        r"ckad": "CKAD",
        r"certified\s+kubernetes": "CKA",
        # Genel
        r"itil": "ITIL",
        r"comptia\s+a\+": "CompTIA A+",
        r"oracle\s+certified": "Oracle Certified",
        r"java\s+se\s+\d+\s+(?:developer|programmer)": "Oracle Java Certified",
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

        # ── CV Bolum Algilama ──
        sections = self._detect_sections(text)

        # ── Deneyim yili (bolum bazli) ──
        years_experience = self._estimate_years_experience(text, sections)

        # ── Egitim seviyesi ──
        education_level = self._detect_education(text.lower())

        # ── Sertifika tespiti ──
        certifications = self._detect_certifications(text.lower())

        summary = text[:600]

        return {
            "summary": summary,
            "skills": sorted(skills),
            "years_experience": years_experience,
            "education_level": education_level,
            "certifications": certifications,
            "sections_found": list(sections.keys()),
            "entities": entities,
            "nlp_engine": "spacy",
        }

    def _parse_with_regex(self, text: str) -> dict:
        """Regex tabanlı fallback parse."""
        words = {w.lower().strip(".,;:()[]{}") for w in text.split()}
        skills = self._extract_skills(words, text.lower())
        sections = self._detect_sections(text)
        years_experience = self._estimate_years_experience(text, sections)
        education_level = self._detect_education(text.lower())
        certifications = self._detect_certifications(text.lower())

        return {
            "summary": text[:600],
            "skills": sorted(skills),
            "years_experience": years_experience,
            "education_level": education_level,
            "certifications": certifications,
            "sections_found": list(sections.keys()),
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

    def _detect_sections(self, text: str) -> Dict[str, str]:
        """
        CV metnini bolumlere ayir.

        Baslik satirlarini (buyuk harf veya bilinen anahtar kelimeler) tespit
        ederek metni 'work', 'education', 'projects', 'skills', 'certifications'
        gibi bolumlere ayirir.

        Returns:
            Dict[str, str]: bolum_adi -> bolum_metni
        """
        lower = text.lower()
        found_sections: Dict[str, tuple] = {}  # section_type -> (start_pos, heading)

        for section_type, headings in self.SECTION_HEADINGS.items():
            for heading in headings:
                # Baslik kelimesini bul (satir basinda veya : / - sonrasinda)
                patterns = [
                    rf"(?:^|\n)\s*{re.escape(heading)}\s*[:\-]?",
                    rf"(?:^|\n)\s*{re.escape(heading.upper())}\s*[:\-]?",
                ]
                for pat in patterns:
                    match = re.search(pat, lower)
                    if match:
                        pos = match.start()
                        # Ayni bolum tipinde daha once bulunan daha once geliyorsa onu koru
                        if section_type not in found_sections or pos < found_sections[section_type][0]:
                            found_sections[section_type] = (pos, heading)
                        break

        if not found_sections:
            return {}

        # Pozisyona gore sirala ve her bolumun metnini cikar
        sorted_sections = sorted(found_sections.items(), key=lambda x: x[1][0])
        result: Dict[str, str] = {}

        for i, (section_type, (start_pos, _heading)) in enumerate(sorted_sections):
            if i + 1 < len(sorted_sections):
                end_pos = sorted_sections[i + 1][1][0]
            else:
                end_pos = len(text)
            result[section_type] = text[start_pos:end_pos]

        return result

    def _estimate_years_experience(self, text: str, sections: Dict[str, str] = None) -> int:
        """
        Deneyim yili tahmini — bolum bazli + cok dilli regex.

        Eger CV bolumlere ayrildiysa, oncelikle 'work' bolumundeki
        tarih araliklarini kullanir. Bulunamazsa tam metin uzerinde
        egitim filtreli arama yapar.
        """
        lower = text.lower()

        # ── 1. Acik deneyim ifadeleri (en guvenilir) ──
        explicit_patterns = [
            r"(\d{1,2})\+?\s*(?:yil|yıl|year|years|yr)\s*(?:deneyim|experience|tecrube|tecrübe)",
            r"(?:deneyim|experience|tecrube|tecrübe)\s*[:.]?\s*(\d{1,2})\s*(?:yil|yıl|year|years|yr)?",
        ]
        explicit_matches = []
        for pattern in explicit_patterns:
            explicit_matches.extend(re.findall(pattern, lower))

        if explicit_matches:
            return max(int(m) for m in explicit_matches)

        # ── 2. Bolum bazli tarih araligi (en dogruluklu) ──
        if sections and "work" in sections:
            work_text = sections["work"].lower()
            work_years = self._extract_year_ranges(work_text)
            if work_years > 0:
                return work_years

        # ── 3. Genel "X yil/year" ifadeleri (egitim filtreli) ──
        general_patterns = [
            r"(\d{1,2})\+?\s*(?:yil|yıl|year|years|yr)",
            r"(\d{1,2})\+?\s*(?:yillik|yıllık|year's)",
        ]
        filtered_matches = []
        for pattern in general_patterns:
            for match in re.finditer(pattern, lower):
                start = max(0, match.start() - 60)
                end = min(len(lower), match.end() + 60)
                context = lower[start:end]

                is_education_context = any(
                    kw in context for kw in self.EDUCATION_CONTEXT_KEYWORDS
                )
                if not is_education_context:
                    filtered_matches.append(int(match.group(1)))

        if filtered_matches:
            return max(filtered_matches)

        # ── 4. Tarih araligi tahmini (egitim filtrelemeli — fallback) ──
        return self._extract_year_ranges(lower, filter_education=True)

    def _extract_year_ranges(self, text: str, filter_education: bool = False) -> int:
        """Tarih araliklarindan toplam yil hesapla."""
        year_range_pattern = r"(20\d{2})\s*[-–]\s*(20\d{2}|present|gunumuz|günümüz|halen|devam)"
        total = 0
        for match in re.finditer(year_range_pattern, text):
            if filter_education:
                start_pos = max(0, match.start() - 80)
                end_pos = min(len(text), match.end() + 80)
                context = text[start_pos:end_pos]
                if any(kw in context for kw in self.EDUCATION_CONTEXT_KEYWORDS):
                    continue

            start_year = int(match.group(1))
            end_raw = match.group(2)
            end_year = 2026 if end_raw in ("present", "gunumuz", "günümüz", "halen", "devam") else int(end_raw)
            total += max(0, end_year - start_year)

        return total

    def _detect_certifications(self, text: str) -> List[str]:
        """
        CV metninden sertifika tespiti.

        Bilinen sertifika pattern'lerini regex ile arar.
        Returns:
            Tespit edilen sertifika isimlerinin listesi
        """
        found = set()
        for pattern, cert_name in self.CERTIFICATE_PATTERNS.items():
            if re.search(pattern, text, re.IGNORECASE):
                found.add(cert_name)
        return sorted(found)

    def _detect_education(self, text: str) -> str:
        """Egitim seviyesi tespiti — cok dilli."""
        for keyword, level in self.EDUCATION_PATTERNS.items():
            if keyword in text:
                return level
        return "lisans"  # Varsayilan
