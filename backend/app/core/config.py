import os
from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "ReqLint API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./reqlint.db")
    
    # Redis & Queue
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    AUDIT_EXECUTION_MODE: str = os.getenv("AUDIT_EXECUTION_MODE", "inline")  # inline | celery

    # JWT Authentication
    JWT_SECRET: str = os.getenv("JWT_SECRET", "super-secret-key-change-in-production-reqlint-hs256")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRE_HOURS: int = int(os.getenv("JWT_EXPIRE_HOURS", "24"))
    BCRYPT_ROUNDS: int = int(os.getenv("BCRYPT_ROUNDS", "12"))

    # File & Content Limits
    MAX_UPLOAD_MB: int = int(os.getenv("MAX_UPLOAD_MB", "10"))
    MAX_TEXT_CHARS: int = int(os.getenv("MAX_TEXT_CHARS", "50000"))
    TEMP_DIR: str = os.getenv("TEMP_DIR", "./storage/cache")
    TEMP_TTL_MINUTES: int = int(os.getenv("TEMP_TTL_MINUTES", "60"))

    # SLM (Stage 2)
    SLM_PROVIDER: str = os.getenv("SLM_PROVIDER", "mock")  # mock | ollama | openai_compatible
    SLM_BASE_URL: str = os.getenv("SLM_BASE_URL", "http://localhost:11434")
    SLM_MODEL: str = os.getenv("SLM_MODEL", "phi3:mini")
    SLM_TIMEOUT_SECONDS: int = int(os.getenv("SLM_TIMEOUT_SECONDS", "4"))
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

    # CORS
    # Union annotation: a plain comma-separated string env value is passed through to the
    # "before" validator below instead of failing JSON decoding (pydantic-settings >= 2.7).
    CORS_ORIGINS: Union[List[str], str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    @field_validator("CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        extra="allow"
    )

settings = Settings()
