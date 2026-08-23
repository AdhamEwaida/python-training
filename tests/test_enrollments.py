"""Day 22 tests for course relationships, filtering, and CLI seeding."""

import pytest

from student_portal import Course, Enrollment, Student, create_app, db


@pytest.fixture
def app():
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        }
    )
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def add_student_and_courses():
    primary = Course(name="Python")
    secondary = Course(name="Databases")
    student = Student(
        name="Adham",
        email="adham@example.com",
        grades=[],
        course=primary,
    )
    db.session.add_all([student, secondary])
    db.session.commit()
    return student, primary, secondary


def test_student_can_enroll_in_multiple_courses(client):
    student, primary, secondary = add_student_and_courses()

    first = client.post(
        f"/api/students/{student.id}/enrollments",
        json={"course_id": primary.id},
    )
    second = client.post(
        f"/api/students/{student.id}/enrollments",
        json={"course_id": secondary.id},
    )
    assert first.status_code == 201
    assert second.status_code == 201

    listed = client.get(f"/api/students/{student.id}/enrollments")
    assert {item["course"]["name"] for item in listed.json["enrollments"]} == {
        "Python",
        "Databases",
    }
    assert db.session.execute(db.select(Enrollment)).scalars().all()


def test_duplicate_enrollment_returns_conflict(client):
    student, primary, _ = add_student_and_courses()
    payload = {"course_id": primary.id}
    client.post(f"/api/students/{student.id}/enrollments", json=payload)

    response = client.post(
        f"/api/students/{student.id}/enrollments",
        json=payload,
    )
    assert response.status_code == 409


def test_enrollment_can_be_deleted(client):
    student, _, secondary = add_student_and_courses()
    db.session.add(Enrollment(student=student, course=secondary))
    db.session.commit()

    response = client.delete(f"/api/students/{student.id}/enrollments/{secondary.id}")
    assert response.status_code == 204
    assert db.session.execute(db.select(Enrollment)).scalar_one_or_none() is None


def test_course_collection_filters_and_paginates(client):
    db.session.add_all(Course(name=f"Python {number:02}") for number in range(12))
    db.session.add(Course(name="Databases"))
    db.session.commit()

    response = client.get("/api/courses?q=python&page=2&per_page=5")
    assert response.status_code == 200
    assert len(response.json["courses"]) == 5
    assert response.json["pagination"] == {
        "page": 2,
        "pages": 3,
        "per_page": 5,
        "total": 12,
    }


def test_flask_seed_command_is_repeatable(app):
    runner = app.test_cli_runner()
    assert runner.invoke(args=["seed"]).exit_code == 0
    assert runner.invoke(args=["seed"]).exit_code == 0
    assert len(db.session.execute(db.select(Student)).scalars().all()) == 2
    assert len(db.session.execute(db.select(Course)).scalars().all()) == 2
    assert len(db.session.execute(db.select(Enrollment)).scalars().all()) == 2
