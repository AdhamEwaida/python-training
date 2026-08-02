"""JSON and CSV export functions for student records."""

import csv
import json
from pathlib import Path

from student_management.manager import StudentRegistry, calculate_average


class StudentExportError(OSError):
    """Raised when student records cannot be exported."""


def _ordered_students(students: StudentRegistry) -> list[dict[str, object]]:
    return sorted(students.values(), key=lambda student: str(student["id"]))


def export_to_json(students: StudentRegistry, file_path: str | Path) -> Path:
    """Export student records to a JSON file."""
    path = Path(file_path)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as json_file:
            json.dump(
                _ordered_students(students),
                json_file,
                indent=2,
                ensure_ascii=False,
            )
            json_file.write("\n")
    except OSError as error:
        raise StudentExportError(f"could not export students to {path}") from error
    return path


def export_to_csv(students: StudentRegistry, file_path: str | Path) -> Path:
    """Export student records to a CSV file."""
    path = Path(file_path)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as csv_file:
            writer = csv.DictWriter(
                csv_file,
                fieldnames=["id", "name", "email", "grades", "average"],
            )
            writer.writeheader()
            for student in _ordered_students(students):
                writer.writerow(
                    {
                        "id": student["id"],
                        "name": student["name"],
                        "email": student["email"],
                        "grades": ";".join(f"{grade:g}" for grade in student["grades"]),
                        "average": f"{calculate_average(student):g}",
                    }
                )
    except OSError as error:
        raise StudentExportError(f"could not export students to {path}") from error
    return path
