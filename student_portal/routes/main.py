"""Public pages and service health checks for the student portal."""

from flask import Blueprint, current_app, jsonify, render_template
from markupsafe import escape

bp = Blueprint("main", __name__)


@bp.get("/")
def welcome() -> str:
    """Return the application welcome page."""
    return render_template("index.html")


@bp.get("/hello/<name>")
def hello(name: str) -> str:
    """Greet the visitor using the name supplied in the URL."""
    return render_template("hello.html", name=escape(name))


@bp.get("/health")
def health():
    """Return a lightweight status document for deployment monitoring."""
    return jsonify(status="ok", environment=current_app.config["APP_ENV"])
