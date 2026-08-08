"""Tests for the introductory Flask application."""

import pytest

from app import app, students


@pytest.fixture
def client():
    """Return a Flask test client configured for testing."""
    app.config.update(TESTING=True)
    students.clear()
    with app.test_client() as test_client:
        yield test_client
    students.clear()


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


def test_register_student_redirects_to_student_detail(client):
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
    assert b"adham@example.com" in response.data
    assert b"Python" in response.data
    assert b"Average:" in response.data
    assert b"84.33" in response.data
    assert students == [
        {
            "id": 1,
            "name": "Adham",
            "email": "adham@example.com",
            "course": "Python",
            "grades": [90.0, 85.0, 78.0],
        }
    ]


def test_registration_rejects_invalid_data(client):
    response = client.post(
        "/students/register",
        data={"name": "", "email": "invalid", "course": ""},
    )

    assert response.status_code == 400
    assert b"Name is required." in response.data
    assert b"A valid email is required." in response.data
    assert b"Course is required." in response.data
    assert students == []


def test_student_list_escapes_registered_values(client):
    students.append(
        {
            "id": 1,
            "name": "<script>alert(1)</script>",
            "email": "safe@example.com",
            "course": "Python",
            "grades": [],
        }
    )

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
    assert students == []


def test_student_list_links_to_detail_page(client):
    students.append(
        {
            "id": 7,
            "name": "Adham",
            "email": "adham@example.com",
            "course": "Python",
            "grades": [88.0],
        }
    )

    response = client.get("/students")

    assert response.status_code == 200
    assert b'href="/students/7"' in response.data


def test_student_detail_shows_profile_and_grades(client):
    students.append(
        {
            "id": 1,
            "name": "Adham",
            "email": "adham@example.com",
            "course": "Python",
            "grades": [80.0, 90.0],
        }
    )

    response = client.get("/students/1")

    assert response.status_code == 200
    assert b"adham@example.com" in response.data
    assert b"80.0" in response.data
    assert b"90.0" in response.data
    assert b"85.00" in response.data


def test_missing_student_detail_returns_404(client):
    response = client.get("/students/999")

    assert response.status_code == 404
