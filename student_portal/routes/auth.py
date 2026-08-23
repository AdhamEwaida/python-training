"""Account registration and session routes for the student portal."""

from urllib.parse import urlsplit

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from ..database import db
from ..models import User
from ..services import find_user_by_username

bp = Blueprint("auth", __name__)


def is_safe_next_url(next_url: str | None) -> bool:
    """Allow redirects only to local absolute paths."""
    if not next_url:
        return False
    target = urlsplit(next_url)
    return (
        not target.scheme
        and not target.netloc
        and target.path.startswith("/")
        and not target.path.startswith("//")
    )


@bp.route("/register", methods=["GET", "POST"])
def register() -> str:
    """Create a user account with a hashed password."""
    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        errors = []

        if len(username) < 3:
            errors.append("Username must contain at least 3 characters.")
        elif len(username) > 80:
            errors.append("Username must contain at most 80 characters.")

        if len(password) < 8:
            errors.append("Password must contain at least 8 characters.")

        if username and find_user_by_username(username) is not None:
            errors.append("That username is already registered.")

        if errors:
            for error in errors:
                flash(error, "error")
            return render_template("register_user.html", username=username), 400

        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("Account created. You can now log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register_user.html", username="")


@bp.route("/login", methods=["GET", "POST"])
def login() -> str:
    """Authenticate a user and start a Flask-Login session."""
    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = find_user_by_username(username)

        if user is None or not user.check_password(password):
            flash("Invalid username or password.", "error")
            return render_template("login.html", username=username), 401

        login_user(user)
        flash("You are now logged in.", "success")
        next_url = request.args.get("next")
        if is_safe_next_url(next_url):
            return redirect(next_url)
        return redirect(url_for("auth.dashboard"))

    return render_template("login.html", username="")


@bp.post("/logout")
@login_required
def logout() -> str:
    """End the current authenticated session."""
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.login"))


@bp.get("/dashboard")
@login_required
def dashboard() -> str:
    """Render a page available only to authenticated users."""
    return render_template("dashboard.html")
