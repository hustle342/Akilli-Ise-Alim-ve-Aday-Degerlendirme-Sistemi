import re
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path

from pypdf import PdfReader

from app.core.config import settings


class CVParserService:
    SKILL_DICTIONARY = {
        "python",
        "java",
        "c#",
        "c++",
        "sql",
        "postgresql",
        "redis",
        "docker",
        "flask",
        "fastapi",
        "django",
        "flutter",
        "dart",
        "react",
        "nodejs",
        "aws",
        "git",
    }

    def parse_bytes(self, file_bytes: bytes) -> dict:
        text = self._extract_text(file_bytes)
        normalized = re.sub(r"\s+", " ", text).strip()
        summary = normalized[:600]

        words = {w.lower().strip(".,;:()[]{}") for w in normalized.split()}
        skills = sorted([s for s in self.SKILL_DICTIONARY if s in words])

        years_experience = self._estimate_years_experience(normalized)

        return {
            "summary": summary,
            "skills": skills,
            "years_experience": years_experience,
        }

    def save_cv(self, file_bytes: bytes, original_filename: str) -> str:
        storage_dir = Path(settings.CV_STORAGE_DIR)
        storage_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
        target_path = storage_dir / f"{timestamp}_{original_filename}"
        target_path.write_bytes(file_bytes)

        return str(target_path).replace("\\", "/")

    def _extract_text(self, file_bytes: bytes) -> str:
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

    def _estimate_years_experience(self, text: str) -> int:
        matches = re.findall(r"(\d{1,2})\+?\s*(?:yil|year)", text.lower())
        if not matches:
            return 0
        return max(int(m) for m in matches)
