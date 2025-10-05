"""
Tests for the AuthService class.
This module contains test cases for password hashing, JWT handling, registration, and authentication logic.
"""

from datetime import datetime, timezone, timedelta
from unittest.mock import patch
import pytest
import jwt
from app.services.auth_service import AuthService
from app.config import Config


def test_hash_password(mock_db):
    """
    Test that password hashing returns a string different from the input and is verifiable.
    """
    mock_db.reset_mock()

    password = "SecurePass123!"
    hashed = AuthService.hash_password(password)

    # Check that result is a string and not equal to the input
    assert isinstance(hashed, str)
    assert hashed != password
    # Verify the hash works with the original password
    assert AuthService.verify_password(password, hashed)


def test_verify_password_success(mock_db):
    """
    Test password verification with the correct password returns True.
    """
    mock_db.reset_mock()

    password = "SecurePass123!"
    hashed = AuthService.hash_password(password)

    assert AuthService.verify_password(password, hashed) is True


def test_verify_password_failure(mock_db):
    """
    Test password verification with an incorrect password returns False.
    """
    mock_db.reset_mock()

    password = "SecurePass123!"
    wrong_password = "WrongPass123!"
    hashed = AuthService.hash_password(password)

    assert AuthService.verify_password(wrong_password, hashed) is False


def test_generate_jwt(mock_db):
    """
    Test JWT token generation and verify its payload content.
    """
    mock_db.reset_mock()

    user_id = 1
    email = "test@example.com"
    is_admin = False

    token = AuthService.generate_jwt(user_id, email, is_admin)

    # Verify token is a string
    assert isinstance(token, str)

    # Decode and verify token content
    payload = jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"])
    assert payload["user_id"] == user_id
    assert payload["email"] == email
    assert payload["is_admin"] == is_admin
    assert "iat" in payload
    assert "exp" in payload
    assert payload["exp"] > payload["iat"]


def test_verify_jwt_valid_token(mock_db):
    """
    Test JWT verification with a valid token returns correct payload.
    """
    mock_db.reset_mock()

    payload = {
        "user_id": 1,
        "email": "test@example.com",
        "is_admin": False,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
    }
    token = jwt.encode(payload, Config.JWT_SECRET, algorithm="HS256")

    result = AuthService.verify_jwt(token)

    assert result["user_id"] == payload["user_id"]
    assert result["email"] == payload["email"]
    assert result["is_admin"] == payload["is_admin"]


def test_verify_jwt_expired_token(mock_db):
    """
    Test JWT verification with an expired token raises ValueError.
    """
    mock_db.reset_mock()

    payload = {
        "user_id": 1,
        "email": "test@example.com",
        "is_admin": False,
        "iat": datetime.now(timezone.utc) - timedelta(hours=2),
        "exp": datetime.now(timezone.utc) - timedelta(hours=1),
    }
    token = jwt.encode(payload, Config.JWT_SECRET, algorithm="HS256")

    with pytest.raises(ValueError, match="Token has expired"):
        AuthService.verify_jwt(token)


def test_verify_jwt_invalid_token(mock_db):
    """
    Test JWT verification with an invalid token raises ValueError.
    """
    mock_db.reset_mock()

    with pytest.raises(ValueError, match="Invalid token"):
        AuthService.verify_jwt("invalid.token.string")


def test_register_user_success(mock_db):
    """
    Test successful user registration returns user data and success True.
    """
    mock_db.reset_mock()
    # First call: check user existence (returns None), second call: insert user (returns user dict)
    mock_db.execute_one.side_effect = [
        None,  # No existing user
        {
            "id": 1,
            "email": "test@example.com",
            "is_admin": False,
            "created_at": "2025-10-03T10:00:00",
        },
    ]

    success, _, user_data = AuthService.register_user(
        "test@example.com", "TestPassword123"
    )

    assert success
    assert user_data["email"] == "test@example.com"


def test_register_user_invalid_email(mock_db):
    """
    Test registration with invalid email returns error and does not call DB.
    """
    mock_db.reset_mock()

    email = "invalid_email"
    password = "SecurePass123!"

    success, message, user_data = AuthService.register_user(email, password)

    assert success is False
    assert "Invalid email address" in message
    assert user_data is None
    # Database should not be called
    mock_db.execute_one.assert_not_called()


