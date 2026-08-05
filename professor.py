"""Professor model for assigning grades to students."""

from student import Student


class Professor:
    """Represent a professor with protected and private attributes."""

    def __init__(self, name: str, employee_id: str, department: str) -> None:
        self.name = self._clean_text(name, "name")
        self.__employee_id = self._clean_text(employee_id, "employee ID")
        self._department = self._clean_text(department, "department")

    @staticmethod
    def _clean_text(value: str, field_name: str) -> str:
        if not isinstance(value, str):
            raise TypeError(f"{field_name} must be a string")

        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValueError(f"{field_name} cannot be empty")
        return cleaned_value

    def get_employee_id(self) -> str:
        """Return the private employee identifier."""
        return self.__employee_id

    def get_department(self) -> str:
        """Return the protected department name."""
        return self._department

    def assign_grade(self, student: Student, grade: int | float) -> None:
        """Assign a validated grade to a student."""
        if not isinstance(student, Student):
            raise TypeError("student must be a Student instance")
        student.add_grade(grade)

    def __str__(self) -> str:
        return f"Professor {self.name} ({self._department})"
