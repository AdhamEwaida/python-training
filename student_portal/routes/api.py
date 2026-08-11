"""JSON REST API routes for student records."""

from typing import Any

from flask import Blueprint, Response, current_app, jsonify, request, url_for
from sqlalchemy.exc import SQLAlchemyError

from ..database import db
from ..models import Student
from ..services import find_student_by_email, get_or_create_course
from ..validation import validate_student_payload

bp = Blueprint("api", __name__, url_prefix="/api")


def student_to_dict(student: Student) -> dict[str, Any]:
    """Serialize a student and its course for a JSON response."""
    return {
        "id": student.id,
        "name": student.name,
        "email": student.email,
        "grades": student.grades,
        "average": student.average,
        "course": {
            "id": student.course.id,
            "name": student.course.name,
        },
    }


def error_response(
    message: str,
    status_code: int,
    *,
    details: list[str] | None = None,
) -> tuple[Response, int]:
    """Build a consistent JSON error response."""
    body: dict[str, Any] = {"error": message}
    if details:
        body["details"] = details
    return jsonify(body), status_code


@bp.errorhandler(SQLAlchemyError)
def handle_database_error(error: SQLAlchemyError) -> tuple[Response, int]:
    """Roll back failed database work and return JSON instead of HTML."""
    db.session.rollback()
    current_app.logger.error("Student API database error: %s", error)
    return error_response("Database operation failed.", 500)


@bp.get("/students")
def student_list() -> tuple[Response, int]:
    """Return all students ordered by name and ID."""
    students = (
        db.session.execute(db.select(Student).order_by(Student.name, Student.id))
        .scalars()
        .all()
    )
    return jsonify({"students": [student_to_dict(s) for s in students]}), 200


@bp.get("/students/<int:student_id>")
def student_detail(student_id: int) -> tuple[Response, int]:
    """Return one student or a JSON 404 response."""
    student = db.session.get(Student, student_id)
    if student is None:
        return error_response("Student not found.", 404)
    return jsonify(student_to_dict(student)), 200


@bp.post("/students")
def create_student() -> tuple[Response, int]:
    """Validate a JSON document and create a student."""
    form_data, errors = validate_student_payload(request.get_json(silent=True))
    if errors:
        return error_response("Validation failed.", 400, details=errors)

    email = str(form_data["email"])
    if find_student_by_email(email) is not None:
        return error_response(
            "Validation failed.",
            400,
            details=["A student with this email already exists."],
        )

    student = Student(
        name=str(form_data["name"]),
        email=email,
        course=get_or_create_course(str(form_data["course"])),
        grades=list(form_data["grades"]),
    )
    db.session.add(student)
    db.session.commit()

    response = jsonify(student_to_dict(student))
    response.headers["Location"] = url_for(
        "api.student_detail",
        student_id=student.id,
    )
    return response, 201


@bp.put("/students/<int:student_id>")
def update_student(student_id: int) -> tuple[Response, int]:
    """Replace one student's editable fields from a JSON document."""
    student = db.session.get(Student, student_id)
    if student is None:
        return error_response("Student not found.", 404)

    form_data, errors = validate_student_payload(request.get_json(silent=True))
    if errors:
        return error_response("Validation failed.", 400, details=errors)

    email = str(form_data["email"])
    if find_student_by_email(email, excluding_id=student.id) is not None:
        return error_response(
            "Validation failed.",
            400,
            details=["A student with this email already exists."],
        )

    student.name = str(form_data["name"])
    student.email = email
    student.course = get_or_create_course(str(form_data["course"]))
    student.grades = list(form_data["grades"])
    db.session.commit()
    return jsonify(student_to_dict(student)), 200


@bp.delete("/students/<int:student_id>")
def delete_student(student_id: int) -> tuple[Response, int]:
    """Delete one student and return an empty success response."""
    student = db.session.get(Student, student_id)
    if student is None:
        return error_response("Student not found.", 404)

    db.session.delete(student)
    db.session.commit()
    return Response(status=204), 204
