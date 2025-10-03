"""
Tests for validation utilities.
"""

import pytest


@pytest.mark.parametrize(
    "email,expected",
    [
        ("valid@example.com", True),
        ("user.name@domain.co.uk", True),
        ("user-name123@subdomain.domain.com", True),
        ("", False),
        ("invalid", False),
        ("invalid@", False),
        ("invalid@domain", False),
        ("invalid@domain.", False),
        ("@domain.com", False),
    ],
)
def test_validate_email(email, expected):
    """Test email validation."""
    from app.validation import validate_email

    assert validate_email(email) == expected


@pytest.mark.parametrize(
    "password,valid,error",
    [
        ("SecurePass123!", True, None),
        ("Password123", True, None),
        ("", False, "Password is required"),
        ("short", False, "Password must be at least 8 characters long"),
        (
            "lowercase123",
            False,
            "Password must contain at least one uppercase letter",
        ),
        (
            "UPPERCASE123",
            False,
            "Password must contain at least one lowercase letter",
        ),
        ("NoDigitsHere", False, "Password must contain at least one digit"),
    ],
)
def test_validate_password(password, valid, error):
    """Test password validation."""
    from app.validation import validate_password

    is_valid, error_message = validate_password(password)
    assert is_valid == valid
    assert error_message == error
