"""
File service tests.
"""

from unittest.mock import patch
from datetime import datetime, timezone
from app.services.file_service import FileService


def test_create_file_success(mock_db):
    """Test creating a file successfully."""

    mock_db.reset_mock()
    # 1. Check for duplicate file name (returns None)
    # 2. Insert file record (returns {"id": 42})
    # 3. Get complete file record (returns file dict)
    mock_db.execute_one.side_effect = [
        None,  # No duplicate file
        {
            "id": 42,
            "name": "test.md",
            "file_size": 123,
            "mime_type": "text/markdown",
            "owner_id": 1,
            "team_id": None,
            "created_at": "2025-10-03T10:00:00",
            "updated_at": "2025-10-03T10:00:00",
        },
    ]
    mock_db.execute_modify.return_value = 42
    with patch(
        "app.services.file_service.file_storage.generate_file_path"
    ) as mock_gen_path, patch(
        "app.services.file_service.file_storage.save_file"
    ) as mock_save_file, patch(
        "app.services.file_service.log_activity"
    ) as mock_log_activity:
        mock_gen_path.return_value = "/tmp/test.md"
        mock_save_file.return_value = (123, "abc123")
        success, _, file_record = FileService.create_file("test.md", "# Test", 1, None)
        assert success
        assert file_record["name"] == "test.md"
        mock_log_activity.assert_called_with(
            1, "file_created", "file", 42, "Created file: test.md"
        )


def test_get_file_details_success(mock_db):
    """Test getting a file successfully."""

    mock_db.reset_mock()
    # 1. Access check (check_file_access) returns True
    # 2. Get file record (returns file dict with file_path, file_size, etc.)
    file_record_db = {
        "id": 1,
        "name": "test.md",
        "file_path": "/tmp/test.md",
        "file_size": 123,
        "mime_type": "text/markdown",
        "owner_id": 1,
        "team_id": None,
        "created_at": "2025-10-03T10:00:00",
        "updated_at": "2025-10-03T10:00:00",
    }
    mock_db.execute_one.return_value = file_record_db
    with patch("app.services.file_service.check_file_access", return_value=True), patch(
        "app.services.file_service.file_storage.read_file"
    ) as mock_read_file, patch(
        "app.services.file_service.log_activity"
    ) as mock_log_activity:
        mock_read_file.return_value = "# Test Content"
        success, _, file_record = FileService.get_file_details(1, 1)
        assert success
        assert file_record["id"] == 1
        assert file_record["content"] == "# Test Content"
        mock_log_activity.assert_called_with(
            1, "file_viewed", "file", 1, "Viewed file: test.md"
        )


def test_create_file_invalid_name(mock_db):
    """Test creating a file with invalid (empty) name fails."""
    mock_db.reset_mock()
    success, msg, file_record = FileService.create_file("   ", "content", 1)
    assert not success
    assert msg == "File name is required"
    assert file_record is None


def test_create_file_duplicate_name(mock_db):
    """Test creating a file with duplicate name fails."""
    mock_db.reset_mock()
    mock_db.execute_one.side_effect = [
        {"id": 1},  # Duplicate file exists
    ]
    success, msg, file_record = FileService.create_file("test.md", "content", 1)
    assert not success
    assert msg == "File with this name already exists"
    assert file_record is None


def test_create_file_invalid_team_access(mock_db):
    """Test creating a file in a team without access fails."""
    mock_db.reset_mock()
    mock_db.execute_one.side_effect = [
        None,  # No team member found
    ]
    success, msg, file_record = FileService.create_file("test.md", "content", 1, 2)
    assert not success
    assert msg == "Access denied to team"
    assert file_record is None


def test_get_file_details_access_denied(mock_db):
    """Test getting a file fails due to access denied."""

    mock_db.reset_mock()
    with patch("app.services.file_service.check_file_access", return_value=False):
        success, msg, file_record = FileService.get_file_details(1, 1)
        assert not success
        assert msg == "Access denied"
        assert file_record is None


def test_get_file_details_not_found(mock_db):
    """Test getting a file that does not exist fails."""

    mock_db.reset_mock()
    with patch("app.services.file_service.check_file_access", return_value=True):
        mock_db.execute_one.return_value = None
        success, msg, file_record = FileService.get_file_details(1, 1)
        assert not success
        assert msg == "File not found"
        assert file_record is None


