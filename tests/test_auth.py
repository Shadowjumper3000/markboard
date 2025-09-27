"""
Unit tests for authentication functions.
"""

import pytest
import jwt
from datetime import datetime, timedelta, timezone
from app.auth import hash_password, verify_password, generate_jwt
from app.config import Config


class TestPasswordHashing:
    """Test password hashing and verification."""

    def test_hash_password(self):
        """Test password hashing."""
        password = "testpassword123"
        hashed = hash_password(password)

        assert hashed != password
        assert hashed.startswith("$2b$")
        assert len(hashed) > 50

    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        password = "testpassword123"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = hash_password(password)

        assert verify_password(wrong_password, hashed) is False

    def test_different_passwords_different_hashes(self):
        """Test that different passwords produce different hashes."""
        password1 = "testpassword123"
        password2 = "testpassword456"

        hash1 = hash_password(password1)
        hash2 = hash_password(password2)

        assert hash1 != hash2

    def test_same_password_different_hashes(self):
        """Test that same password produces different hashes (due to salt)."""
        password = "testpassword123"

        hash1 = hash_password(password)
        hash2 = hash_password(password)

        assert hash1 != hash2
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestJWTGeneration:
    """Test JWT token generation and validation."""

    def test_generate_jwt(self):
        """Test JWT token generation."""
        user_id = 1
        email = "test@example.com"

        token = generate_jwt(user_id, email)

        assert isinstance(token, str)
        assert len(token) > 100  # JWT tokens are typically long

    def test_jwt_payload(self):
        """Test JWT token contains correct payload."""
        user_id = 1
        email = "test@example.com"

        token = generate_jwt(user_id, email)
        payload = jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"])

        assert payload["user_id"] == user_id
        assert payload["email"] == email
        assert "iat" in payload
        assert "exp" in payload

    def test_jwt_expiry(self):
        """Test JWT token expiry time."""
        user_id = 1
        email = "test@example.com"

        token = generate_jwt(user_id, email)
        payload = jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"])

        # Check that expiry is approximately correct (within 1 minute)
        expected_exp = datetime.now(timezone.utc) + timedelta(
            hours=Config.JWT_EXPIRY_HOURS
        )
        actual_exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)

        diff = abs((expected_exp - actual_exp).total_seconds())
        assert diff < 60  # Should be within 1 minute

    def test_jwt_invalid_secret(self):
        """Test JWT validation with wrong secret."""
        user_id = 1
        email = "test@example.com"

        token = generate_jwt(user_id, email)

        with pytest.raises(jwt.InvalidTokenError):
            jwt.decode(token, "wrong-secret", algorithms=["HS256"])

    def test_jwt_expired_token(self):
        """Test expired JWT token validation."""
        # Create token with negative expiry (already expired)
        payload = {
            "user_id": 1,
            "email": "test@example.com",
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc)
            - timedelta(hours=1),  # Expired 1 hour ago
        }

        token = jwt.encode(payload, Config.JWT_SECRET, algorithm="HS256")

        with pytest.raises(jwt.ExpiredSignatureError):
            jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"])
