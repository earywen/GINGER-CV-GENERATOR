# -*- coding: utf-8 -*-
from pathlib import Path
import shutil
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

BASE_DIR = Path(__file__).resolve().parent.parent.parent
APP_DIR = BASE_DIR / "app"
STATIC_DIR = APP_DIR / "static"
TEMPLATE_DIR = APP_DIR / "templates"
ASSETS_DIR = STATIC_DIR / "assets"
LOGO_PATH = ASSETS_DIR / "logo.png"

def _find_agy_binary() -> str:
    found = shutil.which("agy")
    if found:
        return found
    fallback = Path.home() / ".local" / "bin" / "agy"
    if fallback.exists():
        return str(fallback)
    return "agy"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    APP_TITLE: str = "Ginger Burgeap CV Generator 2026"
    APP_VERSION: str = "1.0.0"
    HOST: str = "0.0.0.0"
    PORT: int = 8085
    LOG_LEVEL: str = "INFO"

    CORS_ORIGINS: List[str] = Field(default_factory=lambda: ["*"])

    # agy CLI configuration (authenticated via Google OAuth / Google Pro)
    AGY_BIN_PATH: str = Field(default_factory=_find_agy_binary)
    AGY_MODEL: str = "gemini-3.8-flash-low"
    AGY_EFFORT: str = "low"
    AGY_TIMEOUT_SECONDS: int = 180

    # Default corporate values
    DEFAULT_AGENCY: str = "RÉGION NORD-OUEST"

    # Job cleanup
    JOB_EXPIRATION_SECONDS: int = 1800
    JOB_MAX_STORED: int = 200

settings = Settings()
