"""Populate the student portal database with repeatable demo data."""

from student_portal import Course, Student, create_app, db


def seed_database() -> None:
    """Insert demo courses and students when they do not already exist."""
    courses_by_name: dict[str, Course] = {}
    for name in ("Python", "Web Development"):
        course = db.session.execute(
            db.select(Course).where(Course.name == name)
        ).scalar_one_or_none()
        if course is None:
            course = Course(name=name)
            db.session.add(course)
        courses_by_name[name] = course

    demo_students = [
        ("Adham", "adham@example.com", "Python", [92.0, 88.0, 95.0]),
        ("Lina", "lina@example.com", "Web Development", [86.0, 91.0]),
    ]
    for name, email, course_name, grades in demo_students:
        existing = db.session.execute(
            db.select(Student).where(Student.email == email)
        ).scalar_one_or_none()
        if existing is None:
            db.session.add(
                Student(
                    name=name,
                    email=email,
                    course=courses_by_name[course_name],
                    grades=grades,
                )
            )

    db.session.commit()


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        seed_database()
        print("Demo data added successfully.")
