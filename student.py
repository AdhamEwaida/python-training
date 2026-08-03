"""Object-oriented student model for Week 2."""

import math
from typing import ClassVar


class Student:
    """Represent a student and their grades."""

    school_name: ClassVar[str] = "Python Training School"

    def __init__(
        self,
        name: str,
        student_id: str,
        grades: list[int | float] | None = None,
    ) -> None:
        self.name = self._clean_text(name, "name")
        self.student_id = self._clean_text(student_id, "student ID")
        self.grades: list[float] = []

        if grades is not None:
            if not isinstance(grades, list):
                raise TypeError("grades must be a list")
            for grade in grades:
                self.add_grade(grade)

    @staticmethod
    def _clean_text(value: str, field_name: str) -> str:
        if not isinstance(value, str):
            raise TypeError(f"{field_name} must be a string")

        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValueError(f"{field_name} cannot be empty")
        return cleaned_value

    @staticmethod
    def _clean_grade(grade: int | float) -> float:
        if isinstance(grade, bool) or not isinstance(grade, (int, float)):
            raise TypeError("grade must be a number")
        if not math.isfinite(grade) or not 0 <= grade <= 100:
            raise ValueError("grade must be between 0 and 100")
        return float(grade)

    def add_grade(self, grade: int | float) -> None:
        """Validate and append a grade."""
        self.grades.append(self._clean_grade(grade))

    def get_average(self) -> float:
        """Return the average grade, or zero when no grades exist."""
        if not self.grades:
            return 0.0
        return round(sum(self.grades) / len(self.grades), 2)

    def __str__(self) -> str:
        return f"{self.name} ({self.student_id}) - Average: {self.get_average():.2f}"

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(name={self.name!r}, "
            f"student_id={self.student_id!r}, grades={self.grades!r})"
        )
