"""Day 23 tests for CSRF, uploads, and custom error handling."""

from io import BytesIO
from pathlib import Path

import pytest

from student_portal import Course, Student, create_app, db


@pytest.fixture
def app():
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "UPLOAD_FOLDER": str(Path.cwd() / ".test_uploads"),
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


def add_student():
    student = Student(
        name="Adham",
        email="adham@example.com",
        grades=[],
        course=Course(name="Python"),
    )
    db.session.add(student)
    db.session.commit()
    return student


def test_profile_picture_upload_uses_generated_filename(client, app):
    student = add_student()
    response = client.post(
        f"/students/{student.id}/profile-picture",
        data={
            "profile_picture": (BytesIO(b"fake-image-data"), "avatar.png"),
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Profile picture updated successfully." in response.data
    assert student.profile_picture.startswith(f"student-{student.id}-")
    assert student.profile_picture.endswith(".png")
    assert (Path(app.config["UPLOAD_FOLDER"]) / student.profile_picture).is_file()


def test_profile_picture_rejects_non_image(client):
    student = add_student()
    response = client.post(
        f"/students/{student.id}/profile-picture",
        data={"profile_picture": (BytesIO(b"text"), "notes.txt")},
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert b"Upload a PNG, JPEG, GIF, or WebP image." in response.data
    assert student.profile_picture is None


def test_custom_404_page(client):
    response = client.get("/not-a-real-page")
    assert response.status_code == 404
    assert b"Page Not Found" in response.data


def test_csrf_rejects_missing_token_when_enabled():
    app = create_app(
        {
            "TESTING": False,
            "CSRF_ENABLED": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SECRET_KEY": "test-secret",
        }
    )
    with app.app_context():
        db.create_all()
        response = app.test_client().post(
            "/register",
            data={"username": "admin", "password": "secure-pass"},
        )
        assert response.status_code == 400
        assert b"security token" in response.data
        db.drop_all()


def test_forms_render_csrf_token(client):
    response = client.get("/register")
    assert response.status_code == 200
    assert b'name="_csrf_token"' in response.data
