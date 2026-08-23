"""Environment-aware configuration for the student portal."""

import os
from pathlib import Path
from typing import Any, Mapping

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SECRET_KEY = "dev-secret-key-change-in-production"
DEFAULT_DATABASE_URL = "sqlite:///student_portal.db"

# Load local development settings when a .env file is present. Existing shell
# variables keep precedence, so deployment platforms can inject real secrets.
load_dotenv(PROJECT_ROOT / ".env")


def normalize_database_url(url: str) -> str:
    """Return a SQLAlchemy-compatible database URL."""
    if url.startswith("postgres://"):
        return f"postgresql://{url.removeprefix('postgres://')}"
    return url


class Config:
    """Shared application configuration."""

    APP_ENV = "development"
    SECRET_KEY = DEFAULT_SECRET_KEY
    SQLALCHEMY_DATABASE_URI = DEFAULT_DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    CSRF_ENABLED = True
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024
    UPLOAD_FOLDER = str(PROJECT_ROOT / "instance" / "uploads")
    ALLOWED_IMAGE_EXTENSIONS = {".gif", ".jpeg", ".jpg", ".png", ".webp"}


class DevelopmentConfig(Config):
    """Developer-friendly defaults for local work."""

    APP_ENV = "development"
    DEBUG = True


class ProductionConfig(Config):
    """Safer defaults for a production deployment."""

    APP_ENV = "production"
    DEBUG = False
    SESSION_COOKIE_SECURE = True


CONFIGURATIONS = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}


def get_config() -> type[Config]:
    """Select an application configuration using APP_ENV."""
    environment = os.environ.get("APP_ENV", "development").strip().lower()
    try:
        return CONFIGURATIONS[environment]
    except KeyError as error:
        expected = ", ".join(sorted(CONFIGURATIONS))
        raise RuntimeError(
            f"Unsupported APP_ENV {environment!r}; expected one of: {expected}."
        ) from error


def get_environment_overrides() -> dict[str, Any]:
    """Read settings that deployment platforms provide at runtime."""
    overrides: dict[str, Any] = {}
    secret_key = os.environ.get("SECRET_KEY")
    database_url = os.environ.get("DATABASE_URL")

    if secret_key:
        overrides["SECRET_KEY"] = secret_key
    if database_url:
        overrides["SQLALCHEMY_DATABASE_URI"] = normalize_database_url(database_url)
    return overrides


def validate_config(config: Mapping[str, Any]) -> None:
    """Reject unsafe production settings before the app starts."""
    if (
        config.get("APP_ENV") == "production"
        and config.get("SECRET_KEY") == DEFAULT_SECRET_KEY
    ):
        raise RuntimeError("SECRET_KEY must be set to a strong value in production.")
