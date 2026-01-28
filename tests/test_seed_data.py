"""
Tests for app.seed_data seeding functions.
"""

import os
from unittest.mock import patch
import pytest
import app.infrastructure.database.seed_data as seed_data


@pytest.fixture(autouse=True)
def setup_test_env():
    """Set up test environment variables."""
    os.environ["ADMIN_EMAIL"] = "admin@test.com"
    os.environ["ADMIN_PASSWORD"] = "test_admin_password"
    os.environ["BCRYPT_ROUNDS"] = "4"  # Faster for tests

    # Reload config and seed_data modules to pick up environment variables
    import importlib
    import config.settings
    import app.infrastructure.database.seed_data as sd_module

    importlib.reload(config.settings)
    importlib.reload(sd_module)

    # Update the global seed_data reference
    global seed_data
    seed_data = sd_module


@pytest.fixture(autouse=True)
def patch_file_storage():
    """Patch file storage to avoid actual file operations."""
    with patch("app.infrastructure.database.seed_data.file_storage") as mock_fs:
        mock_fs.generate_file_path.return_value = "/tmp/fakepath.md"
        mock_fs.save_file.return_value = (123, "checksum123")
        yield mock_fs


def test_seed_admin_user_creates_new(mock_db):
    """Test creating a new admin user when none exists."""
    # Reset and configure mock
    mock_db.reset_mock()
    mock_db.execute_one.return_value = None  # No existing admin
    mock_db.execute_modify.return_value = 42  # New admin ID

    # Patch Config to have admin credentials
    with patch("app.infrastructure.database.seed_data.Config") as mock_config:
        mock_config.ADMIN_EMAIL = "admin@test.com"
        mock_config.ADMIN_PASSWORD = "test_admin_password"
        mock_config.BCRYPT_ROUNDS = 4

        admin_id = seed_data.seed_admin_user(force=False)

        assert admin_id == 42
        assert mock_db.execute_modify.called
        assert mock_db.execute_one.called


def test_seed_admin_user_exists(mock_db):
    """Test not creating a new admin if one exists."""
    # Reset and configure mock
    mock_db.reset_mock()
    mock_db.execute_one.return_value = {"id": 99}  # Existing admin

    with patch("app.infrastructure.database.seed_data.Config") as mock_config:
        mock_config.ADMIN_EMAIL = "admin@test.com"
        mock_config.ADMIN_PASSWORD = "test_admin_password"
        mock_config.BCRYPT_ROUNDS = 4

        admin_id = seed_data.seed_admin_user(force=False)

        assert admin_id == 99
        assert mock_db.execute_one.called
        assert not mock_db.execute_modify.called


def test_seed_admin_user_force(mock_db):
    """Test force creating admin user when one exists."""
    # Reset and configure mock
    mock_db.reset_mock()
    mock_db.execute_one.return_value = {"id": 77}  # Existing admin

    with patch("app.infrastructure.database.seed_data.Config") as mock_config:
        mock_config.ADMIN_EMAIL = "admin@test.com"
        mock_config.ADMIN_PASSWORD = "test_admin_password"
        mock_config.BCRYPT_ROUNDS = 4

        admin_id = seed_data.seed_admin_user(force=True)

        assert admin_id == 77
        assert mock_db.execute_one.called
        # Force mode with existing admin should not create new one
        assert not mock_db.execute_modify.called


def test_seed_other_data_runs(mock_db):
    """Test seeding other data creates entries as needed."""
    # Reset and configure mock
    mock_db.reset_mock()
    mock_db.execute_one.return_value = None  # No existing entries
    mock_db.execute_modify.return_value = 1  # Success

    with patch("app.infrastructure.database.seed_data.Config") as mock_config:
        mock_config.ADMIN_EMAIL = "admin@test.com"
        mock_config.ADMIN_PASSWORD = "test_admin_password"
        mock_config.BCRYPT_ROUNDS = 4

        seed_data.seed_other_data(admin_id=1)

        assert mock_db.execute_modify.called
        assert mock_db.execute_one.called


def test_seed_other_data_existing(mock_db):
    """Test seeding other data when entries already exist."""
    # Reset and configure mock
    mock_db.reset_mock()

    def execute_one_side_effect(query, *args):
        # Return existing objects for all queries
        if "users" in query:
            return {"id": 2}
        elif "teams" in query:
            return {"id": 3}
        elif "team_members" in query:
            return {"id": 4}
        elif "files" in query:
            return {"id": 5}
        return {"id": 1}  # Default return

    mock_db.execute_one.side_effect = execute_one_side_effect

    with patch("app.infrastructure.database.seed_data.Config") as mock_config:
        mock_config.ADMIN_EMAIL = "admin@test.com"
        mock_config.ADMIN_PASSWORD = "test_admin_password"
        mock_config.BCRYPT_ROUNDS = 4

        seed_data.seed_other_data(admin_id=1)

        assert mock_db.execute_one.called


@pytest.mark.usefixtures("mock_db")
def test_seed_development_data(monkeypatch):
    """Test seeding development data calls appropriate functions."""
    monkeypatch.setattr(seed_data, "seed_admin_user", lambda force=False: 123)
    monkeypatch.setattr(seed_data, "seed_other_data", lambda admin_id: None)
    seed_data.seed_development_data(force=True)


@pytest.mark.usefixtures("mock_db")
def test_seed_production_data(monkeypatch):
    """Test seeding production data calls appropriate functions."""
    monkeypatch.setattr(seed_data, "seed_admin_user", lambda force=False: 456)
    seed_data.seed_production_data(force=True)
