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

    @classmethod
    def set_school_name(cls, school_name: str) -> None:
        """Set the shared school name for this class."""
        cls.school_name = cls._clean_text(school_name, "school name")

    def add_grade(self, grade: int | float) -> None:
        """Validate and append a grade."""
        self.grades.append(self._clean_grade(grade))

    def get_average(self) -> float:
        """Return the average grade, or zero when no grades exist."""
        if not self.grades:
            return 0.0
        return round(sum(self.grades) / len(self.grades), 2)

    @property
    def gpa(self) -> float:
        """Return the current grade average as an automatically calculated GPA."""
        return self.get_average()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Student):
            return NotImplemented
        return self.student_id.casefold() == other.student_id.casefold()

    def __str__(self) -> str:
        return f"{self.name} ({self.student_id}) - Average: {self.get_average():.2f}"

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(name={self.name!r}, "
            f"student_id={self.student_id!r}, grades={self.grades!r})"
        )


class GraduateStudent(Student):
    """Represent a graduate student with an associated thesis."""

    def __init__(
        self,
        name: str,
        student_id: str,
        thesis_title: str,
        grades: list[int | float] | None = None,
    ) -> None:
        super().__init__(name, student_id, grades)
        self.thesis_title = thesis_title

    @property
    def thesis_title(self) -> str:
        """Return the thesis title."""
        return self._thesis_title

    @thesis_title.setter
    def thesis_title(self, value: str) -> None:
        self._thesis_title = self._clean_text(value, "thesis title")

    def get_thesis_title(self) -> str:
        """Return the protected thesis title."""
        return self.thesis_title

    def __str__(self) -> str:
        return f"{super().__str__()} - Thesis: {self._thesis_title}"

    def __repr__(self) -> str:
        return (
            f"GraduateStudent(name={self.name!r}, "
            f"student_id={self.student_id!r}, "
            f"thesis_title={self._thesis_title!r}, grades={self.grades!r})"
        )
