import math
from collections.abc import Mapping

PASSING_GRADE = 60.0

STUDENT_GRADES = {
    "Adham": 95,
    "Lina": 88,
    "Omar": 72,
    "Sara": 59,
    "Yousef": 81,
}


def validate_grades(grades: Mapping[str, float]) -> None:
    """Validate student names and grades."""
    if not isinstance(grades, Mapping):
        raise TypeError("grades must be a mapping of student names to grades")

    for student, grade in grades.items():
        if not isinstance(student, str):
            raise TypeError("student names must be strings")

        if not student.strip():
            raise ValueError("student names cannot be empty")

        if isinstance(grade, bool) or not isinstance(grade, (int, float)):
            raise TypeError("grades must be numbers")

        if not math.isfinite(grade) or not 0 <= grade <= 100:
            raise ValueError("grades must be finite numbers between 0 and 100")


def get_top_three_students(
    grades: Mapping[str, float],
) -> list[tuple[str, float]]:
    """Return up to three students ordered by grade, then by name."""
    validate_grades(grades)
    return sorted(
        grades.items(),
        key=lambda student_grade: (
            -student_grade[1],
            student_grade[0].casefold(),
        ),
    )[:3]


def get_pass_fail_results(
    grades: Mapping[str, float], passing_grade: float = PASSING_GRADE
) -> dict[str, str]:
    """Transform student grades into pass/fail results."""
    validate_grades(grades)

    if isinstance(passing_grade, bool) or not isinstance(passing_grade, (int, float)):
        raise TypeError("passing grade must be a number")

    if not math.isfinite(passing_grade) or not 0 <= passing_grade <= 100:
        raise ValueError("passing grade must be between 0 and 100")

    return {
        student: "Pass" if grade >= passing_grade else "Fail"
        for student, grade in grades.items()
    }


def main() -> None:
    """Display the sample grade report."""
    print("Top students:")
    for position, (student, grade) in enumerate(
        get_top_three_students(STUDENT_GRADES), start=1
    ):
        print(f"{position}. {student}: {grade}")

    print("\nResults:")
    for student, result in get_pass_fail_results(STUDENT_GRADES).items():
        print(f"{student}: {result}")


if __name__ == "__main__":
    main()
