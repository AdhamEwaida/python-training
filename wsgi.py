"""Production WSGI entry point for the student portal."""

from student_portal import create_app

app = create_app()
