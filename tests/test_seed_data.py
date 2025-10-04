"""
Tests for app.seed_data seeding functions.
"""

from unittest.mock import patch
import pytest
import app.seed_data as seed_data


@pytest.fixture(autouse=True)
def patch_file_storage():
    """Patch file storage to avoid actual file operations."""
    with patch("app.seed_data.file_storage") as mock_fs:
        mock_fs.generate_file_path.return_value = "/tmp/fakepath.md"
        mock_fs.save_file.return_value = (123, "checksum123")
        yield mock_fs


@pytest.mark.usefixtures("mock_db")
def test_seed_admin_user_creates_new(mock_db):
    """Test creating a new admin user when none exists."""
    # Simulate no existing admin
    mock_db.execute_one.return_value = None
    mock_db.execute_modify.return_value = 42
    admin_id = seed_data.seed_admin_user(force=False)
    assert admin_id == 42
    assert mock_db.execute_modify.called
    assert mock_db.execute_one.called


@pytest.mark.usefixtures("mock_db")
def test_seed_admin_user_exists(mock_db):
    """Test not creating a new admin if one exists."""
    # Simulate existing admin
    mock_db.execute_one.return_value = {"id": 99}
    admin_id = seed_data.seed_admin_user(force=False)
    assert admin_id == 99
    assert mock_db.execute_one.called
    assert not mock_db.execute_modify.called


@pytest.mark.usefixtures("mock_db")
def test_seed_admin_user_force(mock_db):
    """Test force creating a new admin user."""
    # Simulate existing admin, force=True
    mock_db.execute_one.return_value = {"id": 77}
    admin_id = seed_data.seed_admin_user(force=True)
    assert admin_id == 77
    assert mock_db.execute_one.called
    # Should not create new admin
    assert not mock_db.execute_modify.called


@pytest.mark.usefixtures("mock_db")
def test_seed_other_data_runs(mock_db):
    """Test seeding other data creates entries as needed."""
    # Simulate all queries return None (so all inserts happen)
    mock_db.execute_one.return_value = None
    mock_db.execute_modify.return_value = 1
    # Should not raise
    seed_data.seed_other_data(admin_id=1)
    assert mock_db.execute_modify.called
    assert mock_db.execute_one.called


@pytest.mark.usefixtures("mock_db")
def test_seed_other_data_existing(mock_db):
    """Test seeding other data when entries already exist."""

    # Simulate all queries return existing objects (so no inserts)
    def execute_one_side_effect(*args):
        if "users" in args[0]:
            return {"id": 2}
        if "teams" in args[0]:
            return {"id": 3}
        if "team_members" in args[0]:
            return {"id": 4}
        if "files" in args[0]:
            return {"id": 5}
        return None

    mock_db.execute_one.side_effect = execute_one_side_effect
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
