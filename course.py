"""Course model demonstrating composition with student objects."""

from collections.abc import Iterator

from student import Student


class Course:
    """Represent a course that contains enrolled students."""

    def __init__(self, code: str, title: str) -> None:
        self.code = self._clean_text(code, "course code")
        self.title = self._clean_text(title, "course title")
        self.__students: list[Student] = []

    @staticmethod
    def _clean_text(value: str, field_name: str) -> str:
        if not isinstance(value, str):
            raise TypeError(f"{field_name} must be a string")

        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValueError(f"{field_name} cannot be empty")
        return cleaned_value

    def add_student(self, student: Student) -> None:
        """Enroll a student unless that student ID is already enrolled."""
        if not isinstance(student, Student):
            raise TypeError("student must be a Student instance")
        if any(
            enrolled.student_id.casefold() == student.student_id.casefold()
            for enrolled in self.__students
        ):
            raise ValueError(f"student {student.student_id!r} is already enrolled")
        self.__students.append(student)

    def remove_student(self, student_id: str) -> Student:
        """Remove and return the student matching an ID."""
        cleaned_id = self._clean_text(student_id, "student ID")
        for index, student in enumerate(self.__students):
            if student.student_id.casefold() == cleaned_id.casefold():
                return self.__students.pop(index)
        raise LookupError(f"student {cleaned_id!r} is not enrolled")

    def get_students(self) -> list[Student]:
        """Return a copy of the enrolled-student list."""
        return self.__students.copy()

    def has_student(self, student_id: str) -> bool:
        """Return whether a student ID is enrolled."""
        cleaned_id = self._clean_text(student_id, "student ID")
        return any(
            student.student_id.casefold() == cleaned_id.casefold()
            for student in self.__students
        )

    def __str__(self) -> str:
        student_count = len(self.__students)
        suffix = "" if student_count == 1 else "s"
        return f"{self.code} - {self.title} ({student_count} student{suffix})"

    def __len__(self) -> int:
        return len(self.__students)

    def __iter__(self) -> Iterator[Student]:
        return iter(self.__students.copy())
