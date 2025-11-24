"""
Tests for file API endpoints.
"""

import json
from unittest.mock import patch


def test_list_files_success(client, mock_db, auth_headers):
    """Test listing files with authentication."""
    mock_db.reset_mock()
    # Mock database response for file listing
    mock_db.execute_query.return_value = [
        {
            "id": 1,
            "name": "test.md",
            "file_path": "/data/files/000/test.md",
            "file_size": 100,
            "mime_type": "text/markdown",
            "owner_id": 1,
            "team_id": None,
            "created_at": "2025-10-03T10:00:00",
            "updated_at": "2025-10-03T10:00:00",
        }
    ]
    with patch("app.services.auth_service.AuthService.verify_jwt") as mock_verify:
        mock_verify.return_value = {"user_id": 1, "email": "test@example.com"}
        response = client.get("/api/files", headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "files" in data
        assert isinstance(data["files"], list)
        assert len(data["files"]) == 1
        assert data["files"][0]["name"] == "test.md"
        assert data["files"][0]["id"] == 1
        # Verify database was called correctly
        mock_db.execute_query.assert_called_once()


def test_list_files_unauthorized(client):
    """Test file listing without authentication."""
    response = client.get("/api/files")

    assert response.status_code == 401
    data = json.loads(response.data)
    assert "error" in data
    assert "authorization" in data["error"].lower()


def test_get_file_success(client, mock_db, auth_headers):
    """Test getting a file successfully."""
    mock_db.reset_mock()
    # 1. Access check returns True (simulate by returning a non-None value)
    # 2. File record fetch returns the file dict
    file_record = {
        "id": 1,
        "name": "test.md",
        "file_path": "/data/files/000/test.md",
        "file_size": 100,
        "mime_type": "text/markdown",
        "owner_id": 1,
        "team_id": None,
        "created_at": "2025-10-03T10:00:00",
        "updated_at": "2025-10-03T10:00:00",
    }
    mock_db.execute_one.side_effect = [
        {"id": 1},  # access check result (simulate access granted)
        file_record,  # file fetch result
    ]
    with (
        patch("app.services.auth_service.AuthService.verify_jwt") as mock_verify,
        patch("app.services.file_service.file_storage.read_file") as mock_read_file,
        patch("app.services.file_service.log_activity") as mock_log_activity,
    ):
        mock_verify.return_value = {"user_id": 1, "email": "test@example.com"}
        mock_read_file.return_value = "# Test Content"
        response = client.get("/api/files/1", headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["name"] == "test.md"
        assert data["id"] == 1
        assert mock_db.execute_one.call_count == 2
        calls = mock_db.execute_one.call_args_list
        # First call: access check, second call: file fetch
        assert "SELECT f.id" in calls[0][0][0] or "team_members" in calls[0][0][0]
        assert "SELECT id, name, file_path" in calls[1][0][0]
        mock_read_file.assert_called_once_with("/data/files/000/test.md")
        mock_log_activity.assert_called_with(
            1, "file_viewed", "file", 1, "Viewed file: test.md"
        )


def test_get_nonexistent_file(client, mock_db, auth_headers):
    """Test getting a file that doesn't exist."""
    mock_db.reset_mock()
    # Simulate access granted, but file not found
    mock_db.execute_one.side_effect = [
        {"id": 1},  # access check result (simulate access granted)
        None,  # file fetch result (not found)
    ]
    with patch("app.services.auth_service.AuthService.verify_jwt") as mock_verify:
        mock_verify.return_value = {"user_id": 1, "email": "test@example.com"}
        response = client.get("/api/files/999", headers=auth_headers)
        assert response.status_code == 404
        data = json.loads(response.data)
        assert "error" in data
        assert "not found" in data["error"].lower()


def test_create_file_success(client, mock_db, auth_headers):
    """Test successful file creation."""
    mock_db.reset_mock()
    # Mock database responses for file creation in correct order:
    # 1. Duplicate file check (None = no duplicate)
    # 2. Insert file (returns new id)
    # 3. Get file record (returns file dict)
    mock_db.execute_one.side_effect = [
        None,  # duplicate file check
        {
            "id": 1,
            "name": "new_file.md",
            "file_path": "/data/files/000/new_file.md",
            "file_size": 50,
            "mime_type": "text/markdown",
            "owner_id": 1,
            "team_id": None,
            "created_at": "2025-10-03T10:00:00",
            "updated_at": "2025-10-03T10:00:00",
        },
    ]

    # Mock DB update call for file storage info
    mock_db.execute_modify.return_value = 1

    # Mock file storage at the correct import path
    with (
        patch("app.services.file_service.sanitize_filename") as mock_sanitize,
        patch(
            "app.services.file_service.file_storage.generate_file_path"
        ) as mock_generate_path,
        patch("app.services.file_service.file_storage.save_file") as mock_save_file,
        patch("app.services.file_service.log_activity") as mock_log_activity,
    ):
        mock_sanitize.return_value = "new_file.md"
        mock_generate_path.return_value = "/data/files/000/new_file.md"
        mock_save_file.return_value = (50, "checksum")

        # Mock JWT verification
        with patch("app.services.auth_service.AuthService.verify_jwt") as mock_verify:
            mock_verify.return_value = {"user_id": 1, "email": "test@example.com"}

            # Create test file data
            file_data = {"name": "new_file.md", "content": "# Test Markdown"}

            response = client.post(
                "/api/files",
                data=json.dumps(file_data),
                content_type="application/json",
                headers=auth_headers,
            )

            # Assert response
            assert response.status_code == 201
            data = json.loads(response.data)
            assert data["name"] == "new_file.md"
            assert data["id"] == 1

            # Verify database was called correctly
            assert mock_db.execute_one.call_count == 2
            calls = mock_db.execute_one.call_args_list
            # 1st call: duplicate check
            assert "SELECT id FROM files WHERE name =" in calls[0][0][0]
            # 2nd call: fetch file record
            assert "SELECT id, name, file_size" in calls[1][0][0]
            mock_save_file.assert_called_once()
            mock_log_activity.assert_called()


def test_create_file_missing_fields(client, auth_headers):
    """Test file creation with missing required fields."""
    # Mock JWT verification

    with patch("app.services.auth_service.AuthService.verify_jwt") as mock_verify:
        mock_verify.return_value = {"user_id": 1, "email": "test@example.com"}

        # Missing name field
        response = client.post(
            "/api/files",
            data=json.dumps({"content": "# Test"}),
            content_type="application/json",
            headers=auth_headers,
        )

        # Assert response
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
        assert "name" in data["error"].lower()


def test_update_file_success(client, mock_db, auth_headers):
    """Test successful file update with full DB and side-effect mocking."""
    mock_db.reset_mock()

    # Prepare mock DB responses for each call in the update flow
    file_before = {
        "id": 1,
        "name": "test.md",
        "file_path": "/data/files/000/test.md",
        "file_size": 100,
        "mime_type": "text/markdown",
        "owner_id": 1,
        "team_id": None,
        "created_at": "2025-10-03T10:00:00",
        "updated_at": "2025-10-03T10:00:00",
    }
    file_after = {
        "id": 1,
        "name": "updated.md",
        "file_path": "/data/files/000/updated.md",
        "file_size": 150,
        "mime_type": "text/markdown",
        "owner_id": 1,
        "team_id": None,
        "created_at": "2025-10-03T10:00:00",
        "updated_at": "2025-10-03T11:00:00",
    }
    # Each entry matches a DB call in the service logic
    mock_db.execute_one.side_effect = [
        file_before,  # 1. Get current file
        None,  # 2. Duplicate name check for update (no duplicate)
        file_after,  # 3. Fetch updated file record
    ]

    # Patch all side-effect functions used in the update flow
    with (
        patch("app.services.file_service.sanitize_filename") as mock_sanitize,
        patch("app.services.file_service.file_storage.save_file") as mock_save_file,
        patch("app.services.file_service.log_activity") as mock_log_activity,
        patch("app.services.file_service.check_file_access") as mock_check_access,
        patch("app.services.auth_service.AuthService.verify_jwt") as mock_verify,
    ):
        mock_sanitize.return_value = "updated.md"
        mock_save_file.return_value = (150, "checksum")
        mock_check_access.return_value = True
        mock_verify.return_value = {"user_id": 1, "email": "test@example.com"}

        update_data = {"name": "updated.md", "content": "# Updated Content"}
        response = client.patch(
            "/api/files/1",
            data=json.dumps(update_data),
            content_type="application/json",
            headers=auth_headers,
        )

        # Assert response is successful and correct
        if response.status_code != 200:
            print("DB call sequence:")
            for i, call in enumerate(mock_db.execute_one.call_args_list):
                print(f"Call {i + 1}: {call}")
            print("Response:", response.status_code, response.data.decode())
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["name"] == "updated.md"
        assert data["id"] == 1
        assert data["file_size"] == 150
        assert data["file_path"] == "/data/files/000/updated.md"

        # Verify DB call sequence and arguments
        assert mock_db.execute_one.call_count == 3
        calls = mock_db.execute_one.call_args_list
        # 1st call: get current file
        assert "SELECT id, name, file_path" in calls[0][0][0]
        # 2nd call: duplicate name check for update
        assert "SELECT id FROM files WHERE name =" in calls[1][0][0]
        # 3rd call: fetch updated file record
        assert "SELECT id, name, file_size" in calls[2][0][0]

        # Verify side-effect calls
        mock_save_file.assert_called_once()
        mock_log_activity.assert_called()


def test_update_nonexistent_file(client, mock_db, auth_headers):
    """Test updating a file that doesn't exist."""
    mock_db.reset_mock()
    # Mock database response for no file found
    mock_db.execute_one.return_value = None

    # Patch check_file_access to allow file existence check
    with (
        patch("app.services.file_service.check_file_access") as mock_check_access,
        patch("app.services.auth_service.AuthService.verify_jwt") as mock_verify,
    ):
        mock_check_access.return_value = True
        mock_verify.return_value = {"user_id": 1, "email": "test@example.com"}

        update_data = {"name": "updated.md", "content": "# Updated Content"}

        response = client.patch(
            "/api/files/999",
            data=json.dumps(update_data),
            content_type="application/json",
            headers=auth_headers,
        )

        # Assert response
        assert response.status_code == 404
        data = json.loads(response.data)
        assert "error" in data
        assert "not found" in data["error"].lower()


def test_delete_file_success(client, mock_db, auth_headers):
    """Test successful file deletion."""
    mock_db.reset_mock()
    # Mock database responses: access check, then file fetch
    mock_db.execute_one.side_effect = [
        {"id": 1},  # access check
        {
            "id": 1,
            "name": "test.md",
            "file_path": "/data/files/000/test.md",
            "file_size": 100,
            "mime_type": "text/markdown",
            "owner_id": 1,
            "team_id": None,
            "created_at": "2025-10-03T10:00:00",
            "updated_at": "2025-10-03T10:00:00",
        },
    ]

    # Mock file removal (file_storage.delete_file)
    with patch("app.file_storage.file_storage.delete_file") as mock_remove:
        mock_remove.return_value = True

        # Mock JWT verification
        with patch("app.services.auth_service.AuthService.verify_jwt") as mock_verify:
            mock_verify.return_value = {"user_id": 1, "email": "test@example.com"}

            response = client.delete("/api/files/1", headers=auth_headers)

            # Assert response
            assert response.status_code == 200
            data = json.loads(response.data)
            assert "success" in data["message"].lower()

            # Verify calls
            assert mock_db.execute_one.call_count == 2
            # Check that a DELETE FROM files call was made
            delete_calls = [
                call
                for call in mock_db.execute_modify.call_args_list
                if "DELETE FROM files" in call[0][0]
            ]
            assert delete_calls, "DELETE FROM files was not called"
            mock_remove.assert_called_once()


def test_get_file_content_success(client, mock_db, auth_headers):
    """Test getting file content."""
    mock_db.reset_mock()
    # Mock database responses: access check, file fetch, access check, name fetch
    mock_db.execute_one.side_effect = [
        {"id": 1},  # access check
        {
            "id": 1,
            "name": "test.md",
            "file_path": "/data/files/000/test.md",
            "file_size": 100,
            "mime_type": "text/markdown",
            "owner_id": 1,
            "team_id": None,
            "created_at": "2025-10-03T10:00:00",
            "updated_at": "2025-10-03T10:00:00",
        },
        {"id": 1},  # access check (for get_file_name)
        {"name": "test.md"},  # name fetch
    ]

    # Mock file reading (file_storage.read_file)
    with patch("app.file_storage.file_storage.read_file") as mock_read:
        mock_read.return_value = "# Test Markdown Content"

        # Mock JWT verification
        with patch("app.services.auth_service.AuthService.verify_jwt") as mock_verify:
            mock_verify.return_value = {"user_id": 1, "email": "test@example.com"}

            response = client.get("/api/files/1/content", headers=auth_headers)

            # Assert response
            assert response.status_code == 200
            # The endpoint returns JSON, not raw markdown
            data = json.loads(response.data)
            assert data["content"] == "# Test Markdown Content"
            assert data["name"] == "test.md"

            # Verify calls
            assert mock_db.execute_one.call_count == 4
            mock_read.assert_called_once()


def test_list_files(client, mock_db):
    """Test listing files with authentication."""
    mock_db.reset_mock()
    mock_db.execute_query.return_value = [
        {
            "id": 1,
            "name": "test.md",
            "file_path": "/data/files/000/test.md",
            "file_size": 100,
            "mime_type": "text/markdown",
            "owner_id": 1,
            "team_id": None,
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
        }
    ]
    with patch(
        "app.services.auth_service.AuthService.verify_jwt",
        return_value={"user_id": 1, "email": "test@example.com"},
    ):
        response = client.get(
            "/api/files", headers={"Authorization": "Bearer valid_token"}
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "files" in data
        assert isinstance(data["files"], list)
        assert len(data["files"]) == 1
        assert data["files"][0]["name"] == "test.md"
        assert data["files"][0]["id"] == 1


def test_create_file(client, mock_db):
    """Test creating a file with authentication."""
    mock_db.reset_mock()
    # Mock DB responses for file creation in correct order:
    # 1. Duplicate file check (None = no duplicate)
    # 2. Insert file (returns new id)
    # 3. Get file record (returns file dict)
    mock_db.execute_one.side_effect = [
        None,  # duplicate file check
        {
            "id": 1,
            "name": "test.md",
            "file_path": "/data/files/000/test.md",
            "file_size": 50,
            "mime_type": "text/markdown",
            "owner_id": 1,
            "team_id": None,
            "created_at": "2025-10-03T10:00:00",
            "updated_at": "2025-10-03T10:00:00",
        },
    ]
    mock_db.execute_modify.return_value = 1
    with (
        patch("app.services.file_service.sanitize_filename") as mock_sanitize,
        patch(
            "app.services.file_service.file_storage.generate_file_path"
        ) as mock_generate_path,
        patch("app.services.file_service.file_storage.save_file") as mock_save_file,
        patch("app.services.file_service.log_activity") as mock_log_activity,
        patch("app.services.auth_service.AuthService.verify_jwt") as mock_verify,
    ):
        mock_sanitize.return_value = "test.md"
        mock_generate_path.return_value = "/data/files/000/test.md"
        mock_save_file.return_value = (50, "checksum")
        mock_log_activity.return_value = None
        mock_verify.return_value = {"user_id": 1, "email": "test@example.com"}

        payload = {"name": "test.md", "content": "# Test"}
        response = client.post(
            "/api/files",
            data=json.dumps(payload),
            content_type="application/json",
            headers={"Authorization": "Bearer valid_token"},
        )
        assert response.status_code == 201
