"""
Pytest configuration file.
Contains fixtures for testing.
"""

import os
from unittest.mock import MagicMock, patch
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Mock external dependencies before importing anything
# Create realistic mocks for mysql.connector
mock_mysql = MagicMock()
mock_mysql_connector = MagicMock()
mock_mysql_pooling = MagicMock()
sys.modules["mysql"] = mock_mysql
sys.modules["mysql.connector"] = mock_mysql_connector
sys.modules["mysql.connector.pooling"] = mock_mysql_pooling
sys.modules["mysql.connector"].Error = Exception  # Make Error a real exception class

mock_bcrypt = MagicMock()
mock_bcrypt.gensalt = MagicMock(return_value=b"$2b$12$mocksaltmocksaltmocksalt")
mock_bcrypt.hashpw = MagicMock(return_value=b"$2b$12$mockedhashpassword")
mock_bcrypt.checkpw = MagicMock(return_value=True)
sys.modules["bcrypt"] = mock_bcrypt
sys.modules["dotenv"] = MagicMock()
sys.modules["jwt"] = MagicMock()
sys.modules["flask"] = MagicMock()
sys.modules["flask_cors"] = MagicMock()

# Create mock database instance
mock_db_instance = MagicMock()
mock_db_instance.test_connection.return_value = True
mock_db_instance.execute_query.return_value = []
mock_db_instance.execute_one.return_value = {"now": "2025-10-03T10:00:00"}
mock_db_instance.execute_modify.return_value = 1
mock_db_instance.execute_one.side_effect = None
mock_db_instance.execute_query.side_effect = None
mock_db_instance.execute_modify.side_effect = None

# Store the mock for access in fixtures
sys.modules["_test_mock_db_instance"] = mock_db_instance

# Patch get_db function at module level - import the module and patch it directly
from unittest.mock import patch as mock_patch

# We'll patch get_db in the app fixture and other places as needed


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
    # Set environment variables before importing config
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

    # Reload config module to pick up new environment variables
    import importlib
    import config.settings

    importlib.reload(config.settings)
    from config.settings import Config

    # Mock get_db and Config.validate before creating app
    with patch("app.main.get_db") as mock_get_db, patch(
        "app.main.Config.validate"
    ) as mock_validate:
        mock_get_db.return_value = mock_db_instance
        mock_db_instance.reset_mock()
        mock_db_instance.test_connection.return_value = True
        mock_db_instance.execute_one.return_value = {"now": "2025-10-03T10:00:00"}
        mock_validate.return_value = None  # Don't raise errors

        from app.main import create_app

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
