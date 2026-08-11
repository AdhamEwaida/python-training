"""Shared database queries and operations for student portal routes."""

from sqlalchemy import func

from .database import db
from .models import Course, Student


def find_course(name: str) -> Course | None:
    """Find a course by name without treating letter case as significant."""
    statement = db.select(Course).where(func.lower(Course.name) == name.lower())
    return db.session.execute(statement).scalar_one_or_none()


def get_or_create_course(name: str) -> Course:
    """Return an existing course or add a new one to the current session."""
    course = find_course(name)
    if course is None:
        course = Course(name=name)
        db.session.add(course)
    return course


def find_student_by_email(
    email: str,
    *,
    excluding_id: int | None = None,
) -> Student | None:
    """Find a student by email, optionally excluding one student ID."""
    statement = db.select(Student).where(func.lower(Student.email) == email.lower())
    if excluding_id is not None:
        statement = statement.where(Student.id != excluding_id)
    return db.session.execute(statement).scalar_one_or_none()
