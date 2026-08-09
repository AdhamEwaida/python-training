"""SQLAlchemy models for the student portal."""

from .database import db


class Course(db.Model):
    """A course that can contain many students."""

    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    students = db.relationship(
        "Student",
        back_populates="course",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"Course(id={self.id!r}, name={self.name!r})"


class Student(db.Model):
    """A student persisted in the portal database."""

    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    grades = db.Column(db.JSON, nullable=False, default=list)
    course_id = db.Column(
        db.Integer,
        db.ForeignKey("courses.id"),
        nullable=False,
    )
    course = db.relationship("Course", back_populates="students")

    @property
    def average(self) -> float | None:
        """Return the average grade, or ``None`` when no grades exist."""
        return sum(self.grades) / len(self.grades) if self.grades else None

    def __repr__(self) -> str:
        return f"Student(id={self.id!r}, email={self.email!r})"
