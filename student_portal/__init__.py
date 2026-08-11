"""Application factory and public interface for the student portal."""

from typing import Any

from flask import Flask

from .config import Config
from .database import db, migrate
from .models import Course, Student
from .validation import validate_student_form


def create_app(test_config: dict[str, Any] | None = None) -> Flask:
    """Create and configure a student portal application instance."""
    app = Flask(__name__)
    app.config.from_object(Config)

    if test_config is not None:
        app.config.update(test_config)

    db.init_app(app)
    migrate.init_app(app, db)

    from .routes.courses import bp as courses_bp
    from .routes.main import bp as main_bp
    from .routes.students import bp as students_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(courses_bp)
    return app


__all__ = [
    "Course",
    "Student",
    "create_app",
    "db",
    "migrate",
    "validate_student_form",
]
