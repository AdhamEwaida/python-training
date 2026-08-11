"""Validation helpers for student registration form data."""

from math import isfinite
from typing import Any


def _parse_grades(value: str) -> tuple[list[float], str | None]:
    """Parse optional comma-separated grades between zero and one hundred."""
    if not value.strip():
        return [], None

    try:
        grades = [float(part.strip()) for part in value.split(",")]
    except ValueError:
        return [], "Grades must be comma-separated numbers."

    if any(not isfinite(grade) or grade < 0 or grade > 100 for grade in grades):
        return [], "Each grade must be between 0 and 100."

    return grades, None


def validate_student_form(
    name: str,
    email: str,
    course: str,
    grades_text: str,
) -> tuple[dict[str, str | list[float]], list[str]]:
    """Normalize submitted values and return data plus validation errors."""
    cleaned_name = name.strip()
    cleaned_email = email.strip()
    cleaned_course = course.strip()
    errors: list[str] = []

    if not cleaned_name:
        errors.append("Name is required.")
    if not cleaned_email or "@" not in cleaned_email:
        errors.append("A valid email is required.")
    if not cleaned_course:
        errors.append("Course is required.")

    grades, grade_error = _parse_grades(grades_text)
    if grade_error:
        errors.append(grade_error)

    return (
        {
            "name": cleaned_name,
            "email": cleaned_email,
            "course": cleaned_course,
            "grades": grades,
        },
        errors,
    )


def validate_student_payload(
    payload: object,
) -> tuple[dict[str, Any], list[str]]:
    """Normalize a JSON student payload and return data plus errors."""
    if not isinstance(payload, dict):
        return {}, ["Request body must be a JSON object."]

    errors: list[str] = []
    name = payload.get("name")
    email = payload.get("email")
    course = payload.get("course")
    raw_grades = payload.get("grades", [])

    if not isinstance(name, str):
        errors.append("Name must be a string.")
        cleaned_name = ""
    else:
        cleaned_name = name.strip()
        if not cleaned_name:
            errors.append("Name is required.")

    if not isinstance(email, str):
        errors.append("Email must be a string.")
        cleaned_email = ""
    else:
        cleaned_email = email.strip()
        if not cleaned_email or "@" not in cleaned_email:
            errors.append("A valid email is required.")

    if not isinstance(course, str):
        errors.append("Course must be a string.")
        cleaned_course = ""
    else:
        cleaned_course = course.strip()
        if not cleaned_course:
            errors.append("Course is required.")

    grades: list[float] = []
    if not isinstance(raw_grades, list):
        errors.append("Grades must be a list of numbers.")
    elif any(
        isinstance(grade, bool) or not isinstance(grade, (int, float))
        for grade in raw_grades
    ):
        errors.append("Grades must be a list of numbers.")
    else:
        grades = [float(grade) for grade in raw_grades]
        if any(not isfinite(grade) or grade < 0 or grade > 100 for grade in grades):
            errors.append("Each grade must be between 0 and 100.")

    return (
        {
            "name": cleaned_name,
            "email": cleaned_email,
            "course": cleaned_course,
            "grades": grades,
        },
        errors,
    )
