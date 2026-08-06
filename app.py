"""A minimal Flask application for the Day 11 training exercise."""

from flask import Flask
from markupsafe import escape

app = Flask(__name__)


@app.route("/", methods=["GET"])
def welcome() -> str:
    """Return the application welcome page."""
    return "<h1>Welcome to the Student Portal</h1>"


@app.route("/hello/<name>", methods=["GET"])
def hello(name: str) -> str:
    """Greet the visitor using the name supplied in the URL."""
    safe_name = escape(name)
    return f"<h1>Hello, {safe_name}!</h1>"


if __name__ == "__main__":
    app.run(debug=True)
