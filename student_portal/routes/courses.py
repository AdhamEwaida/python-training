"""Course routes for the student portal."""

from flask import Blueprint, render_template

from ..database import db
from ..models import Course

bp = Blueprint("courses", __name__, url_prefix="/courses")


@bp.get("")
def course_list() -> str:
    """Render every course and its enrolled students."""
    courses = (
        db.session.execute(db.select(Course).order_by(Course.name)).scalars().all()
    )
    return render_template("courses.html", courses=courses)