def test_register_user_weak_password(mock_db):
    """
    Test registration with weak password returns error and does not call DB.
    """
    mock_db.reset_mock()

    email = "test@example.com"
    password = "weak"  # Too short

    success, message, user_data = AuthService.register_user(email, password)

    assert success is False
    assert user_data is None
    assert "Password must be at least 8 characters long" in message
    # Database should not be called
    mock_db.execute_one.assert_not_called()


def test_register_user_existing_email(mock_db):
    """
    Test registration with existing email returns error and does not create user.
    """
    mock_db.reset_mock()

    email = "existing@example.com"
    password = "SecurePass123!"

    # Mock existing user found in database - override the side_effect
    mock_db.execute_one.side_effect = None
    mock_db.execute_one.return_value = {"id": 1, "email": email}

    success, message, user_data = AuthService.register_user(email, password)

    assert success is False
    assert "Email already registered" in message
    assert user_data is None


def test_register_user_database_error(mock_db):
    """
    Test registration with a database error returns error and no user data.
    """
    mock_db.reset_mock()

    email = "test@example.com"
    password = "SecurePass123!"

    # Mock database responses - no existing user but error on insert
    mock_db.execute_one.side_effect = [
        None,  # No existing user
        Exception("Database error"),
    ]

    success, message, user_data = AuthService.register_user(email, password)

    assert success is False
    assert "Registration failed" in message
    assert user_data is None


def test_authenticate_user_success(mock_db):
    """
    Test successful user authentication returns user data and success True.
    """
    mock_db.reset_mock()
    # Mock user returned from DB (must include is_admin)
    mock_db.execute_one.return_value = {
        "id": 1,
        "email": "test@example.com",
        "password_hash": "hashed",
        "is_admin": False,
    }
    mock_db.execute_modify.return_value = 1  # Simulate DB update for last login

    # Patch log_activity and logger to avoid side effects and check calls
    with patch("app.services.auth_service.log_activity") as mock_log_activity, patch(
        "app.services.auth_service.logger"
    ):
        AuthService.verify_password = staticmethod(lambda pw, h: True)
        success, _, auth_data = AuthService.authenticate_user(
            "test@example.com", "TestPassword123"
        )

        assert success
        assert auth_data["user"]["email"] == "test@example.com"
        # Ensure log_activity was called for login
        mock_log_activity.assert_called_with(
            1, "user_login", "user", 1, "User logged in: test@example.com"
        )


def test_authenticate_user_nonexistent(mock_db):
    """
    Test authentication with a non-existent user returns error and no data.
    """
    mock_db.reset_mock()

    email = "nonexistent@example.com"
    password = "SecurePass123!"

    # Mock no user found
    mock_db.execute_one.return_value = None

    success, message, auth_data = AuthService.authenticate_user(email, password)

    assert success is False
    assert "Invalid email or password" in message
    assert auth_data is None


def test_authenticate_user_wrong_password(mock_db):
    """
    Test authentication with wrong password returns error and no data.
    """
    mock_db.reset_mock()

    email = "test@example.com"
    password = "WrongPassword123!"

    # Mock user found but wrong password
    mock_db.execute_one.return_value = {
        "id": 1,
        "email": email,
        "password_hash": "hashed_password",
        "is_admin": False,
    }

    with patch.object(AuthService, "verify_password", return_value=False):
        success, message, auth_data = AuthService.authenticate_user(email, password)

        assert success is False
        assert "Invalid email or password" in message
        assert auth_data is None


def test_authenticate_user_missing_fields(mock_db):
    """
    Test authentication with missing fields returns error and does not call DB.
    """
    mock_db.reset_mock()

    email = ""
    password = ""

    success, message, auth_data = AuthService.authenticate_user(email, password)

    assert success is False
    assert "Email and password are required" in message
    assert auth_data is None
    # Database should not be called
    mock_db.execute_one.assert_not_called()


def test_authenticate_user_database_error(mock_db):
    """
    Test authentication with a database error returns error and no data.
    """
    mock_db.reset_mock()

    email = "test@example.com"
    password = "SecurePass123!"

    # Mock database error
    mock_db.execute_one.side_effect = Exception("Database error")

    success, message, auth_data = AuthService.authenticate_user(email, password)

    assert success is False
    assert "Authentication failed" in message
    assert auth_data is None
