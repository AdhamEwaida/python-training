"""Student CRUD and profile routes for the student portal."""

import secrets
from pathlib import Path

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from sqlalchemy import or_
from werkzeug.utils import secure_filename

from ..database import db
from ..models import Course, Student
from ..services import find_student_by_email, get_or_create_course
from ..validation import validate_student_form

bp = Blueprint("students", __name__, url_prefix="/students")


@bp.get("")
def student_list() -> str:
    """Render a searchable, paginated list of students."""
    query = request.args.get("q", "").strip()
    page = request.args.get("page", 1, type=int)
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
        per_page=10,
        error_out=False,
    )
    return render_template(
        "students.html",
        students=pagination.items,
        pagination=pagination,
        query=query,
    )


@bp.get("/<int:student_id>")
def student_detail(student_id: int) -> str:
    """Render one student's details and grades."""
    student = db.session.get(Student, student_id)
    if student is None:
        abort(404)

    return render_template(
        "student_detail.html",
        student=student,
        average=student.average,
    )


@bp.route("/register", methods=["GET", "POST"])
def register_student() -> str:
    """Display and process the student registration form."""
    if request.method == "POST":
        form_data, errors = validate_student_form(
            request.form.get("name", ""),
            request.form.get("email", ""),
            request.form.get("course", ""),
            request.form.get("grades", ""),
        )

        email = str(form_data["email"])
        existing_student = find_student_by_email(email)
        if existing_student is not None:
            errors.append("A student with this email already exists.")

        if errors:
            return (
                render_template(
                    "register.html",
                    errors=errors,
                    form=request.form,
                    page_title="Register a Student",
                    submit_label="Register",
                ),
                400,
            )

        course = get_or_create_course(str(form_data["course"]))
        student = Student(
            name=str(form_data["name"]),
            email=email,
            course=course,
            grades=list(form_data["grades"]),
        )
        db.session.add(student)
        db.session.commit()
        return redirect(url_for("students.student_detail", student_id=student.id))

    return render_template(
        "register.html",
        errors=[],
        form={},
        page_title="Register a Student",
        submit_label="Register",
    )


@bp.route("/<int:student_id>/edit", methods=["GET", "POST"])
def edit_student(student_id: int) -> str:
    """Display and process the form for updating an existing student."""
    student = db.session.get(Student, student_id)
    if student is None:
        abort(404)

    if request.method == "POST":
        form_data, errors = validate_student_form(
            request.form.get("name", ""),
            request.form.get("email", ""),
            request.form.get("course", ""),
            request.form.get("grades", ""),
        )
        email = str(form_data["email"])
        duplicate = find_student_by_email(email, excluding_id=student.id)
        if duplicate is not None:
            errors.append("A student with this email already exists.")

        if errors:
            return (
                render_template(
                    "register.html",
                    errors=errors,
                    form=request.form,
                    page_title="Edit Student",
                    submit_label="Save Changes",
                ),
                400,
            )

        student.name = str(form_data["name"])
        student.email = email
        student.course = get_or_create_course(str(form_data["course"]))
        student.grades = list(form_data["grades"])
        db.session.commit()
        return redirect(url_for("students.student_detail", student_id=student.id))

    return render_template(
        "register.html",
        errors=[],
        form={
            "name": student.name,
            "email": student.email,
            "course": student.course.name,
            "grades": ", ".join(str(grade) for grade in student.grades),
        },
        page_title="Edit Student",
        submit_label="Save Changes",
    )


@bp.post("/<int:student_id>/delete")
def delete_student(student_id: int) -> str:
    """Delete one student from the database."""
    student = db.session.get(Student, student_id)
    if student is None:
        abort(404)

    db.session.delete(student)
    db.session.commit()
    return redirect(url_for("students.student_list"))


@bp.post("/<int:student_id>/profile-picture")
def upload_profile_picture(student_id: int) -> str:
    """Validate and store a student's profile image."""
    student = db.get_or_404(Student, student_id)
    upload = request.files.get("profile_picture")
    if upload is None or not upload.filename:
        flash("Choose an image to upload.", "error")
        return redirect(url_for("students.student_detail", student_id=student.id))

    safe_name = secure_filename(upload.filename)
    extension = Path(safe_name).suffix.lower()
    allowed = current_app.config["ALLOWED_IMAGE_EXTENSIONS"]
    if extension not in allowed or not (upload.mimetype or "").startswith("image/"):
        flash("Upload a PNG, JPEG, GIF, or WebP image.", "error")
        return redirect(url_for("students.student_detail", student_id=student.id))

    filename = f"student-{student.id}-{secrets.token_hex(8)}{extension}"
    upload_folder = Path(current_app.config["UPLOAD_FOLDER"])
    upload_folder.mkdir(parents=True, exist_ok=True)
    upload.save(upload_folder / filename)
    student.profile_picture = filename
    db.session.commit()
    flash("Profile picture updated successfully.", "success")
    return redirect(url_for("students.student_detail", student_id=student.id))


@bp.get("/profile-pictures/<path:filename>")
def profile_picture(filename: str):
    """Serve a generated profile-image filename from the upload directory."""
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)
