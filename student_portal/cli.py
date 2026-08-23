"""Flask CLI commands for repeatable local administration."""

from flask import Flask


def register_commands(app: Flask) -> None:
    """Attach portal commands to an application instance."""

    @app.cli.command("seed")
    def seed_command() -> None:
        """Insert or update the demonstration data."""
        from seed import seed_database

        seed_database()
        print("Demo data added successfully.")
