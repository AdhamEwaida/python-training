"""Day 20 tests for the capstone user API and documentation promises."""

import pytest

from student_portal import User, create_app, db


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


def test_user_api_crud_hashes_password_and_hides_hash(client):
    created = client.post(
        "/api/users",
        json={"username": "admin", "password": "secure-pass"},
    )
    assert created.status_code == 201
    user_id = created.json["id"]
    assert created.json == {"id": user_id, "username": "admin"}
    assert "password" not in created.get_data(as_text=True)

    user = db.session.get(User, user_id)
    assert user.password_hash != "secure-pass"
    assert user.check_password("secure-pass")

    listed = client.get("/api/users")
    assert listed.json == {"users": [{"id": user_id, "username": "admin"}]}

    updated = client.put(
        f"/api/users/{user_id}",
        json={"username": "instructor", "password": "new-password"},
    )
    assert updated.status_code == 200
    assert updated.json["username"] == "instructor"
    assert user.check_password("new-password")

    deleted = client.delete(f"/api/users/{user_id}")
    assert deleted.status_code == 204
    assert db.session.get(User, user_id) is None


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        ({}, "Username must contain between 3 and 80 characters."),
        (
            {"username": "ok-user", "password": "short"},
            "Password must contain at least 8 characters.",
        ),
    ],
)
def test_user_api_validates_create_payload(client, payload, message):
    response = client.post("/api/users", json=payload)
    assert response.status_code == 400
    assert message in response.json["details"]


def test_user_api_rejects_case_insensitive_duplicate(client):
    first = User(username="Admin")
    first.set_password("secure-pass")
    db.session.add(first)
    db.session.commit()

    response = client.post(
        "/api/users",
        json={"username": "ADMIN", "password": "another-pass"},
    )
    assert response.status_code == 400
    assert response.json["details"] == ["That username is already registered."]


def test_user_api_returns_json_404(client):
    assert client.get("/api/users/999").json == {"error": "User not found."}
    assert client.delete("/api/users/999").status_code == 404
