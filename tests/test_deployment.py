"""Tests for Day 26 deployment configuration and health monitoring."""

from pathlib import Path

import pytest

from student_portal import create_app, db

PROJECT_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def client():
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
    with app.app_context():
        db.create_all()
        with app.test_client() as test_client:
            yield test_client
        db.session.remove()
        db.drop_all()


def test_health_endpoint_reports_environment(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json == {"environment": "development", "status": "ok"}


def test_render_blueprint_defines_service_database_and_secrets():
    blueprint = (PROJECT_ROOT / "render.yaml").read_text(encoding="utf-8")

    assert "runtime: python" in blueprint
    assert "gunicorn wsgi:app" in blueprint
    assert "healthCheckPath: /health" in blueprint
    assert "generateValue: true" in blueprint
    assert "fromDatabase:" in blueprint
    assert "plan: free" in blueprint


def test_production_database_driver_is_pinned():
    requirements = (PROJECT_ROOT / "requirements.txt").read_text(encoding="utf-8")

    assert "psycopg[binary]==3.3.4" in requirements
