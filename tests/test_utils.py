"""
Unit tests for utility functions.
"""

import pytest
from app.utils import validate_email, validate_password, sanitize_filename


class TestValidation:
    """Test validation functions."""

    def test_validate_email_valid(self):
        """Test email validation with valid emails."""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.org",
            "firstname.lastname@company.com",
        ]

        for email in valid_emails:
            assert validate_email(email) is True

    def test_validate_email_invalid(self):
        """Test email validation with invalid emails."""
        invalid_emails = [
            "invalid-email",
            "@example.com",
            "test@",
            "test.example.com",
            "test@example",
            "",
            "test@.com",
        ]

        for email in invalid_emails:
            assert validate_email(email) is False

    def test_validate_password_valid(self):
        """Test password validation with valid passwords."""
        valid_passwords = [
            "TestPassword123",
            "MySecurePass1",
            "Complex@Pass2024",
            "Aa1bcdef",  # Minimum requirements met
        ]

        for password in valid_passwords:
            is_valid, error = validate_password(password)
            assert is_valid is True
            assert error is None

    def test_validate_password_too_short(self):
        """Test password validation with too short password."""
        is_valid, error = validate_password("Short1")
        assert is_valid is False
        assert "at least 8 characters" in error

    def test_validate_password_no_uppercase(self):
        """Test password validation without uppercase letter."""
        is_valid, error = validate_password("lowercase123")
        assert is_valid is False
        assert "uppercase letter" in error

    def test_validate_password_no_lowercase(self):
        """Test password validation without lowercase letter."""
        is_valid, error = validate_password("UPPERCASE123")
        assert is_valid is False
        assert "lowercase letter" in error

    def test_validate_password_no_digit(self):
        """Test password validation without digit."""
        is_valid, error = validate_password("NoDigitPassword")
        assert is_valid is False
        assert "digit" in error


class TestFilenamesanitization:
    """Test filename sanitization."""

    def test_sanitize_filename_normal(self):
        """Test sanitization of normal filenames."""
        assert sanitize_filename("test.md") == "test.md"
        assert sanitize_filename("my-file.txt") == "my-file.txt"
        assert sanitize_filename("document_v1.2.md") == "document_v1.2.md"

    def test_sanitize_filename_dangerous_chars(self):
        """Test sanitization of filenames with dangerous characters."""
        assert sanitize_filename("../../../etc/passwd") == "etcpasswd"
        assert (
            sanitize_filename("file<script>evil</script>.md")
            == "filescriptevilscript.md"
        )
        assert sanitize_filename("file|with|pipes.txt") == "filewithpipes.txt"

    def test_sanitize_filename_leading_trailing_dots(self):
        """Test sanitization removes leading/trailing dots and spaces."""
        assert sanitize_filename("...hidden-file.txt...") == "hidden-file.txt"
        assert sanitize_filename("  spaced-file.md  ") == "spaced-file.md"
        assert sanitize_filename(".....") == "untitled"

    def test_sanitize_filename_empty(self):
        """Test sanitization of empty or invalid filenames."""
        assert sanitize_filename("") == "untitled"
        assert sanitize_filename("   ") == "untitled"
        assert sanitize_filename("!@#$%^&*()") == "untitled"

    def test_sanitize_filename_length_limit(self):
        """Test filename length limitation."""
        long_name = "a" * 300
        sanitized = sanitize_filename(long_name)
        assert len(sanitized) <= 255
