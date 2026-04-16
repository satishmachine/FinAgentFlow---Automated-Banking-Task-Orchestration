"""
Application configuration — loads settings from environment variables.

Uses Pydantic Settings for type-safe configuration management.
All sensitive values (API keys, secrets) are loaded from environment
variables or a `.env` file.
"""

from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
ARTIFACTS_DIR = DATA_DIR / "artifacts"
LOGS_DIR = DATA_DIR / "logs"


class Settings(BaseSettings):
    """Central application settings, sourced from env vars / .env file."""

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── App ────────────────────────────────────────────────────────────────
    app_name: str = "FinAgentFlow"
    app_version: str = "0.1.0"
    debug: bool = False

    # ── API Keys ──────────────────────────────────────────────────────────
    euri_api_key: Optional[str] = None

    # ── EuriAI Settings ───────────────────────────────────────────────────
    euri_model: str = "gpt-4.1-nano"
    euri_temperature: float = 0.3
    euri_max_tokens: int = 2048
    euri_retry_attempts: int = 3
    euri_retry_delay: float = 1.0  # seconds

    # ── FastAPI ───────────────────────────────────────────────────────────
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/api/v1"

    # ── Storage ───────────────────────────────────────────────────────────
    storage_backend: str = "local"  # "local" | "sqlite"
    sqlite_url: str = f"sqlite:///{BASE_DIR / 'data' / 'finagentflow.db'}"
    artifacts_dir: str = str(ARTIFACTS_DIR)

    # ── Logging ───────────────────────────────────────────────────────────
    log_level: str = "INFO"
    log_dir: str = str(LOGS_DIR)

    # ── Streamlit ─────────────────────────────────────────────────────────
    streamlit_port: int = 8501


# Singleton settings instance
settings = Settings()
