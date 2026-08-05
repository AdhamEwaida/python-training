import pytest

from course import Course
from professor import Professor
from student import GraduateStudent, Student


def test_graduate_student_inherits_student_behavior():
    student = GraduateStudent(
        "Adham",
        "G1",
        "Reliable Flask Applications",
        [90, 80],
    )

    student.add_grade(100)

    assert isinstance(student, Student)
    assert student.get_average() == 90.0
    assert student.get_thesis_title() == "Reliable Flask Applications"


def test_graduate_student_uses_super_and_overrides_string_methods():
    student = GraduateStudent("Adham", "G1", "  Python Testing  ", [90])

    assert str(student) == ("Adham (G1) - Average: 90.00 - Thesis: Python Testing")
    assert repr(student) == (
        "GraduateStudent(name='Adham', student_id='G1', "
        "thesis_title='Python Testing', grades=[90.0])"
    )


@pytest.mark.parametrize("thesis_title", ["", "   "])
def test_graduate_student_rejects_empty_thesis_titles(thesis_title):
    with pytest.raises(ValueError, match="thesis title cannot be empty"):
        GraduateStudent("Adham", "G1", thesis_title)


def test_professor_encapsulates_identifiers_and_assigns_grades():
    professor = Professor("  Lina  ", "  P-10  ", "  Computer Science  ")
    student = Student("Adham", "S1")

    professor.assign_grade(student, 92)

    assert professor.name == "Lina"
    assert professor.get_employee_id() == "P-10"
    assert professor.get_department() == "Computer Science"
    assert student.grades == [92.0]
    assert not hasattr(professor, "__employee_id")


def test_professor_can_assign_a_grade_to_a_graduate_student():
    professor = Professor("Lina", "P-10", "Computer Science")
    student = GraduateStudent("Adham", "G1", "Python Testing")

    professor.assign_grade(student, 88)

    assert student.grades == [88.0]


def test_professor_rejects_non_students_and_invalid_grades():
    professor = Professor("Lina", "P-10", "Computer Science")

    with pytest.raises(TypeError, match="Student instance"):
        professor.assign_grade("Adham", 90)

    with pytest.raises(ValueError, match="between 0 and 100"):
        professor.assign_grade(Student("Adham", "S1"), 101)


def test_course_composes_students_and_returns_a_defensive_list_copy():
    course = Course("  CS301  ", "  Advanced Python  ")
    student = Student("Adham", "S1")
    graduate = GraduateStudent("Lina", "G1", "Flask APIs")

    course.add_student(student)
    assert str(course) == "CS301 - Advanced Python (1 student)"

    course.add_student(graduate)
    returned_students = course.get_students()
    returned_students.clear()

    assert course.code == "CS301"
    assert course.title == "Advanced Python"
    assert course.get_students() == [student, graduate]
    assert course.has_student("s1") is True
    assert str(course) == "CS301 - Advanced Python (2 students)"


def test_course_rejects_duplicate_student_ids_case_insensitively():
    course = Course("CS301", "Advanced Python")
    course.add_student(Student("Adham", "S1"))

    with pytest.raises(ValueError, match="already enrolled"):
        course.add_student(Student("Another Student", "s1"))


def test_course_removes_students_by_id():
    course = Course("CS301", "Advanced Python")
    student = Student("Adham", "S1")
    course.add_student(student)

    removed_student = course.remove_student("s1")

    assert removed_student is student
    assert course.get_students() == []


def test_course_rejects_invalid_members_and_missing_student_ids():
    course = Course("CS301", "Advanced Python")

    with pytest.raises(TypeError, match="Student instance"):
        course.add_student("Adham")

    with pytest.raises(LookupError, match="is not enrolled"):
        course.remove_student("S1")
