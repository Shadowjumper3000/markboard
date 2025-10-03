"""
Tests for authentication API endpoints.
"""

import json
from unittest.mock import patch


class TestAuthAPI:
    """Test case for auth API endpoints."""

    def test_register_success(self, mock_db):
        """Test successful user registration through the service."""
        mock_db.reset_mock()
        mock_db.execute_one.side_effect = None
        mock_db.execute_one.return_value = None
        from app.services.auth_service import AuthService  # Import here, after patching

        # Mock database response for successful registration
        mock_db.execute_one.side_effect = [
            None,  # for checking existing user
            {
                "id": 1,
                "email": "test@example.com",
                "is_admin": False,
                "created_at": "2025-10-03T10:10:00",
            },
        ]

        # Mock activity logging
        with patch("app.services.auth_service.log_activity") as mock_log:
            # Call the service directly
            success, message, user_data = AuthService.register_user(
                "test@example.com", "SecurePass123!"
            )

            # Assert the service response
            print(user_data)
            assert success is True
            assert message == "User registered successfully"
            assert user_data["id"] == 1
            assert user_data["email"] == "test@example.com"
            assert "is_admin" in user_data

            # Verify database was called correctly
            assert mock_db.execute_one.call_count >= 2
            mock_log.assert_called_once()

    def test_register_invalid_email(self, client, mock_db):
        """Test registration with invalid email format."""
        mock_db.reset_mock()
        mock_db.execute_one.side_effect = None
        mock_db.execute_one.return_value = None

        response = client.post(
            "/auth/register",
            data=json.dumps({"email": "invalid_email", "password": "SecurePass123!"}),
            content_type="application/json",
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
        assert "Invalid email format" in data["error"]

    def test_register_weak_password(self, client, mock_db):
        """Test registration with weak password."""
        mock_db.reset_mock()
        mock_db.execute_one.side_effect = None
        mock_db.execute_one.return_value = None

        response = client.post(
            "/auth/register",
            data=json.dumps(
                {"email": "test@example.com", "password": "weak"}  # Too short password
            ),
            content_type="application/json",
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data

    def test_register_duplicate_email(self, client, mock_db):
        """Test registration with already registered email."""
        mock_db.reset_mock()
        # Always return a user for any call to execute_one
        mock_db.execute_one.side_effect = None
        mock_db.execute_one.return_value = {
            "id": 1,
            "email": "test@example.com",
            "is_admin": False,
            "created_at": "2025-10-03T10:10:00",
        }

        response = client.post(
            "/auth/register",
            data=json.dumps(
                {"email": "test@example.com", "password": "SecurePass123!"}
            ),
            content_type="application/json",
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
        assert "Email already registered" in data["error"]

    def test_register_missing_fields(self, client, mock_db):
        """Test registration with missing fields."""
        mock_db.reset_mock()
        mock_db.execute_one.side_effect = None
        mock_db.execute_one.return_value = None

        response = client.post(
            "/auth/register", data=json.dumps({}), content_type="application/json"
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
        assert "Email and password are required" in data["error"]

    def test_login_success(self, mock_db):
        """Test successful login through the service."""
        mock_db.reset_mock()
        mock_db.execute_one.side_effect = None
        # Return a valid user dict for user lookup
        mock_db.execute_one.return_value = {
            "id": 1,
            "email": "test@example.com",
            "password_hash": "hashed_password",
            "is_admin": False,
        }
        mock_db.execute_modify.return_value = 1  # Simulate successful last login update
        from app.services.auth_service import AuthService  # Import here, after patching

        # Mock password verification and token generation
        with patch.object(AuthService, "verify_password", return_value=True):
            with patch.object(AuthService, "generate_jwt", return_value="test_token"):
                with patch("app.services.auth_service.log_activity") as mock_log:
                    # Call the service directly
                    success, message, auth_data = AuthService.authenticate_user(
                        "test@example.com", "SecurePass123!"
                    )

                    # Assert the service response
                    assert success is True
                    assert message == "Login successful"
                    assert "token" in auth_data
                    assert "user" in auth_data
                    assert auth_data["user"]["id"] == 1
                    assert auth_data["user"]["email"] == "test@example.com"
                    assert auth_data["token"] == "test_token"

                    # Verify activity was logged
                    mock_log.assert_called_once()

    def test_login_invalid_credentials(self, client, mock_db):
        mock_db.reset_mock()
        """Test login with invalid credentials."""
        mock_db.execute_one.side_effect = None
        mock_db.execute_one.return_value = {
            "id": 1,
            "email": "test@example.com",
            "password_hash": "hashed_password",
            "is_admin": False,
        }
        from app.services.auth_service import AuthService  # Import here, after patching

        with patch.object(AuthService, "verify_password", return_value=False):
            response = client.post(
                "/auth/login",
                data=json.dumps(
                    {"email": "test@example.com", "password": "WrongPassword123!"}
                ),
                content_type="application/json",
            )

            assert response.status_code == 401
            data = json.loads(response.data)
            assert "error" in data
            assert "Invalid email or password" in data["error"]

    def test_login_nonexistent_user(self, client, mock_db):
        mock_db.reset_mock()
        """Test login with non-existent user."""
        mock_db.execute_one.side_effect = None
        mock_db.execute_one.return_value = None

        response = client.post(
            "/auth/login",
            data=json.dumps(
                {"email": "nonexistent@example.com", "password": "SecurePass123!"}
            ),
            content_type="application/json",
        )

        assert response.status_code == 401
        data = json.loads(response.data)
        assert "error" in data
        assert "Invalid email or password" in data["error"]

    def test_login_missing_fields(self, client, mock_db):
        mock_db.reset_mock()
        """Test login with missing fields."""
        mock_db.execute_one.side_effect = None
        mock_db.execute_one.return_value = None

        response = client.post(
            "/auth/login", data=json.dumps({}), content_type="application/json"
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
        assert "Request body is required" in data["error"]

    def test_login_db_error(self, client, mock_db):
        mock_db.reset_mock()
        """Test login when database throws an error."""
        mock_db.execute_one.side_effect = Exception("Database error")
        mock_db.execute_one.return_value = None

        response = client.post(
            "/auth/login",
            data=json.dumps(
                {"email": "test@example.com", "password": "SecurePass123!"}
            ),
            content_type="application/json",
        )

        assert response.status_code == 401
        data = json.loads(response.data)
        assert "error" in data
        assert "Authentication failed" in data["error"]
