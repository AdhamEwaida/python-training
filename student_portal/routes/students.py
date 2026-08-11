"""Student CRUD routes for the student portal."""

from flask import Blueprint, abort, redirect, render_template, request, url_for

from ..database import db
from ..models import Student
from ..services import find_student_by_email, get_or_create_course
from ..validation import validate_student_form

bp = Blueprint("students", __name__, url_prefix="/students")


@bp.get("")
def student_list() -> str:
    """Render all students currently stored in the database."""
    students = (
        db.session.execute(db.select(Student).order_by(Student.name, Student.id))
        .scalars()
        .all()
    )
    return render_template("students.html", students=students)


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
