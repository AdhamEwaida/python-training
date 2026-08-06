"""Public interface for the school package."""

from school.course import Course
from school.professor import Professor
from school.student import GraduateStudent, Student

__all__ = ["Course", "GraduateStudent", "Professor", "Student"]
