"""Tests for the introductory Flask application."""

import pytest

from app import app


@pytest.fixture
def client():
    """Return a Flask test client configured for testing."""
    app.config.update(TESTING=True)
    with app.test_client() as test_client:
        yield test_client


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
