import pytest

from course import Course
from student import GraduateStudent, Student


def test_gpa_property_is_calculated_from_current_grades():
    student = Student("Adham", "S1", [90, 80])

    assert student.gpa == 85.0

    student.add_grade(100)

    assert student.gpa == 90.0


def test_gpa_property_cannot_be_assigned_directly():
    student = Student("Adham", "S1", [90])

    with pytest.raises(AttributeError):
        student.gpa = 100


def test_student_equality_uses_case_insensitive_student_id():
    first_student = Student("Adham", "S1", [90])
    same_id_student = GraduateStudent("Different Name", "s1", "Testing")
    different_student = Student("Adham", "S2", [90])

    assert first_student == same_id_student
    assert first_student != different_student
    assert first_student != "S1"


def test_course_supports_len_and_ordered_iteration():
    course = Course("CS301", "Advanced Python")
    first_student = Student("Adham", "S1")
    second_student = GraduateStudent("Lina", "G1", "Flask APIs")
    course.add_student(first_student)
    course.add_student(second_student)

    assert len(course) == 2
    assert list(course) == [first_student, second_student]
    assert [student.name for student in course] == ["Adham", "Lina"]


def test_course_iterator_uses_a_snapshot_of_enrollment():
    course = Course("CS301", "Advanced Python")
    first_student = Student("Adham", "S1")
    course.add_student(first_student)
    iterator = iter(course)

    course.add_student(Student("Lina", "S2"))

    assert list(iterator) == [first_student]
    assert len(course) == 2


def test_class_method_updates_and_validates_school_name(monkeypatch):
    monkeypatch.setattr(Student, "school_name", "Python Training School")

    Student.set_school_name("  Advanced Python Academy  ")

    assert Student.school_name == "Advanced Python Academy"

    with pytest.raises(ValueError, match="school name cannot be empty"):
        Student.set_school_name("   ")


def test_thesis_title_property_setter_cleans_and_validates_values():
    student = GraduateStudent("Adham", "G1", "Initial Thesis")

    student.thesis_title = "  Reliable APIs  "

    assert student.thesis_title == "Reliable APIs"
    assert student.get_thesis_title() == "Reliable APIs"

    with pytest.raises(ValueError, match="thesis title cannot be empty"):
        student.thesis_title = "   "
