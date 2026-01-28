"""
Authentication service - handles auth business logic.
Refactored to follow Single Responsibility Principle.
Uses external services for password and JWT operations.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Optional, Tuple

from app.utils.activity_logger import log_activity
from app.infrastructure.database.connection import get_db
from app.infrastructure.security.jwt_service import JwtService
from app.infrastructure.security.password_service import PasswordService
from app.utils.validators import validate_email, validate_password

logger = logging.getLogger(__name__)


class AuthService:
    """Service class for authentication business logic."""

    @staticmethod
    def register_user(email: str, password: str) -> Tuple[bool, str, Optional[Dict]]:
        """Register a new user."""
        # Validate email
        if not validate_email(email):
            return False, "Invalid email address", None

        # Validate password
        is_valid, error_msg = validate_password(password)
        if not is_valid:
            return False, error_msg, None

        # Check if email already exists
        existing_user = get_db().execute_one(
            "SELECT id FROM users WHERE email = %s", (email,)
        )

        if existing_user:
            return False, "Email already registered", None

        try:
            # Hash password
            password_hash = PasswordService.hash_password(password)

            # Insert user
            insert_query = """
                INSERT INTO users (email, password_hash, created_at)
                VALUES (%s, %s, %s)
            """
            user_id = get_db().execute_modify(
                insert_query, (email, password_hash, datetime.now(timezone.utc))
            )

            # Fetch the inserted user
            user_result = get_db().execute_one(
                "SELECT id, email, is_admin, created_at FROM users WHERE id = %s",
                (user_id,),
            )

            if not user_result:
                return False, "Failed to fetch new user", None

            # Log activity
            log_activity(
                user_id, "user_created", "user", user_id, f"User {email} registered"
            )

            return True, "User registered successfully", user_result

        except Exception as e:
            logger.error(f"Error registering user: {e}")
            return False, "Registration failed", None

    @staticmethod
    def authenticate_user(
        email: str, password: str
    ) -> Tuple[bool, str, Optional[Dict]]:
        """Authenticate user with email and password."""
        if not email or not password:
            return False, "Email and password are required", None

        try:
            # Get user from database
            user = get_db().execute_one(
                "SELECT id, email, password_hash, is_admin FROM users WHERE email = %s",
                (email,),
            )

            if not user:
                return False, "Invalid email or password", None

            # Verify password
            if not PasswordService.verify_password(password, user["password_hash"]):
                return False, "Invalid email or password", None

            # Update last login
            get_db().execute_modify(
                "UPDATE users SET last_login = %s WHERE id = %s",
                (datetime.now(timezone.utc), user["id"]),
            )

            # Generate JWT token
            token = JwtService.generate_token(
                user["id"], user["email"], user["is_admin"]
            )

            # Log activity
            log_activity(
                user["id"], "user_login", "user", user["id"], f"User {email} logged in"
            )

            return (
                True,
                "Login successful",
                {
                    "token": token,
                    "user": {
                        "id": user["id"],
                        "email": user["email"],
                        "is_admin": user["is_admin"],
                    },
                },
            )

        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            return False, "Authentication failed", None

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using the password service."""
        return PasswordService.hash_password(password)

    @staticmethod
    def get_user_by_id(user_id: int) -> Tuple[bool, str, Optional[Dict]]:
        """Get user information by ID."""
        try:
            user = get_db().execute_one(
                "SELECT id, email, is_admin, created_at, last_login FROM users WHERE id = %s",
                (user_id,),
            )

            if not user:
                return False, "User not found", None

            return (
                True,
                "User found",
                {
                    "id": user["id"],
                    "email": user["email"],
                    "is_admin": user["is_admin"],
                    "created_at": user["created_at"],
                    "last_login": user["last_login"],
                },
            )

        except Exception as e:
            logger.error(f"Error fetching user by ID: {e}")
            return False, "Failed to fetch user", None

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify a password against a hash."""
        return PasswordService.verify_password(password, password_hash)

    @staticmethod
    def generate_jwt(user_id: int, email: str, is_admin: bool = False) -> str:
        """Generate a JWT token."""
        return JwtService.generate_token(user_id, email, is_admin)

    @staticmethod
    def verify_jwt(token: str) -> Dict:
        """Verify a JWT token and return the payload."""
        return JwtService.verify_token(token)
