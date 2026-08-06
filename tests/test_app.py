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


def test_register_student_redirects_to_student_list(client):
    response = client.post(
        "/students/register",
        data={
            "name": "Adham",
            "email": "adham@example.com",
            "course": "Python",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Adham" in response.data
    assert b"adham@example.com" in response.data
    assert b"Python" in response.data
    assert students == [
        {
            "name": "Adham",
            "email": "adham@example.com",
            "course": "Python",
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
            "name": "<script>alert(1)</script>",
            "email": "safe@example.com",
            "course": "Python",
        }
    )

    response = client.get("/students")

    assert response.status_code == 200
    assert b"&lt;script&gt;alert(1)&lt;/script&gt;" in response.data
    assert b"<script>" not in response.data
