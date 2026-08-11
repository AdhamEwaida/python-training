"""Tests for the database-backed Flask student portal."""

import pytest

from seed import seed_database
from student_portal import Course, Student, create_app, db


@pytest.fixture
def app():
    """Return an application instance with an isolated database."""
    test_app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        }
    )
    with test_app.app_context():
        db.drop_all()
        db.create_all()
        yield test_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Return a test client for the isolated application instance."""
    with app.test_client() as test_client:
        yield test_client


def test_application_factory_applies_test_config(app):
    assert app.testing is True
    assert str(db.engine.url) == "sqlite:///:memory:"


def test_expected_blueprints_are_registered(app):
    assert {"api", "main", "students", "courses"} <= set(app.blueprints)


def add_student(
    *,
    name: str = "Adham",
    email: str = "adham@example.com",
    course_name: str = "Python",
    grades: list[float] | None = None,
) -> Student:
    """Add and return one student for a route test."""
    course = Course(name=course_name)
    student = Student(
        name=name,
        email=email,
        course=course,
        grades=grades or [],
    )
    db.session.add(student)
    db.session.commit()
    return student


def test_welcome_route(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"Welcome to the Student Portal" in response.data


def test_hello_route(client):
    response = client.get("/hello/Adham")

    assert response.status_code == 200
    assert b"Hello, Adham!" in response.data


def test_hello_route_escapes_html(client):
    response = client.get("/hello/%3Cscript%3E")

    assert response.status_code == 200
    assert b"&lt;script&gt;" in response.data
    assert b"<script>" not in response.data


@pytest.mark.parametrize("path", ["/", "/hello/Adham"])
def test_routes_reject_post_requests(client, path):
    response = client.post(path)

    assert response.status_code == 405


def test_student_list_shows_empty_state(client):
    response = client.get("/students")

    assert response.status_code == 200
    assert b"No students have been registered yet." in response.data


def test_registration_form_is_available(client):
    response = client.get("/students/register")

    assert response.status_code == 200
    assert b"Register a Student" in response.data
    assert b'<form method="post">' in response.data


def test_register_student_persists_models_and_redirects(client):
    response = client.post(
        "/students/register",
        data={
            "name": "Adham",
            "email": "adham@example.com",
            "course": "Python",
            "grades": "90, 85, 78",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Adham" in response.data
    assert b"84.33" in response.data
    student = db.session.execute(db.select(Student)).scalar_one()
    assert student.email == "adham@example.com"
    assert student.grades == [90.0, 85.0, 78.0]
    assert student.course.name == "Python"


def test_registration_reuses_course_without_matching_case(client):
    db.session.add(Course(name="Python"))
    db.session.commit()

    client.post(
        "/students/register",
        data={
            "name": "Adham",
            "email": "adham@example.com",
            "course": "python",
        },
    )

    assert len(db.session.execute(db.select(Course)).scalars().all()) == 1
    assert db.session.execute(db.select(Student)).scalar_one().course.name == "Python"


def test_registration_rejects_invalid_data(client):
    response = client.post(
        "/students/register",
        data={"name": "", "email": "invalid", "course": ""},
    )

    assert response.status_code == 400
    assert b"Name is required." in response.data
    assert b"A valid email is required." in response.data
    assert b"Course is required." in response.data
    assert db.session.execute(db.select(Student)).scalar_one_or_none() is None


def test_registration_rejects_duplicate_email(client):
    add_student()

    response = client.post(
        "/students/register",
        data={
            "name": "Another",
            "email": "ADHAM@example.com",
            "course": "Flask",
        },
    )

    assert response.status_code == 400
    assert b"A student with this email already exists." in response.data


def test_student_list_escapes_registered_values(client):
    add_student(name="<script>alert(1)</script>")

    response = client.get("/students")

    assert response.status_code == 200
    assert b"&lt;script&gt;alert(1)&lt;/script&gt;" in response.data
    assert b"<script>" not in response.data


@pytest.mark.parametrize(
    ("grades", "message"),
    [
        ("90, excellent", b"Grades must be comma-separated numbers."),
        ("101", b"Each grade must be between 0 and 100."),
        ("nan", b"Each grade must be between 0 and 100."),
    ],
)
def test_registration_rejects_invalid_grades(client, grades, message):
    response = client.post(
        "/students/register",
        data={
            "name": "Adham",
            "email": "adham@example.com",
            "course": "Python",
            "grades": grades,
        },
    )

    assert response.status_code == 400
    assert message in response.data


def test_student_list_links_to_detail_page(client):
    student = add_student()

    response = client.get("/students")

    assert response.status_code == 200
    assert f'href="/students/{student.id}"'.encode() in response.data


def test_student_detail_shows_profile_and_grades(client):
    student = add_student(grades=[80.0, 90.0])

    response = client.get(f"/students/{student.id}")

    assert response.status_code == 200
    assert b"adham@example.com" in response.data
    assert b"80.0" in response.data
    assert b"90.0" in response.data
    assert b"85.00" in response.data


def test_missing_student_detail_returns_404(client):
    response = client.get("/students/999")

    assert response.status_code == 404


def test_edit_student_updates_database(client):
    student = add_student()

    response = client.post(
        f"/students/{student.id}/edit",
        data={
            "name": "Adham Updated",
            "email": "updated@example.com",
            "course": "Flask",
            "grades": "95, 100",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    updated = db.session.get(Student, student.id)
    assert updated.name == "Adham Updated"
    assert updated.email == "updated@example.com"
    assert updated.course.name == "Flask"
    assert updated.grades == [95.0, 100.0]


def test_delete_student_removes_database_record(client):
    student = add_student()
    student_id = student.id

    response = client.post(
        f"/students/{student_id}/delete",
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"No students have been registered yet." in response.data
    assert db.session.get(Student, student_id) is None


def test_course_list_shows_enrollment_count(client):
    add_student(course_name="Python")

    response = client.get("/courses")

    assert response.status_code == 200
    assert b"Python" in response.data
    assert b"1 student(s)" in response.data


def test_seed_database_is_repeatable(client):
    seed_database()
    seed_database()

    students = db.session.execute(db.select(Student)).scalars().all()
    courses = db.session.execute(db.select(Course)).scalars().all()
    assert len(students) == 2
    assert len(courses) == 2


def test_api_student_list_returns_json(client):
    student = add_student(grades=[80.0, 90.0])

    response = client.get("/api/students")

    assert response.status_code == 200
    assert response.is_json
    assert response.json == {
        "students": [
            {
                "id": student.id,
                "name": "Adham",
                "email": "adham@example.com",
                "grades": [80.0, 90.0],
                "average": 85.0,
                "course": {"id": student.course.id, "name": "Python"},
            }
        ]
    }


def test_api_creates_student_and_returns_location(client):
    response = client.post(
        "/api/students",
        json={
            "name": "Adham",
            "email": "adham@example.com",
            "course": "Python",
            "grades": [90, 85, 80],
        },
    )

    assert response.status_code == 201
    assert response.headers["Location"] == f"/api/students/{response.json['id']}"
    assert response.json["average"] == 85.0
    assert response.json["course"]["name"] == "Python"
    assert db.session.get(Student, response.json["id"]) is not None


def test_api_student_detail_returns_json(client):
    student = add_student()

    response = client.get(f"/api/students/{student.id}")

    assert response.status_code == 200
    assert response.json["email"] == "adham@example.com"


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        ({}, "Name must be a string."),
        (
            {
                "name": "Adham",
                "email": "invalid",
                "course": "Python",
            },
            "A valid email is required.",
        ),
        (
            {
                "name": "Adham",
                "email": "adham@example.com",
                "course": "Python",
                "grades": "90, 80",
            },
            "Grades must be a list of numbers.",
        ),
        (
            {
                "name": "Adham",
                "email": "adham@example.com",
                "course": "Python",
                "grades": [101],
            },
            "Each grade must be between 0 and 100.",
        ),
    ],
)
def test_api_rejects_invalid_student_payload(client, payload, message):
    response = client.post("/api/students", json=payload)

    assert response.status_code == 400
    assert response.json["error"] == "Validation failed."
    assert message in response.json["details"]


def test_api_rejects_non_json_body(client):
    response = client.post("/api/students", data="not json")

    assert response.status_code == 400
    assert response.json["details"] == ["Request body must be a JSON object."]


def test_api_rejects_duplicate_email(client):
    add_student()

    response = client.post(
        "/api/students",
        json={
            "name": "Another Student",
            "email": "ADHAM@example.com",
            "course": "Flask",
        },
    )

    assert response.status_code == 400
    assert response.json["details"] == ["A student with this email already exists."]


def test_api_updates_student(client):
    student = add_student()

    response = client.put(
        f"/api/students/{student.id}",
        json={
            "name": "Adham Updated",
            "email": "updated@example.com",
            "course": "Flask",
            "grades": [100, 95],
        },
    )

    assert response.status_code == 200
    assert response.json["name"] == "Adham Updated"
    assert response.json["grades"] == [100.0, 95.0]
    assert response.json["course"]["name"] == "Flask"


def test_api_deletes_student(client):
    student = add_student()
    student_id = student.id

    response = client.delete(f"/api/students/{student_id}")

    assert response.status_code == 204
    assert response.data == b""
    assert db.session.get(Student, student_id) is None


@pytest.mark.parametrize("method", ["get", "put", "delete"])
def test_api_missing_student_returns_json_404(client, method):
    request_method = getattr(client, method)
    kwargs = {}
    if method == "put":
        kwargs["json"] = {
            "name": "Adham",
            "email": "adham@example.com",
            "course": "Python",
        }

    response = request_method("/api/students/999", **kwargs)

    assert response.status_code == 404
    assert response.json == {"error": "Student not found."}


def test_api_database_failure_returns_json_500(client, monkeypatch):
    def fail_query(*args, **kwargs):
        from sqlalchemy.exc import SQLAlchemyError

        raise SQLAlchemyError("simulated failure")

    monkeypatch.setattr(db.session, "execute", fail_query)

    response = client.get("/api/students")

    assert response.status_code == 500
    assert response.json == {"error": "Database operation failed."}
