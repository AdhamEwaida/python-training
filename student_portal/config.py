"""Configuration defaults for the student portal."""

import os


class Config:
    """Default application configuration."""

    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "dev-secret-key-change-in-production",
    )
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///student_portal.db",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
