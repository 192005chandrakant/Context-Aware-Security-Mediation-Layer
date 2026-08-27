"""
CASML Backend — Core Configuration

Loads settings from environment variables / .env file.
"""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────
    app_name: str = "CASML"
    app_env: str = "development"
    debug: bool = True
    log_level: str = "DEBUG"

    # ── Database ─────────────────────────────────────────
    database_url: str = "postgresql+asyncpg://casml:casml_dev@localhost:5432/casml_db"
    database_url_sync: str = "postgresql://casml:casml_dev@localhost:5432/casml_db"

    # ── LLM ──────────────────────────────────────────────
    llm_provider: str = "openai"
    llm_api_key: str = "FAKE_API_KEY_001"
    model_name: str = "gpt-4o"

    # ── Security ─────────────────────────────────────────
    jwt_secret: str = "CHANGE_ME_IN_PRODUCTION"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60

    # ── CORS ─────────────────────────────────────────────
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    # ── Paths ────────────────────────────────────────────
    experiment_data_dir: str = "./experiments"
    dataset_dir: str = "./dataset"
    configs_dir: str = "../configs"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]


# Singleton instance
settings = Settings()
