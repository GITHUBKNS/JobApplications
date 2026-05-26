"""Application configuration loaded from .env via pydantic-settings."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # LLM
    anthropic_api_key: str = ""
    openai_api_key: str = ""

    # Job search
    jsearch_api_key: str = ""
    adzuna_app_id: str = ""
    adzuna_api_key: str = ""

    # Email finding
    hunter_api_key: str = ""
    apollo_api_key: str = ""
    rocketreach_api_key: str = ""

    # Email verification
    neverbounce_api_key: str = ""
    zerobounce_api_key: str = ""

    # Company news
    tavily_api_key: str = ""
    serpapi_api_key: str = ""

    # Google Sheets
    google_service_account_file: str = "secrets/service_account.json"

    # Gmail OAuth2
    gmail_oauth_client_id: str = ""
    gmail_oauth_client_secret: str = ""
    gmail_token_path: str = "secrets/gmail_token.json"

    # LinkedIn
    linkedin_session_cookie: str = ""

    # Encryption
    fernet_key: str = ""

    # User defaults
    user_name: str = "Prasanth Konada"
    user_email: str = ""
    user_phone: str = ""
    user_location: str = "Newark, NJ"
    user_physical_address: str = ""
    daily_email_cap: int = 20
    max_email_cap: int = 40

    @property
    def service_account_path(self) -> Path:
        p = Path(self.google_service_account_file)
        if not p.is_absolute():
            p = PROJECT_ROOT / p
        return p

    @property
    def gmail_token_full_path(self) -> Path:
        p = Path(self.gmail_token_path)
        if not p.is_absolute():
            p = PROJECT_ROOT / p
        return p

    def has_key(self, name: str) -> bool:
        return bool(getattr(self, name, ""))

    def missing_keys(self, *names: str) -> list[str]:
        return [n for n in names if not self.has_key(n)]


_settings: Optional[Settings] = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
