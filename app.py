"""Flask entry point for the student portal."""

from student_portal import create_app

app = create_app()


if __name__ == "__main__":
    app.run()
