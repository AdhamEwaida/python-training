"""Application factory and public interface for the student portal."""

from typing import Any

from flask import Flask, render_template

from .config import get_config, get_environment_overrides, validate_config
from .database import db, login_manager, migrate
from .models import Course, Enrollment, Student, User
from .security import init_csrf_protection
from .validation import validate_student_form, validate_student_payload


def create_app(test_config: dict[str, Any] | None = None) -> Flask:
    """Create and configure a student portal application instance."""
    app = Flask(__name__)
    app.config.from_object(get_config())
    app.config.update(get_environment_overrides())

    if test_config is not None:
        app.config.update(test_config)

    if app.testing and "CSRF_ENABLED" not in (test_config or {}):
        app.config["CSRF_ENABLED"] = False

    validate_config(app.config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    init_csrf_protection(app)

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

    from .cli import register_commands

    register_commands(app)

    @app.errorhandler(404)
    def not_found(error: Exception) -> tuple[str, int]:
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(error: Exception) -> tuple[str, int]:
        db.session.rollback()
        return render_template("errors/500.html"), 500

    return app


__all__ = [
    "Course",
    "Enrollment",
    "Student",
    "User",
    "create_app",
    "db",
    "login_manager",
    "migrate",
    "validate_student_form",
    "validate_student_payload",
]
