"""JSON REST API routes for student records."""

from typing import Any

from flask import Blueprint, Response, current_app, jsonify, request, url_for
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError

from ..database import db
from ..models import Course, Enrollment, Student, User
from ..services import (
    find_course,
    find_student_by_email,
    find_user_by_username,
    get_or_create_course,
)
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


def course_to_dict(course: Course) -> dict[str, Any]:
    """Serialize a course and its primary enrollment count."""
    return {
        "id": course.id,
        "name": course.name,
        "student_count": len(course.students),
        "enrollment_count": len(course.enrollments),
    }


def validate_course_payload(payload: Any) -> tuple[str, list[str]]:
    """Validate the JSON shape used by course write endpoints."""
    if not isinstance(payload, dict):
        return "", ["Request body must be a JSON object."]
    name = payload.get("name")
    if not isinstance(name, str) or not name.strip():
        return "", ["Course name must be a non-empty string."]
    name = name.strip()
    if len(name) > 120:
        return name, ["Course name must contain at most 120 characters."]
    return name, []


def user_to_dict(user: User) -> dict[str, Any]:
    """Serialize a user without exposing authentication secrets."""
    return {"id": user.id, "username": user.username}


def validate_user_payload(
    payload: Any,
    *,
    password_required: bool,
) -> tuple[dict[str, str], list[str]]:
    """Validate user account JSON for create and update operations."""
    if not isinstance(payload, dict):
        return {}, ["Request body must be a JSON object."]
    username = payload.get("username")
    password = payload.get("password")
    errors = []
    if not isinstance(username, str) or not 3 <= len(username.strip()) <= 80:
        errors.append("Username must contain between 3 and 80 characters.")
    if password_required and (not isinstance(password, str) or len(password) < 8):
        errors.append("Password must contain at least 8 characters.")
    elif password is not None and (not isinstance(password, str) or len(password) < 8):
        errors.append("Password must contain at least 8 characters.")
    return {
        "username": username.strip() if isinstance(username, str) else "",
        "password": password if isinstance(password, str) else "",
    }, errors


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
    """Return students, with optional search and pagination for the UI."""
    if not request.args:
        students = (
            db.session.execute(db.select(Student).order_by(Student.name, Student.id))
            .scalars()
            .all()
        )
        return jsonify({"students": [student_to_dict(s) for s in students]}), 200

    query = request.args.get("q", "").strip()
    page = max(request.args.get("page", 1, type=int), 1)
    per_page = min(max(request.args.get("per_page", 20, type=int), 1), 100)
    statement = db.select(Student).join(Student.course)
    if query:
        pattern = f"%{query}%"
        statement = statement.where(
            or_(
                Student.name.ilike(pattern),
                Student.email.ilike(pattern),
                Course.name.ilike(pattern),
            )
        )
    pagination = db.paginate(
        statement.order_by(Student.name, Student.id),
        page=page,
        per_page=per_page,
        error_out=False,
    )
    payload: dict[str, Any] = {
        "students": [student_to_dict(student) for student in pagination.items],
        "pagination": {
            "page": pagination.page,
            "pages": pagination.pages,
            "per_page": pagination.per_page,
            "total": pagination.total,
        },
    }
    return jsonify(payload), 200


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


@bp.get("/courses")
def course_list() -> tuple[Response, int]:
    """Return a filtered, paginated course collection."""
    query = request.args.get("q", "").strip()
    page = max(request.args.get("page", 1, type=int), 1)
    per_page = min(max(request.args.get("per_page", 20, type=int), 1), 100)
    statement = db.select(Course)
    if query:
        statement = statement.where(Course.name.ilike(f"%{query}%"))
    pagination = db.paginate(
        statement.order_by(Course.name),
        page=page,
        per_page=per_page,
        error_out=False,
    )
    return (
        jsonify(
            {
                "courses": [course_to_dict(course) for course in pagination.items],
                "pagination": {
                    "page": pagination.page,
                    "pages": pagination.pages,
                    "per_page": pagination.per_page,
                    "total": pagination.total,
                },
            }
        ),
        200,
    )


@bp.get("/courses/<int:course_id>")
def course_detail(course_id: int) -> tuple[Response, int]:
    """Return one course or a JSON 404 response."""
    course = db.session.get(Course, course_id)
    if course is None:
        return error_response("Course not found.", 404)
    return jsonify(course_to_dict(course)), 200


@bp.post("/courses")
def create_course() -> tuple[Response, int]:
    """Create a course from a JSON document."""
    name, errors = validate_course_payload(request.get_json(silent=True))
    if name and find_course(name) is not None:
        errors.append("A course with this name already exists.")
    if errors:
        return error_response("Validation failed.", 400, details=errors)
    course = Course(name=name)
    db.session.add(course)
    db.session.commit()
    response = jsonify(course_to_dict(course))
    response.headers["Location"] = url_for("api.course_detail", course_id=course.id)
    return response, 201


@bp.put("/courses/<int:course_id>")
def update_course(course_id: int) -> tuple[Response, int]:
    """Replace a course name from a JSON document."""
    course = db.session.get(Course, course_id)
    if course is None:
        return error_response("Course not found.", 404)
    name, errors = validate_course_payload(request.get_json(silent=True))
    duplicate = find_course(name) if name else None
    if duplicate is not None and duplicate.id != course.id:
        errors.append("A course with this name already exists.")
    if errors:
        return error_response("Validation failed.", 400, details=errors)
    course.name = name
    db.session.commit()
    return jsonify(course_to_dict(course)), 200


