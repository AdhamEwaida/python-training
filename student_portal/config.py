"""Configuration defaults for the student portal."""

import os


class Config:
    """Default application configuration."""

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///student_portal.db",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
