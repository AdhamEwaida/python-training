import csv
import json

import pytest

from student_management.exporters import export_to_csv, export_to_json
from student_management.manager import (
    DuplicateStudentError,
    StudentNotFoundError,
    StudentValidationError,
    calculate_average,
    get_student,
    list_top_students,
    register_student,
    update_grades,
)
from student_manager import parse_grades, run_cli


def test_register_student_stores_cleaned_data():
    students = {}

    result = register_student(
        students,
        "  Adham Ewaida ",
        " CS-101 ",
        " ADHAM@EXAMPLE.COM ",
        [90, 85.5],
    )

    assert result == {
        "id": "CS-101",
        "name": "Adham Ewaida",
        "email": "adham@example.com",
        "grades": [90.0, 85.5],
    }
    assert get_student(students, "cs-101") == result


def test_register_student_rejects_duplicate_id():
    students = {}
    register_student(students, "Adham", "S1", "adham@example.com")

    with pytest.raises(DuplicateStudentError):
        register_student(students, "Omar", "s1", "omar@example.com")


@pytest.mark.parametrize("email", ["missing-at.com", "a@b", "a b@example.com"])
def test_register_student_rejects_invalid_email(email):
    with pytest.raises(StudentValidationError, match="email is not valid"):
        register_student({}, "Adham", "S1", email)


@pytest.mark.parametrize("grades", [[-1], [101], [float("inf")], [float("nan")]])
def test_register_student_rejects_invalid_grade_values(grades):
    with pytest.raises(StudentValidationError):
        register_student({}, "Adham", "S1", "adham@example.com", grades)


@pytest.mark.parametrize("grades", [[True], ["90"], None, ()])
def test_update_grades_rejects_invalid_grade_types(grades):
    students = {}
    register_student(students, "Adham", "S1", "adham@example.com")

    with pytest.raises(TypeError):
        update_grades(students, "S1", grades)


def test_update_grades_replaces_existing_grades():
    students = {}
    register_student(students, "Adham", "S1", "adham@example.com", [60])

    updated_student = update_grades(students, "S1", [80, 90])

    assert updated_student["grades"] == [80.0, 90.0]
    assert calculate_average(updated_student) == 85.0


def test_update_grades_rejects_unknown_student():
    with pytest.raises(StudentNotFoundError):
        update_grades({}, "missing", [80])


def test_list_top_students_ranks_by_average_then_name():
    students = {}
    register_student(students, "Zaid", "S1", "zaid@example.com", [90])
    register_student(students, "Adam", "S2", "adam@example.com", [90])
    register_student(students, "Lina", "S3", "lina@example.com", [80])
    register_student(students, "No Grades", "S4", "none@example.com")

    ranking = list_top_students(students)

    assert [(student["name"], average) for student, average in ranking] == [
        ("Adam", 90.0),
        ("Zaid", 90.0),
        ("Lina", 80.0),
    ]


@pytest.mark.parametrize("limit", [0, -1])
def test_list_top_students_rejects_non_positive_limit(limit):
    with pytest.raises(StudentValidationError):
        list_top_students({}, limit)


def test_export_to_json_writes_student_records(tmp_path):
    students = {}
    register_student(students, "Adham", "S1", "adham@example.com", [90, 80])
    file_path = tmp_path / "exports" / "students.json"

    result = export_to_json(students, file_path)

    assert result == file_path
    exported_students = json.loads(file_path.read_text(encoding="utf-8"))
    assert exported_students[0]["id"] == "S1"
    assert exported_students[0]["grades"] == [90.0, 80.0]


def test_export_to_csv_writes_average_and_grades(tmp_path):
    students = {}
    register_student(students, "Adham", "S1", "adham@example.com", [90, 80])
    file_path = tmp_path / "students.csv"

    export_to_csv(students, file_path)

    with file_path.open(encoding="utf-8", newline="") as csv_file:
        rows = list(csv.DictReader(csv_file))
    assert rows == [
        {
            "id": "S1",
            "name": "Adham",
            "email": "adham@example.com",
            "grades": "90;80",
            "average": "85",
        }
    ]


def test_parse_grades_handles_values_and_empty_input():
    assert parse_grades("90, 80.5") == [90.0, 80.5]
    assert parse_grades("   ") == []


def test_parse_grades_rejects_invalid_input():
    with pytest.raises(StudentValidationError, match="comma-separated numbers"):
        parse_grades("90, excellent")


def test_cli_registers_lists_and_exits(monkeypatch, capsys):
    answers = iter(
        [
            "1",
            "Adham",
            "S1",
            "adham@example.com",
            "90,80",
            "3",
            "6",
        ]
    )
    monkeypatch.setattr("builtins.input", lambda _: next(answers))

    assert run_cli() == 0

    output = capsys.readouterr().out
    assert "Student registered." in output
    assert "1. Adham (S1) - 85.00" in output
    assert "Goodbye." in output
