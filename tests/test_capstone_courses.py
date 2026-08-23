"""Day 19 tests for course CRUD and student discovery."""

import pytest

from student_portal import Course, Student, create_app, db


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


def test_html_course_crud(client):
    created = client.post("/courses/new", data={"name": "Databases"})
    assert created.status_code == 302
    course = db.session.execute(db.select(Course)).scalar_one()

    updated = client.post(
        f"/courses/{course.id}/edit",
        data={"name": "Advanced Databases"},
        follow_redirects=True,
    )
    assert updated.status_code == 200
    assert b"Advanced Databases" in updated.data

    deleted = client.post(f"/courses/{course.id}/delete")
    assert deleted.status_code == 302
    assert db.session.get(Course, course.id) is None


def test_course_api_crud(client):
    created = client.post("/api/courses", json={"name": "Flask"})
    assert created.status_code == 201
    course_id = created.json["id"]
    assert created.headers["Location"] == f"/api/courses/{course_id}"

    listed = client.get("/api/courses")
    assert listed.json["courses"][0]["student_count"] == 0

    updated = client.put(f"/api/courses/{course_id}", json={"name": "Flask API"})
    assert updated.status_code == 200
    assert updated.json["name"] == "Flask API"

    deleted = client.delete(f"/api/courses/{course_id}")
    assert deleted.status_code == 204


def test_course_delete_rejects_enrolled_students(client):
    course = Course(name="Python")
    db.session.add(
        Student(
            name="Adham",
            email="adham@example.com",
            grades=[],
            course=course,
        )
    )
    db.session.commit()

    response = client.delete(f"/api/courses/{course.id}")
    assert response.status_code == 409
    assert response.json == {"error": "Course has enrolled students."}


def test_student_search_matches_course_name(client):
    course = Course(name="Machine Learning")
    db.session.add_all(
        [
            Student(
                name="Adham",
                email="adham@example.com",
                grades=[],
                course=course,
            ),
            Student(
                name="Sara",
                email="sara@example.com",
                grades=[],
                course=Course(name="Web Development"),
            ),
        ]
    )
    db.session.commit()

    response = client.get("/students?q=machine")
    assert response.status_code == 200
    assert b"Adham" in response.data
    assert b"Sara" not in response.data
