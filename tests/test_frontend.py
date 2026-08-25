"""Tests for the Day 25 Bootstrap UI and asynchronous student search."""

import pytest

from student_portal import Course, Student, create_app, db


@pytest.fixture
def app():
    test_app = create_app(
        {"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"}
    )
    with test_app.app_context():
        db.create_all()
        yield test_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def add_student(name: str, email: str, course: Course) -> None:
    db.session.add(Student(name=name, email=email, course=course, grades=[]))


def test_home_page_loads_bootstrap_and_project_styles(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"bootstrap@5.3.8" in response.data
    assert b"/static/css/site.css" in response.data
    assert b"Student Management Dashboard" in response.data


def test_students_page_exposes_async_search_hooks(client):
    response = client.get("/students")

    assert response.status_code == 200
    assert b"data-student-search" in response.data
    assert b'data-api-url="/api/students"' in response.data
    assert b"/static/js/student-search.js" in response.data


def test_student_api_searches_and_paginates_for_frontend(client):
    python = Course(name="Python")
    flask = Course(name="Flask")
    add_student("Adham", "adham@example.com", python)
    add_student("Maya", "maya@example.com", flask)
    add_student("Omar", "omar@example.com", python)
    db.session.commit()

    response = client.get("/api/students?q=python&page=1&per_page=1")

    assert response.status_code == 200
    assert len(response.json["students"]) == 1
    assert response.json["students"][0]["course"]["name"] == "Python"
    assert response.json["pagination"] == {
        "page": 1,
        "pages": 2,
        "per_page": 1,
        "total": 2,
    }


def test_student_api_keeps_original_unpaginated_contract(client):
    response = client.get("/api/students")

    assert response.json == {"students": []}


def test_student_search_script_is_served(client):
    response = client.get("/static/js/student-search.js")

    assert response.status_code == 200
    assert b"fetch(" in response.data
    assert b"textContent" in response.data
