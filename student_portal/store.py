"""In-memory student storage used by the Flask portal."""

from typing import TypedDict


class StudentRecord(TypedDict):
    """The data rendered by the student portal templates."""

    id: int
    name: str
    email: str
    course: str
    grades: list[float]


students: list[StudentRecord] = []


def add_student(
    name: str,
    email: str,
    course: str,
    grades: list[float],
) -> StudentRecord:
    """Create, store, and return a student with a stable numeric ID."""
    next_id = max((student["id"] for student in students), default=0) + 1
    student: StudentRecord = {
        "id": next_id,
        "name": name,
        "email": email,
        "course": course,
        "grades": grades.copy(),
    }
    students.append(student)
    return student


def find_student(student_id: int) -> StudentRecord | None:
    """Return a student by ID, or ``None`` when it does not exist."""
    return next(
        (student for student in students if student["id"] == student_id),
        None,
    )
