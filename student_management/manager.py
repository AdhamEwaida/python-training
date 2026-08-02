"""Core operations for the student management system."""

import math
import re

Student = dict[str, object]
StudentRegistry = dict[str, Student]

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class StudentValidationError(ValueError):
    """Raised when student data is invalid."""


class DuplicateStudentError(StudentValidationError):
    """Raised when a student ID is already registered."""


class StudentNotFoundError(LookupError):
    """Raised when a student ID does not exist."""


def _clean_text(value: str, field_name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string")

    cleaned_value = value.strip()
    if not cleaned_value:
        raise StudentValidationError(f"{field_name} cannot be empty")

    return cleaned_value


def _clean_email(email: str) -> str:
    cleaned_email = _clean_text(email, "email").lower()
    if not EMAIL_PATTERN.fullmatch(cleaned_email):
        raise StudentValidationError("email is not valid")
    return cleaned_email


def _clean_grades(grades: list[int | float]) -> list[float]:
    if not isinstance(grades, list):
        raise TypeError("grades must be a list")

    cleaned_grades = []
    for grade in grades:
        if isinstance(grade, bool) or not isinstance(grade, (int, float)):
            raise TypeError("each grade must be a number")
        if not math.isfinite(grade) or not 0 <= grade <= 100:
            raise StudentValidationError("grades must be between 0 and 100")
        cleaned_grades.append(float(grade))

    return cleaned_grades


def _student_key(student_id: str) -> str:
    return _clean_text(student_id, "student ID").casefold()


def _copy_student(student: Student) -> Student:
    copied_student = student.copy()
    copied_student["grades"] = list(student["grades"])
    return copied_student


def register_student(
    students: StudentRegistry,
    name: str,
    student_id: str,
    email: str,
    grades: list[int | float] | None = None,
) -> Student:
    """Validate and register a new student."""
    cleaned_name = _clean_text(name, "name")
    cleaned_id = _clean_text(student_id, "student ID")
    student_key = cleaned_id.casefold()

    if student_key in students:
        raise DuplicateStudentError(f"student ID '{cleaned_id}' already exists")

    student = {
        "id": cleaned_id,
        "name": cleaned_name,
        "email": _clean_email(email),
        "grades": _clean_grades([] if grades is None else grades),
    }
    students[student_key] = student
    return _copy_student(student)


def get_student(students: StudentRegistry, student_id: str) -> Student:
    """Return a copy of a student record by ID."""
    student_key = _student_key(student_id)
    try:
        return _copy_student(students[student_key])
    except KeyError as error:
        raise StudentNotFoundError(
            f"student ID '{student_id.strip()}' was not found"
        ) from error


def update_grades(
    students: StudentRegistry, student_id: str, grades: list[int | float]
) -> Student:
    """Replace a student's grades and return the updated record."""
    student_key = _student_key(student_id)
    if student_key not in students:
        raise StudentNotFoundError(f"student ID '{student_id.strip()}' was not found")

    students[student_key]["grades"] = _clean_grades(grades)
    return _copy_student(students[student_key])


def calculate_average(student: Student) -> float:
    """Calculate a student's average, returning zero when no grades exist."""
    grades = student["grades"]
    if not grades:
        return 0.0
    return round(sum(grades) / len(grades), 2)


def list_top_students(
    students: StudentRegistry, limit: int = 3
) -> list[tuple[Student, float]]:
    """Return students ranked by average grade, then name."""
    if isinstance(limit, bool) or not isinstance(limit, int):
        raise TypeError("limit must be an integer")
    if limit <= 0:
        raise StudentValidationError("limit must be greater than zero")

    ranked_students = sorted(
        students.values(),
        key=lambda student: (
            -calculate_average(student),
            str(student["name"]).casefold(),
        ),
    )
    return [
        (_copy_student(student), calculate_average(student))
        for student in ranked_students[:limit]
    ]
