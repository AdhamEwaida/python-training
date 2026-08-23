"""HTML CRUD routes for courses in the student portal."""

from flask import Blueprint, flash, redirect, render_template, request, url_for
from sqlalchemy import func

from ..database import db
from ..models import Course
from ..services import find_course

bp = Blueprint("courses", __name__, url_prefix="/courses")


@bp.get("")
def course_list() -> str:
    """Render a searchable, paginated course list."""
    query = request.args.get("q", "").strip()
    page = request.args.get("page", 1, type=int)
    statement = db.select(Course)
    if query:
        statement = statement.where(func.lower(Course.name).contains(query.lower()))
    pagination = db.paginate(
        statement.order_by(Course.name),
        page=page,
        per_page=10,
        error_out=False,
    )
    return render_template(
        "courses.html",
        courses=pagination.items,
        pagination=pagination,
        query=query,
    )


def validate_course_name(raw_name: str) -> tuple[str, list[str]]:
    """Normalize a course name and return any validation messages."""
    name = raw_name.strip()
    errors = []
    if not name:
        errors.append("Course name is required.")
    elif len(name) > 120:
        errors.append("Course name must contain at most 120 characters.")
    return name, errors


@bp.route("/new", methods=["GET", "POST"])
def create_course() -> str:
    """Create a course from an HTML form."""
    name = request.form.get("name", "")
    if request.method == "POST":
        normalized_name, errors = validate_course_name(name)
        if normalized_name and find_course(normalized_name) is not None:
            errors.append("A course with this name already exists.")
        if errors:
            return (
                render_template(
                    "course_form.html",
                    errors=errors,
                    name=name,
                    page_title="Add Course",
                ),
                400,
            )
        course = Course(name=normalized_name)
        db.session.add(course)
        db.session.commit()
        flash("Course added successfully.", "success")
        return redirect(url_for("courses.course_list"))
    return render_template(
        "course_form.html",
        errors=[],
        name="",
        page_title="Add Course",
    )


@bp.route("/<int:course_id>/edit", methods=["GET", "POST"])
def edit_course(course_id: int) -> str:
    """Update an existing course name."""
    course = db.get_or_404(Course, course_id)
    if request.method == "POST":
        name, errors = validate_course_name(request.form.get("name", ""))
        duplicate = find_course(name) if name else None
        if duplicate is not None and duplicate.id != course.id:
            errors.append("A course with this name already exists.")
        if errors:
            return (
                render_template(
                    "course_form.html",
                    errors=errors,
                    name=request.form.get("name", ""),
                    page_title="Edit Course",
                ),
                400,
            )
        course.name = name
        db.session.commit()
        flash("Course updated successfully.", "success")
        return redirect(url_for("courses.course_list"))
    return render_template(
        "course_form.html",
        errors=[],
        name=course.name,
        page_title="Edit Course",
    )


@bp.post("/<int:course_id>/delete")
def delete_course(course_id: int) -> str:
    """Delete an empty course while preserving enrolled students."""
    course = db.get_or_404(Course, course_id)
    if course.students or course.enrollments:
        flash("A course with enrolled students cannot be deleted.", "error")
        return redirect(url_for("courses.course_list"))
    db.session.delete(course)
    db.session.commit()
    flash("Course deleted successfully.", "success")
    return redirect(url_for("courses.course_list"))
