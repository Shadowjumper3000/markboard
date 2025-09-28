"""
Integration tests for API endpoints.
"""

import pytest
import json
from unittest.mock import patch, MagicMock


class TestAuthEndpoints:
    """Test authentication endpoints."""

    def test_signup_success(self, client):
        """Test successful user signup."""
        with patch("app.auth.db") as mock_db:
            # Mock database responses
            mock_db.execute_one.return_value = None  # No existing user
            mock_db.execute_modify.return_value = 1  # New user ID

            response = client.post(
                "/auth/signup",
                data=json.dumps(
                    {"email": "test@example.com", "password": "TestPassword123"}
                ),
                content_type="application/json",
            )

            assert response.status_code == 201
            data = json.loads(response.data)
            assert data["user_id"] == 1
            assert data["email"] == "test@example.com"

    def test_signup_missing_data(self, client):
        """Test signup with missing data."""
        response = client.post(
            "/auth/signup", data=json.dumps({}), content_type="application/json"
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data

    def test_signup_invalid_email(self, client):
        """Test signup with invalid email."""
        response = client.post(
            "/auth/signup",
            data=json.dumps({"email": "invalid-email", "password": "TestPassword123"}),
            content_type="application/json",
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data

    def test_signup_weak_password(self, client):
        """Test signup with weak password."""
        response = client.post(
            "/auth/signup",
            data=json.dumps({"email": "test@example.com", "password": "weak"}),
            content_type="application/json",
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data

    def test_signup_existing_user(self, client):
        """Test signup with existing email."""
        with patch("app.auth.db") as mock_db:
            # Mock existing user
            mock_db.execute_one.return_value = {"id": 1}

            response = client.post(
                "/auth/signup",
                data=json.dumps(
                    {"email": "existing@example.com", "password": "TestPassword123"}
                ),
                content_type="application/json",
            )

            assert response.status_code == 409
            data = json.loads(response.data)
            assert "error" in data

    def test_login_success(self, client):
        """Test successful login."""
        with patch("app.auth.db") as mock_db, patch(
            "app.auth.verify_password"
        ) as mock_verify:

            # Mock database and password verification
            mock_db.execute_one.return_value = {
                "id": 1,
                "email": "test@example.com",
                "password_hash": "hashed_password",
                "is_admin": False,
            }
            mock_verify.return_value = True

            response = client.post(
                "/auth/login",
                data=json.dumps(
                    {"email": "test@example.com", "password": "TestPassword123"}
                ),
                content_type="application/json",
            )

            assert response.status_code == 200
            data = json.loads(response.data)
            assert "token" in data
            assert data["user_id"] == 1
            assert data["email"] == "test@example.com"

    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials."""
        with patch("app.auth.db") as mock_db:
            # Mock no user found
            mock_db.execute_one.return_value = None

            response = client.post(
                "/auth/login",
                data=json.dumps(
                    {"email": "nonexistent@example.com", "password": "TestPassword123"}
                ),
                content_type="application/json",
            )

            assert response.status_code == 401
            data = json.loads(response.data)
            assert "error" in data

    def test_login_wrong_password(self, client):
        """Test login with wrong password."""
        with patch("app.auth.db") as mock_db, patch(
            "app.auth.verify_password"
        ) as mock_verify:

            # Mock user exists but wrong password
            mock_db.execute_one.return_value = {
                "id": 1,
                "email": "test@example.com",
                "password_hash": "hashed_password",
            }
            mock_verify.return_value = False

            response = client.post(
                "/auth/login",
                data=json.dumps(
                    {"email": "test@example.com", "password": "WrongPassword123"}
                ),
                content_type="application/json",
            )

            assert response.status_code == 401
            data = json.loads(response.data)
            assert "error" in data


class TestFileEndpoints:
    """Test file management endpoints."""

    def test_list_files_unauthorized(self, client):
        """Test listing files without authentication."""
        response = client.get("/files")
        assert response.status_code == 401

    def test_list_files_success(self, client):
        """Test successful file listing."""
        with patch("app.utils.jwt.decode") as mock_decode, patch(
            "app.files.db"
        ) as mock_db:

            # Mock JWT verification
            mock_decode.return_value = {"user_id": 1, "email": "test@example.com"}

            # Mock database response with datetime objects
            from datetime import datetime

            test_datetime = datetime.fromisoformat("2024-01-01T00:00:00")
            mock_db.execute_query.return_value = [
                {
                    "id": 1,
                    "name": "test.md",
                    "created_at": test_datetime.strftime("%Y-%m-%dT%H:%M:%S"),
                    "updated_at": test_datetime.strftime("%Y-%m-%dT%H:%M:%S"),
                    "owner_id": 1,
                    "team_id": None,
                }
            ]

            response = client.get(
                "/files", headers={"Authorization": "Bearer valid_token"}
            )

            assert response.status_code == 200
            data = json.loads(response.data)
            assert "files" in data
            assert len(data["files"]) == 1

    def test_create_file_success(self, client):
        """Test successful file creation."""
        with patch("app.utils.jwt.decode") as mock_decode, patch(
            "app.files.db"
        ) as mock_db:

            # Mock JWT verification
            mock_decode.return_value = {"user_id": 1, "email": "test@example.com"}

            # Mock database response
            mock_db.execute_modify.return_value = 1  # New file ID

            response = client.post(
                "/files",
                data=json.dumps(
                    {"name": "test.md", "content": "# Test File", "team_id": None}
                ),
                content_type="application/json",
                headers={"Authorization": "Bearer valid_token"},
            )

            assert response.status_code == 201
            data = json.loads(response.data)
            assert data["id"] == 1
            assert data["name"] == "test.md"

    def test_create_file_missing_name(self, client):
        """Test file creation with missing name."""
        with patch("app.utils.jwt.decode") as mock_decode:
            # Mock JWT verification
            mock_decode.return_value = {"user_id": 1, "email": "test@example.com"}

            response = client.post(
                "/files",
                data=json.dumps({"content": "# Test File"}),
                content_type="application/json",
                headers={"Authorization": "Bearer valid_token"},
            )

            assert response.status_code == 400
            data = json.loads(response.data)
            assert "error" in data


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_check_success(self, client):
        """Test successful health check."""
        with patch("app.main.db.test_connection") as mock_test:
            mock_test.return_value = True

            response = client.get("/health")

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["status"] == "healthy"
            assert data["database"] == "connected"

    def test_health_check_db_failure(self, client):
        """Test health check with database failure."""
        with patch("app.main.db.test_connection") as mock_test:
            mock_test.return_value = False

            response = client.get("/health")

            assert response.status_code == 503
            data = json.loads(response.data)
            assert data["status"] == "unhealthy"
            assert data["database"] == "disconnected"