@bp.delete("/courses/<int:course_id>")
def delete_course(course_id: int) -> tuple[Response, int]:
    """Delete a course only when it has no primary students."""
    course = db.session.get(Course, course_id)
    if course is None:
        return error_response("Course not found.", 404)
    if course.students or course.enrollments:
        return error_response("Course has enrolled students.", 409)
    db.session.delete(course)
    db.session.commit()
    return Response(status=204), 204


def enrollment_to_dict(enrollment: Enrollment) -> dict[str, Any]:
    """Serialize a student-course enrollment."""
    return {
        "id": enrollment.id,
        "student_id": enrollment.student_id,
        "course": course_to_dict(enrollment.course),
        "enrolled_at": enrollment.enrolled_at.isoformat(),
    }


@bp.get("/students/<int:student_id>/enrollments")
def enrollment_list(student_id: int) -> tuple[Response, int]:
    """List a student's explicit course enrollments."""
    student = db.session.get(Student, student_id)
    if student is None:
        return error_response("Student not found.", 404)
    return (
        jsonify(
            {"enrollments": [enrollment_to_dict(item) for item in student.enrollments]}
        ),
        200,
    )


@bp.post("/students/<int:student_id>/enrollments")
def create_enrollment(student_id: int) -> tuple[Response, int]:
    """Enroll a student in a course identified by JSON `course_id`."""
    student = db.session.get(Student, student_id)
    if student is None:
        return error_response("Student not found.", 404)
    payload = request.get_json(silent=True)
    course_id = payload.get("course_id") if isinstance(payload, dict) else None
    if not isinstance(course_id, int):
        return error_response(
            "Validation failed.",
            400,
            details=["course_id must be an integer."],
        )
    course = db.session.get(Course, course_id)
    if course is None:
        return error_response("Course not found.", 404)
    duplicate = db.session.execute(
        db.select(Enrollment).where(
            Enrollment.student_id == student.id,
            Enrollment.course_id == course.id,
        )
    ).scalar_one_or_none()
    if duplicate is not None:
        return error_response("Student is already enrolled in this course.", 409)
    enrollment = Enrollment(student=student, course=course)
    db.session.add(enrollment)
    db.session.commit()
    response = jsonify(enrollment_to_dict(enrollment))
    response.headers["Location"] = url_for(
        "api.enrollment_list",
        student_id=student.id,
    )
    return response, 201


@bp.delete("/students/<int:student_id>/enrollments/<int:course_id>")
def delete_enrollment(student_id: int, course_id: int) -> tuple[Response, int]:
    """Remove one explicit student-course enrollment."""
    enrollment = db.session.execute(
        db.select(Enrollment).where(
            Enrollment.student_id == student_id,
            Enrollment.course_id == course_id,
        )
    ).scalar_one_or_none()
    if enrollment is None:
        return error_response("Enrollment not found.", 404)
    db.session.delete(enrollment)
    db.session.commit()
    return Response(status=204), 204


@bp.get("/users")
def user_list() -> tuple[Response, int]:
    """Return every user without password hashes."""
    users = db.session.execute(db.select(User).order_by(User.username)).scalars()
    return jsonify({"users": [user_to_dict(user) for user in users]}), 200


@bp.get("/users/<int:user_id>")
def user_detail(user_id: int) -> tuple[Response, int]:
    """Return one user or a JSON 404 response."""
    user = db.session.get(User, user_id)
    if user is None:
        return error_response("User not found.", 404)
    return jsonify(user_to_dict(user)), 200


@bp.post("/users")
def create_user() -> tuple[Response, int]:
    """Create a password-hashed user account from JSON."""
    data, errors = validate_user_payload(
        request.get_json(silent=True),
        password_required=True,
    )
    username = data.get("username", "")
    if username and find_user_by_username(username) is not None:
        errors.append("That username is already registered.")
    if errors:
        return error_response("Validation failed.", 400, details=errors)
    user = User(username=username)
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()
    response = jsonify(user_to_dict(user))
    response.headers["Location"] = url_for("api.user_detail", user_id=user.id)
    return response, 201


@bp.put("/users/<int:user_id>")
def update_user(user_id: int) -> tuple[Response, int]:
    """Update a username and optionally rotate its password."""
    user = db.session.get(User, user_id)
    if user is None:
        return error_response("User not found.", 404)
    data, errors = validate_user_payload(
        request.get_json(silent=True),
        password_required=False,
    )
    username = data.get("username", "")
    duplicate = (
        find_user_by_username(username, excluding_id=user.id) if username else None
    )
    if duplicate is not None:
        errors.append("That username is already registered.")
    if errors:
        return error_response("Validation failed.", 400, details=errors)
    user.username = username
    if data.get("password"):
        user.set_password(data["password"])
    db.session.commit()
    return jsonify(user_to_dict(user)), 200


@bp.delete("/users/<int:user_id>")
def delete_user(user_id: int) -> tuple[Response, int]:
    """Delete a portal account."""
    user = db.session.get(User, user_id)
    if user is None:
        return error_response("User not found.", 404)
    db.session.delete(user)
    db.session.commit()
    return Response(status=204), 204
