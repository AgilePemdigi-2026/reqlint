import logging
import os
import secrets
from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger("reqlint.config")

class Settings(BaseSettings):
    PROJECT_NAME: str = "ReqLint API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Runtime environment: 'dev' (default) or anything else ('production'/'staging').
    # P0/SEC-01: when ENV != 'dev', missing security configuration fails fast.
    ENV: str = os.getenv("ENV", "dev")

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./reqlint.db")
    
    # Redis & Queue
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    AUDIT_EXECUTION_MODE: str = os.getenv("AUDIT_EXECUTION_MODE", "inline")  # inline | celery

    # JWT Authentication
    # P0/SEC-01: no insecure default. In 'dev' a missing secret is replaced with an
    # ephemeral random per-process value (see validate_security_settings below);
    # in any other ENV a missing JWT_SECRET aborts startup.
    JWT_SECRET: str = os.getenv("JWT_SECRET", "")
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

# P0/SEC-01: nilai contoh yang diketahui publik tidak boleh dipakai di non-dev.
_INSECURE_KNOWN_SECRETS = {
    "ganti-ini-dengan-secret-acak-panjang",  # placeholder di backend/.env.example
}


def validate_security_settings(s: Settings) -> None:
    """
    P0/SEC-01 & DOC-04: fail fast when required security configuration is missing.

    - ENV == 'dev': a missing JWT_SECRET is replaced with an ephemeral random
      per-process value, so tokens are never signed with a publicly-known key.
    - ENV != 'dev' (production/staging): a missing JWT_SECRET — or one equal to
      a published example value — aborts startup instead of silently falling
      back to an insecure default.
    """
    if s.ENV != "dev" and s.JWT_SECRET in _INSECURE_KNOWN_SECRETS:
        raise RuntimeError(
            "JWT_SECRET still uses a published example value. "
            'Set a long random value, e.g. python -c "import secrets; print(secrets.token_hex(32))".'
        )
    if s.JWT_SECRET:
        return
    if s.ENV == "dev":
        s.JWT_SECRET = secrets.token_hex(32)
        # P0.1/R1-1: make the dev-only ephemeral secret impossible to miss.
        logger.warning(
            "ENV=dev: using an EPHEMERAL random JWT secret for this process. "
            "This is unsuitable for production, and tokens will NOT survive a "
            "process restart. For production, set ENV=production and a long "
            'random JWT_SECRET (e.g. python -c "import secrets; print(secrets.token_hex(32))").'
        )
    else:
        raise RuntimeError(
            "JWT_SECRET is required when ENV is not 'dev'. "
            'Set a long random value, e.g. python -c "import secrets; print(secrets.token_hex(32))".'
        )


validate_security_settings(settings)
