"""
Pytest configuration file.
Contains fixtures for testing.
"""

import os
from unittest.mock import MagicMock, patch
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

mock_db_instance = MagicMock()
mock_db_instance.test_connection.return_value = True
mock_db_instance.execute_query.return_value = []
mock_db_instance.execute_one.return_value = {"now": "2025-10-03T10:00:00"}
mock_db_instance.execute_modify.return_value = 1
mock_db_instance.execute_one.side_effect = None
mock_db_instance.execute_query.side_effect = None
mock_db_instance.execute_modify.side_effect = None
patcher = patch("app.db.get_db", return_value=mock_db_instance)
patcher.start()
sys.modules["_test_mock_db_instance"] = (
    mock_db_instance  # For access in fixtures if needed
)


@pytest.fixture(autouse=True)
def reset_mock_db(mock_db):
    """Reset the mock database before each test."""
    mock_db.reset_mock()
    mock_db.test_connection.return_value = True
    mock_db.execute_query.return_value = []
    mock_db.execute_one.return_value = {"now": "2025-10-03T10:00:00"}
    mock_db.execute_modify.return_value = 1
    mock_db.execute_one.side_effect = None
    mock_db.execute_query.side_effect = None
    mock_db.execute_modify.side_effect = None


@pytest.fixture(autouse=True)
def mock_db():
    """Return the global mock database instance for test customization."""
    yield mock_db_instance


@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    os.environ["FLASK_ENV"] = "testing"
    os.environ["JWT_SECRET"] = "test_secret"
    os.environ["MYSQL_HOST"] = "dummy"
    os.environ["MYSQL_PORT"] = "3306"
    os.environ["MYSQL_USER"] = "dummy"
    os.environ["MYSQL_PASSWORD"] = "dummy"
    os.environ["MYSQL_DATABASE"] = "dummy"
    # Set admin credentials for seed_data tests
    os.environ["ADMIN_EMAIL"] = "admin@test.com"
    os.environ["ADMIN_PASSWORD"] = "test_admin_password"
    from app.main import create_app  # Import after patching get_db

    test_app = create_app()
    test_app.config.update(
        {
            "TESTING": True,
            "JWT_SECRET": "test_secret",
            "JWT_EXPIRY_HOURS": 1,
            "UPLOAD_FOLDER": "test_uploads",
            "BCRYPT_ROUNDS": 4,
        }
    )
    with test_app.app_context():
        yield test_app


@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return app.test_client()


@pytest.fixture
def auth_headers():
    """Create authentication headers for tests."""
    return {"Authorization": "Bearer test_token", "Content-Type": "application/json"}
