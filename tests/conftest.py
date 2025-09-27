"""
Test configuration and fixtures.
"""

import pytest
import os
import tempfile
from app.main import create_app
from app.db import Database
from app.config import Config


@pytest.fixture
def app():
    """Create application for testing."""
    # Override config for testing
    Config.MYSQL_DATABASE = "markboard_test"
    Config.JWT_SECRET = "test-secret-key"
    Config.DEBUG = True

    app = create_app()
    app.config["TESTING"] = True

    yield app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create test CLI runner."""
    return app.test_cli_runner()


@pytest.fixture
def auth_headers():
    """Create authorization headers for testing."""
    # This will be populated by login tests
    return {}


class TestDatabase:
    """Test database helper class."""

    @staticmethod
    def setup_test_db():
        """Setup test database with schema."""
        # Note: In a real test environment, you'd want to:
        # 1. Create a separate test database
        # 2. Run migrations/schema setup
        # 3. Clean up after tests
        pass

    @staticmethod
    def cleanup_test_db():
        """Clean up test database."""
        pass
