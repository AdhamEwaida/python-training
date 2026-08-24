"""Day 24 API contract, database-mocking, and CI coverage tests."""

from unittest.mock import patch

import pytest
from sqlalchemy.exc import SQLAlchemyError

from student_portal import create_app, db


@pytest.fixture
def app():
    """Create a portal instance backed by a fresh in-memory database."""
    test_app = create_app(
        {
            "TESTING": True,
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
    """Return Flask's test client for API requests."""
    return app.test_client()


@pytest.mark.parametrize(
    ("endpoint", "collection_key"),
    [
        ("/api/students", "students"),
        ("/api/courses", "courses"),
        ("/api/users", "users"),
    ],
)
def test_api_collection_contracts_are_json(client, endpoint, collection_key):
    """Every collection endpoint returns a predictable JSON envelope."""
    response = client.get(endpoint)

    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert collection_key in response.json
    assert response.json[collection_key] == []


@pytest.mark.parametrize(
    "endpoint",
    ["/api/students", "/api/courses", "/api/users"],
)
def test_api_write_endpoints_reject_non_object_json(client, endpoint):
    """Write endpoints reject JSON arrays instead of accepting ambiguous input."""
    response = client.post(endpoint, json=[])

    assert response.status_code == 400
    assert response.is_json
    assert response.json["error"] == "Validation failed."


def test_mocked_database_outage_returns_json_and_rolls_back(client):
    """A mocked SQLAlchemy failure is converted into a stable API response."""
    with (
        patch.object(
            db.session,
            "commit",
            side_effect=SQLAlchemyError("simulated database outage"),
        ),
        patch.object(db.session, "rollback", wraps=db.session.rollback) as rollback,
    ):
        response = client.post("/api/courses", json={"name": "CI Testing"})

    assert response.status_code == 500
    assert response.json == {"error": "Database operation failed."}
    rollback.assert_called_once_with()
