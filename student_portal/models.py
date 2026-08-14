"""SQLAlchemy models for the student portal."""

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from .database import db, login_manager


class User(UserMixin, db.Model):
    """A portal account authenticated with a username and password."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password: str) -> None:
        """Store a secure hash instead of the original password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Return whether a password matches the stored hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, username={self.username!r})"


@login_manager.user_loader
def load_user(user_id: str) -> User | None:
    """Reload the signed-in user from the ID stored in the session."""
    try:
        parsed_id = int(user_id)
    except (TypeError, ValueError):
        return None
    return db.session.get(User, parsed_id)


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
