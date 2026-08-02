"""Command-line interface for the Week 1 student management project."""

from student_management.exporters import (
    StudentExportError,
    export_to_csv,
    export_to_json,
)
from student_management.manager import (
    DuplicateStudentError,
    StudentNotFoundError,
    StudentRegistry,
    StudentValidationError,
    list_top_students,
    register_student,
    update_grades,
)


def parse_grades(value: str) -> list[float]:
    """Convert comma-separated grade input to a list of numbers."""
    if not value.strip():
        return []
    try:
        return [float(grade.strip()) for grade in value.split(",")]
    except ValueError as error:
        raise StudentValidationError(
            "grades must be comma-separated numbers"
        ) from error


def _print_top_students(students: StudentRegistry) -> None:
    ranked_students = list_top_students(students)
    if not ranked_students:
        print("No students registered.")
        return

    for position, (student, average) in enumerate(ranked_students, start=1):
        print(f"{position}. {student['name']} ({student['id']}) - {average:.2f}")


def run_cli() -> int:
    """Run the in-memory student management menu."""
    students: StudentRegistry = {}

    while True:
        print("\nStudent Management System")
        print("1. Register student")
        print("2. Update grades")
        print("3. List top students")
        print("4. Export to JSON")
        print("5. Export to CSV")
        print("6. Exit")
        choice = input("Choose an option: ").strip()

        try:
            if choice == "1":
                register_student(
                    students,
                    input("Name: "),
                    input("Student ID: "),
                    input("Email: "),
                    parse_grades(input("Grades (comma-separated): ")),
                )
                print("Student registered.")
            elif choice == "2":
                update_grades(
                    students,
                    input("Student ID: "),
                    parse_grades(input("New grades (comma-separated): ")),
                )
                print("Grades updated.")
            elif choice == "3":
                _print_top_students(students)
            elif choice == "4":
                path = input("JSON file [students.json]: ").strip()
                export_to_json(students, path or "students.json")
                print("Students exported to JSON.")
            elif choice == "5":
                path = input("CSV file [students.csv]: ").strip()
                export_to_csv(students, path or "students.csv")
                print("Students exported to CSV.")
            elif choice == "6":
                print("Goodbye.")
                return 0
            else:
                print("Invalid option.")
        except (
            DuplicateStudentError,
            StudentExportError,
            StudentNotFoundError,
            StudentValidationError,
            TypeError,
        ) as error:
            print(f"Error: {error}")


if __name__ == "__main__":
    raise SystemExit(run_cli())
