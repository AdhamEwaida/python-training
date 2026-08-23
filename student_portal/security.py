"""Small security helpers shared by server-rendered forms."""

import secrets

from flask import Flask, abort, request, session

UNSAFE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


def init_csrf_protection(app: Flask) -> None:
    """Protect non-API writes with a session-backed synchronizer token."""

    def csrf_token() -> str:
        token = session.get("_csrf_token")
        if token is None:
            token = secrets.token_urlsafe(32)
            session["_csrf_token"] = token
        return token

    app.jinja_env.globals["csrf_token"] = csrf_token

    @app.before_request
    def verify_csrf_token() -> None:
        if (
            not app.config.get("CSRF_ENABLED", True)
            or request.method not in UNSAFE_METHODS
            or request.blueprint == "api"
        ):
            return
        expected = session.get("_csrf_token")
        submitted = request.form.get("_csrf_token", "")
        if not expected or not secrets.compare_digest(expected, submitted):
            abort(400, description="The form security token is missing or invalid.")
