import pytest

from student import Student


def test_student_initializes_cleaned_instance_attributes():
    source_grades = [90, 80.5]

    student = Student("  Adham Ewaida  ", "  CS-101  ", source_grades)
    source_grades.append(70)

    assert student.name == "Adham Ewaida"
    assert student.student_id == "CS-101"
    assert student.grades == [90.0, 80.5]


def test_students_have_independent_grade_lists():
    first_student = Student("Adham", "S1")
    second_student = Student("Lina", "S2")

    first_student.add_grade(90)

    assert first_student.grades == [90.0]
    assert second_student.grades == []


def test_school_name_is_a_shared_class_variable():
    first_student = Student("Adham", "S1")
    second_student = Student("Lina", "S2")

    assert first_student.school_name == Student.school_name
    assert second_student.school_name == Student.school_name


def test_add_grade_updates_average():
    student = Student("Adham", "S1", [90, 80])

    student.add_grade(85.5)

    assert student.grades == [90.0, 80.0, 85.5]
    assert student.get_average() == 85.17


def test_student_without_grades_has_zero_average():
    assert Student("Adham", "S1").get_average() == 0.0


@pytest.mark.parametrize("field", ["name", "student_id"])
@pytest.mark.parametrize("value", ["", "   "])
def test_student_rejects_empty_text_attributes(field, value):
    arguments = {"name": "Adham", "student_id": "S1"}
    arguments[field] = value

    with pytest.raises(ValueError, match="cannot be empty"):
        Student(**arguments)


@pytest.mark.parametrize("field", ["name", "student_id"])
@pytest.mark.parametrize("value", [None, 123, True])
def test_student_rejects_non_string_text_attributes(field, value):
    arguments = {"name": "Adham", "student_id": "S1"}
    arguments[field] = value

    with pytest.raises(TypeError, match="must be a string"):
        Student(**arguments)


@pytest.mark.parametrize("grade", [-1, 101, float("inf"), float("nan")])
def test_student_rejects_out_of_range_or_non_finite_grades(grade):
    student = Student("Adham", "S1")

    with pytest.raises(ValueError, match="between 0 and 100"):
        student.add_grade(grade)


@pytest.mark.parametrize("grade", [True, "90", None])
def test_student_rejects_non_numeric_grades(grade):
    student = Student("Adham", "S1")

    with pytest.raises(TypeError, match="must be a number"):
        student.add_grade(grade)


def test_student_rejects_non_list_initial_grades():
    with pytest.raises(TypeError, match="grades must be a list"):
        Student("Adham", "S1", (90, 80))


def test_str_returns_a_readable_student_summary():
    student = Student("Adham", "S1", [90, 80])

    assert str(student) == "Adham (S1) - Average: 85.00"


def test_repr_returns_an_unambiguous_student_representation():
    student = Student("Adham", "S1", [90, 80])

    assert repr(student) == (
        "Student(name='Adham', student_id='S1', grades=[90.0, 80.0])"
    )
