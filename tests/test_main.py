"""
Unit tests for app.main Flask app factory and endpoints, using mocking for config and db.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from app.main import create_app


@pytest.fixture
def client():
    with patch("app.main.Config") as mock_config, patch(
        "app.main.get_db"
    ) as mock_get_db:
        # Setup config
        mock_config.DEBUG = True
        mock_config.validate = MagicMock()
        # Setup db
        mock_db = MagicMock()
        mock_db.test_connection.return_value = True
        mock_db.execute_one.return_value = {"now": datetime(2025, 10, 4, 12, 0, 0)}
        mock_get_db.return_value = mock_db
        app = create_app()
        app.config["TESTING"] = True
        app.config["PROPAGATE_EXCEPTIONS"] = False
        with app.test_client() as c:
            yield c


def test_index(client):
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["message"] == "Markboard API"
    assert data["status"] == "running"


def test_health_healthy(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert data["timestamp"].startswith("2025-10-04T12:00:00")


def test_health_unhealthy():
    with patch("app.main.Config") as mock_config, patch(
        "app.main.get_db"
    ) as mock_get_db, patch("sys.exit") as _:
        mock_config.DEBUG = True
        mock_config.validate = MagicMock()
        mock_db = MagicMock()
        mock_db.test_connection.return_value = False
        mock_db.execute_one.return_value = {"now": datetime(2025, 10, 4, 12, 0, 0)}
        mock_get_db.return_value = mock_db
        app = create_app()
        app.config["TESTING"] = True
        with app.test_client() as client:
            resp = client.get("/health")
            assert resp.status_code == 503
            data = resp.get_json()
            assert data["status"] == "unhealthy"
            assert data["database"] == "disconnected"


def test_404(client):
    resp = client.get("/no-such-endpoint")
    assert resp.status_code == 404
    data = resp.get_json()
    assert data["error"] == "Endpoint not found"


def test_500_handler(client):
    # Register a route that raises an error
    @client.application.route("/error")
    def error():
        raise Exception("fail")

    resp = client.get("/error")
    assert resp.status_code == 500
    data = resp.get_json()
    assert data["error"] == "Internal server error"