def test_update_file_name_and_content(mock_db):
    """Test updating a file's name and content successfully."""

    mock_db.reset_mock()
    file_record = {
        "id": 1,
        "name": "old.md",
        "file_path": "/tmp/old.md",
        "owner_id": 1,
        "team_id": None,
    }
    updated_file = {
        "id": 1,
        "name": "new.md",
        "file_size": 10,
        "mime_type": "text/plain",
        "owner_id": 1,
        "team_id": None,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
    mock_db.execute_one.side_effect = [file_record, None, updated_file]
    mock_db.execute_modify.return_value = 1
    with patch("app.services.file_service.check_file_access", return_value=True), patch(
        "app.services.file_service.file_storage.save_file"
    ) as mock_save_file, patch(
        "app.services.file_service.log_activity"
    ) as mock_log_activity:
        mock_save_file.return_value = (10, "checksum")
        success, _, file = FileService.update_file(
            1, 1, name="new.md", content="new content"
        )
        assert success
        assert file["name"] == "new.md"
        mock_log_activity.assert_called()


def test_update_file_duplicate_name(mock_db):
    """Test updating a file with a duplicate name fails."""
    mock_db.reset_mock()
    file_record = {
        "id": 1,
        "name": "old.md",
        "file_path": "/tmp/old.md",
        "owner_id": 1,
        "team_id": None,
    }
    mock_db.execute_one.side_effect = [file_record, {"id": 2}]
    with patch("app.services.file_service.check_file_access", return_value=True):
        success, msg, file = FileService.update_file(1, 1, name="duplicate.md")
        assert not success
        assert msg == "File with this name already exists"
        assert file is None


def test_delete_file_success(mock_db):
    """Test deleting a file successfully."""
    mock_db.reset_mock()
    file_record = {"name": "test.md", "file_path": "/tmp/test.md"}
    mock_db.execute_one.return_value = file_record
    mock_db.execute_modify.return_value = 1
    with patch("app.services.file_service.check_file_access", return_value=True), patch(
        "app.services.file_service.file_storage.delete_file"
    ) as mock_delete_file, patch(
        "app.services.file_service.log_activity"
    ) as mock_log_activity:
        mock_delete_file.return_value = None
        success, msg = FileService.delete_file(1, 1)
        assert success
        assert msg == "File deleted successfully"
        mock_log_activity.assert_called()


def test_delete_file_not_found(mock_db):
    """Test deleting a file that does not exist fails."""
    mock_db.reset_mock()
    mock_db.execute_one.return_value = None
    with patch("app.services.file_service.check_file_access", return_value=True):
        success, msg = FileService.delete_file(1, 1)
        assert not success
        assert msg == "File not found"


def test_get_file_content_success(mock_db):
    """Test getting file content successfully."""
    mock_db.reset_mock()
    file_record = {"name": "test.md", "file_path": "/tmp/test.md"}
    mock_db.execute_one.return_value = file_record
    with patch("app.services.file_service.check_file_access", return_value=True), patch(
        "app.services.file_service.file_storage.read_file", return_value="file content"
    ):
        success, _, content = FileService.get_file_content(1, 1)
        assert success
        assert content == "file content"


def test_get_file_content_not_found(mock_db):
    """Test getting file content for a file that does not exist fails."""
    mock_db.reset_mock()
    mock_db.execute_one.return_value = None
    with patch("app.services.file_service.check_file_access", return_value=True):
        success, msg, content = FileService.get_file_content(1, 1)
        assert not success
        assert msg == "File not found"
        assert content is None


def test_get_file_name_success(mock_db):
    """Test getting a file's name successfully."""
    mock_db.reset_mock()
    mock_db.execute_one.return_value = {"name": "test.md"}
    with patch("app.services.file_service.check_file_access", return_value=True):
        success, _, name = FileService.get_file_name(1, 1)
        assert success
        assert name == "test.md"


def test_get_file_name_not_found(mock_db):
    """Test getting a file name for a file that does not exist fails."""
    mock_db.reset_mock()
    mock_db.execute_one.return_value = None
    with patch("app.services.file_service.check_file_access", return_value=True):
        success, msg, name = FileService.get_file_name(1, 1)
        assert not success
        assert msg == "File not found"
        assert name is None


def test_create_file_exception(mock_db):
    """Test create_file returns error on exception."""
    mock_db.reset_mock()
    with patch(
        "app.services.file_service.sanitize_filename", return_value="test.md"
    ), patch("app.services.file_service.get_db") as mock_get_db:
        mock_db.execute_one.side_effect = [None, Exception("fail")]
        mock_get_db.return_value = mock_db
        success, msg, file_record = FileService.create_file("test.md", "content", 1)
        assert not success
        assert msg == "Failed to create file"
        assert file_record is None


def test_get_file_details_filenotfounderror(mock_db):
    """Test get_file_details returns error on FileNotFoundError."""
    mock_db.reset_mock()
    file_record_db = {
        "id": 1,
        "name": "test.md",
        "file_path": "/tmp/test.md",
        "file_size": 123,
        "mime_type": "text/markdown",
        "owner_id": 1,
        "team_id": None,
        "created_at": "2025-10-03T10:00:00",
        "updated_at": "2025-10-03T10:00:00",
    }
    mock_db.execute_one.return_value = file_record_db
    with patch("app.services.file_service.check_file_access", return_value=True), patch(
        "app.services.file_service.file_storage.read_file",
        side_effect=FileNotFoundError,
    ):
        success, msg, file_record = FileService.get_file_details(1, 1)
        assert not success
        assert msg == "File content not found"
        assert file_record is None


def test_get_file_details_exception(mock_db):
    """Test get_file_details returns error on generic exception."""
    mock_db.reset_mock()
    file_record_db = {
        "id": 1,
        "name": "test.md",
        "file_path": "/tmp/test.md",
        "file_size": 123,
        "mime_type": "text/markdown",
        "owner_id": 1,
        "team_id": None,
        "created_at": "2025-10-03T10:00:00",
        "updated_at": "2025-10-03T10:00:00",
    }
    mock_db.execute_one.return_value = file_record_db
    with patch("app.services.file_service.check_file_access", return_value=True), patch(
        "app.services.file_service.file_storage.read_file",
        side_effect=Exception("fail"),
    ):
        success, msg, file_record = FileService.get_file_details(1, 1)
        assert not success
        assert msg == "Failed to read file"
        assert file_record is None


def test_update_file_no_updates(mock_db):
    """Test update_file returns error if no updates provided."""
    mock_db.reset_mock()
    file_record = {
        "id": 1,
        "name": "old.md",
        "file_path": "/tmp/old.md",
        "owner_id": 1,
        "team_id": None,
    }
    mock_db.execute_one.return_value = file_record
    with patch("app.services.file_service.check_file_access", return_value=True):
        success, msg, file = FileService.update_file(1, 1)
        assert not success
        assert msg == "No updates provided"
        assert file is None


def test_update_file_invalid_name(mock_db):
    """Test update_file returns error if new name is invalid."""
    mock_db.reset_mock()
    file_record = {
        "id": 1,
        "name": "old.md",
        "file_path": "/tmp/old.md",
        "owner_id": 1,
        "team_id": None,
    }
    mock_db.execute_one.return_value = file_record
    with patch("app.services.file_service.check_file_access", return_value=True), patch(
        "app.services.file_service.sanitize_filename", return_value=None
    ):
        success, msg, file = FileService.update_file(1, 1, name="   ")
        assert not success
        assert msg == "Invalid file name"
        assert file is None


def test_update_file_exception(mock_db):
    """Test update_file returns error on exception."""
    mock_db.reset_mock()
    file_record = {
        "id": 1,
        "name": "old.md",
        "file_path": "/tmp/old.md",
        "owner_id": 1,
        "team_id": None,
    }
    mock_db.execute_one.return_value = file_record
    with patch("app.services.file_service.check_file_access", return_value=True), patch(
        "app.services.file_service.file_storage.save_file",
        side_effect=Exception("fail"),
    ):
        success, msg, file = FileService.update_file(1, 1, content="new content")
        assert not success
        assert msg == "Failed to update file"
        assert file is None


def test_delete_file_exception(mock_db):
    """Test delete_file returns error on exception."""
    mock_db.reset_mock()
    file_record = {"name": "test.md", "file_path": "/tmp/test.md"}
    mock_db.execute_one.return_value = file_record
    mock_db.execute_modify.return_value = 1
    with patch("app.services.file_service.check_file_access", return_value=True), patch(
        "app.services.file_service.file_storage.delete_file",
        side_effect=Exception("fail"),
    ):
        success, msg = FileService.delete_file(1, 1)
        assert not success
        assert msg == "Failed to delete file"


def test_get_file_content_filenotfounderror(mock_db):
    """Test get_file_content returns error on FileNotFoundError."""
    mock_db.reset_mock()
    file_record = {"name": "test.md", "file_path": "/tmp/test.md"}
    mock_db.execute_one.return_value = file_record
    with patch("app.services.file_service.check_file_access", return_value=True), patch(
        "app.services.file_service.file_storage.read_file",
        side_effect=FileNotFoundError,
    ):
        success, msg, content = FileService.get_file_content(1, 1)
        assert not success
        assert msg == "File content not found"
        assert content is None


def test_get_file_content_exception(mock_db):
    """Test get_file_content returns error on generic exception."""
    mock_db.reset_mock()
    file_record = {"name": "test.md", "file_path": "/tmp/test.md"}
    mock_db.execute_one.return_value = file_record
    with patch("app.services.file_service.check_file_access", return_value=True), patch(
        "app.services.file_service.file_storage.read_file",
        side_effect=Exception("fail"),
    ):
        success, msg, content = FileService.get_file_content(1, 1)
        assert not success
        assert msg == "Failed to read file content"
        assert content is None


def test_get_file_name_access_denied(mock_db):
    """Test get_file_name returns error if access denied."""
    mock_db.reset_mock()
    with patch("app.services.file_service.check_file_access", return_value=False):
        success, msg, name = FileService.get_file_name(1, 1)
        assert not success
        assert msg == "Access denied"
        assert name is None
