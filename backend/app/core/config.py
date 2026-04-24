import os


class Settings:
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "sqlite+pysqlite:///./recruitment.db"
    )
    CV_STORAGE_DIR: str = os.getenv("CV_STORAGE_DIR", "backend/storage/cv")
    AUTO_INVITE_SCORE_THRESHOLD: float = float(
        os.getenv("AUTO_INVITE_SCORE_THRESHOLD", "70")
    )
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
    ACCESS_TOKEN_MAX_AGE_SECONDS: int = int(
        os.getenv("ACCESS_TOKEN_MAX_AGE_SECONDS", "86400")
    )
    REFRESH_TOKEN_MAX_AGE_SECONDS: int = int(
        os.getenv("REFRESH_TOKEN_MAX_AGE_SECONDS", "604800")
    )
    ADMIN_BOOTSTRAP_CODE: str = os.getenv(
        "ADMIN_BOOTSTRAP_CODE", "dev-bootstrap-code"
    )


settings = Settings()
