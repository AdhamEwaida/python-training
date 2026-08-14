"""Tests for user authentication and Flask sessions."""

import pytest

from student_portal import User, create_app, db


@pytest.fixture
def app():
    """Return an application with an isolated in-memory database."""
    test_app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret-key",
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        }
    )
    with test_app.app_context():
        db.create_all()
        yield test_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Return a client for the isolated authentication application."""
    return app.test_client()


def create_user(username: str = "adham", password: str = "strong-pass") -> User:
    """Persist and return a user with a securely hashed password."""
    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user


def test_password_is_hashed_and_can_be_checked(app):
    user = create_user()

    assert user.password_hash != "strong-pass"
    assert user.check_password("strong-pass") is True
    assert user.check_password("wrong-pass") is False


def test_register_creates_account_and_flashes_feedback(client):
    response = client.post(
        "/register",
        data={"username": "Adham", "password": "strong-pass"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Account created. You can now log in." in response.data
    user = db.session.execute(db.select(User)).scalar_one()
    assert user.username == "Adham"
    assert user.password_hash != "strong-pass"


def test_register_rejects_duplicate_username_ignoring_case(client):
    create_user(username="Adham")

    response = client.post(
        "/register",
        data={"username": "ADHAM", "password": "another-pass"},
    )

    assert response.status_code == 400
    assert b"That username is already registered." in response.data
    assert len(db.session.execute(db.select(User)).scalars().all()) == 1


def test_dashboard_redirects_anonymous_user_to_login(client):
    response = client.get("/dashboard")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login?next=%2Fdashboard")


def test_login_rejects_invalid_password(client):
    create_user()

    response = client.post(
        "/login",
        data={"username": "adham", "password": "wrong-pass"},
    )

    assert response.status_code == 401
    assert b"Invalid username or password." in response.data


def test_login_allows_access_to_dashboard(client):
    create_user(username="Adham")

    response = client.post(
        "/login",
        data={"username": "ADHAM", "password": "strong-pass"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Welcome, Adham. You are signed in." in response.data
    assert b"You are now logged in." in response.data


def test_logout_clears_authenticated_session(client):
    create_user()
    client.post(
        "/login",
        data={"username": "adham", "password": "strong-pass"},
    )

    response = client.post("/logout", follow_redirects=True)

    assert response.status_code == 200
    assert b"You have been logged out." in response.data
    assert client.get("/dashboard").status_code == 302


@pytest.mark.parametrize(
    "next_url",
    ["https://example.com", "//example.com/dashboard"],
)
def test_login_does_not_redirect_to_external_site(client, next_url):
    create_user()

    response = client.post(
        f"/login?next={next_url}",
        data={"username": "adham", "password": "strong-pass"},
    )

    assert response.status_code == 302
    assert response.headers["Location"] == "/dashboard"
