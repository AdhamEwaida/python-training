"""Application factory and public interface for the student portal."""

from typing import Any

from flask import Flask

from .config import Config
from .database import db, login_manager, migrate
from .models import Course, Student, User
from .validation import validate_student_form, validate_student_payload


def create_app(test_config: dict[str, Any] | None = None) -> Flask:
    """Create and configure a student portal application instance."""
    app = Flask(__name__)
    app.config.from_object(Config)

    if test_config is not None:
        app.config.update(test_config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from .routes.auth import bp as auth_bp
    from .routes.api import bp as api_bp
    from .routes.courses import bp as courses_bp
    from .routes.main import bp as main_bp
    from .routes.students import bp as students_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(courses_bp)
    return app


__all__ = [
    "Course",
    "Student",
    "User",
    "create_app",
    "db",
    "login_manager",
    "migrate",
    "validate_student_form",
    "validate_student_payload",
]
