"""Tests for environment-aware application configuration."""

import pytest

from student_portal import create_app
from student_portal.config import normalize_database_url


def clear_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Remove application settings inherited from the host shell."""
    for variable in ("APP_ENV", "DATABASE_URL", "SECRET_KEY"):
        monkeypatch.delenv(variable, raising=False)


def test_development_is_the_default_environment(monkeypatch):
    clear_environment(monkeypatch)

    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        }
    )

    assert app.config["APP_ENV"] == "development"
    assert app.debug is True
    assert app.config["SESSION_COOKIE_SECURE"] is False


def test_environment_variables_override_defaults(monkeypatch):
    clear_environment(monkeypatch)
    monkeypatch.setenv("SECRET_KEY", "environment-secret")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")

    app = create_app({"TESTING": True})

    assert app.config["SECRET_KEY"] == "environment-secret"
    assert app.config["SQLALCHEMY_DATABASE_URI"] == "sqlite:///:memory:"


def test_production_uses_secure_defaults(monkeypatch):
    clear_environment(monkeypatch)
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("SECRET_KEY", "production-secret")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")

    app = create_app({"TESTING": True})

    assert app.config["APP_ENV"] == "production"
    assert app.debug is False
    assert app.config["SESSION_COOKIE_SECURE"] is True
    assert app.config["SESSION_COOKIE_HTTPONLY"] is True


def test_production_rejects_default_secret(monkeypatch):
    clear_environment(monkeypatch)
    monkeypatch.setenv("APP_ENV", "production")

    with pytest.raises(RuntimeError, match="SECRET_KEY must be set"):
        create_app({"SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})


def test_unknown_environment_is_rejected(monkeypatch):
    clear_environment(monkeypatch)
    monkeypatch.setenv("APP_ENV", "staging")

    with pytest.raises(RuntimeError, match="Unsupported APP_ENV"):
        create_app()


def test_legacy_postgres_url_is_normalized():
    assert normalize_database_url("postgres://host/database") == (
        "postgresql://host/database"
    )
