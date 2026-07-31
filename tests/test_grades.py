import pytest

from grades import get_pass_fail_results, get_top_three_students, validate_grades


def test_get_top_three_students_returns_highest_grades_in_order():
    grades = {
        "Omar": 72,
        "Adham": 95,
        "Sara": 59,
        "Lina": 88,
        "Yousef": 81,
    }

    assert get_top_three_students(grades) == [
        ("Adham", 95),
        ("Lina", 88),
        ("Yousef", 81),
    ]


def test_get_top_three_students_breaks_ties_by_name():
    grades = {"Zaid": 90, "adam": 90, "Mona": 90, "Omar": 80}

    assert get_top_three_students(grades) == [
        ("adam", 90),
        ("Mona", 90),
        ("Zaid", 90),
    ]


def test_get_top_three_students_handles_fewer_than_three_students():
    assert get_top_three_students({"Adham": 95, "Lina": 88}) == [
        ("Adham", 95),
        ("Lina", 88),
    ]


def test_get_pass_fail_results_uses_default_passing_grade():
    grades = {"Adham": 95, "Lina": 60, "Omar": 59.9}

    assert get_pass_fail_results(grades) == {
        "Adham": "Pass",
        "Lina": "Pass",
        "Omar": "Fail",
    }


def test_get_pass_fail_results_accepts_custom_passing_grade():
    grades = {"Adham": 85, "Lina": 75}

    assert get_pass_fail_results(grades, passing_grade=80) == {
        "Adham": "Pass",
        "Lina": "Fail",
    }


@pytest.mark.parametrize(
    "grades",
    [
        {"Adham": -1},
        {"Adham": 101},
        {"Adham": float("inf")},
        {"Adham": float("nan")},
    ],
)
def test_validate_grades_rejects_out_of_range_or_non_finite_grades(grades):
    with pytest.raises(ValueError):
        validate_grades(grades)


@pytest.mark.parametrize(
    "grades",
    [
        {"Adham": "95"},
        {"Adham": None},
        {"Adham": True},
    ],
)
def test_validate_grades_rejects_non_numeric_grades(grades):
    with pytest.raises(TypeError):
        validate_grades(grades)


@pytest.mark.parametrize("student", ["", "   "])
def test_validate_grades_rejects_empty_student_names(student):
    with pytest.raises(ValueError):
        validate_grades({student: 90})


def test_validate_grades_rejects_non_string_student_names():
    with pytest.raises(TypeError):
        validate_grades({123: 90})


def test_validate_grades_rejects_non_mapping_input():
    with pytest.raises(TypeError):
        validate_grades([("Adham", 95)])


@pytest.mark.parametrize("passing_grade", [-1, 101, float("inf"), float("nan")])
def test_get_pass_fail_results_rejects_invalid_passing_grade(passing_grade):
    with pytest.raises(ValueError):
        get_pass_fail_results({"Adham": 95}, passing_grade)


@pytest.mark.parametrize("passing_grade", ["60", None, True])
def test_get_pass_fail_results_rejects_non_numeric_passing_grade(passing_grade):
    with pytest.raises(TypeError):
        get_pass_fail_results({"Adham": 95}, passing_grade)
