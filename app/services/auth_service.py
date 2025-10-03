"""
Authentication service - handles auth-related business logic.
Follows Single Responsibility Principle.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Tuple
from functools import wraps
from flask import jsonify, g, request
import bcrypt
import jwt
from app.db import get_db
from app.config import Config
from app.validation import validate_email, validate_password
from app.activity import log_activity


logger = logging.getLogger(__name__)


class AuthService:
    """Service class for authentication operations."""

    @staticmethod
    def require_auth(f):
        """Decorator to require authentication for endpoints."""

        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth_header = request.headers.get("Authorization")

            if not auth_header:
                return jsonify({"error": "Authorization header required"}), 401

            try:
                # Extract token from "Bearer <token>"
                token = auth_header.split(" ")[1]
                payload = AuthService.verify_jwt(token)

                # Store user info in Flask's g object for use in the view
                g.current_user_id = payload["user_id"]
                g.current_user_email = payload["email"]

            except IndexError:
                return jsonify({"error": "Invalid authorization header format"}), 401
            except ValueError as e:
                # AuthService.verify_jwt raises ValueError for expired/invalid tokens
                return jsonify({"error": str(e)}), 401
            except Exception as e:
                logger.error("Auth error: %s", e)
                return jsonify({"error": "Authentication failed"}), 401

            return f(*args, **kwargs)

        return decorated_function

    @staticmethod
    def require_admin(f):
        """Decorator to require admin privileges for endpoints."""

        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Check if current user is admin
                user = get_db().execute_one(
                    "SELECT is_admin FROM users WHERE id = %s", (g.current_user_id,)
                )

                if not user or not user["is_admin"]:
                    return jsonify({"error": "Admin privileges required"}), 403

            except Exception as e:
                logger.error("Admin check error: %s", e)
                return jsonify({"error": "Authorization check failed"}), 500

            return f(*args, **kwargs)

        return decorated_function

    """Service class for authentication operations."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt."""
        salt = bcrypt.gensalt(rounds=Config.BCRYPT_ROUNDS)
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify password against hash."""
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))

    @staticmethod
    def generate_jwt(user_id: int, email: str, is_admin: bool = False) -> str:
        """Generate JWT token for user."""
        payload = {
            "user_id": user_id,
            "email": email,
            "is_admin": is_admin,
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc)
            + timedelta(hours=Config.JWT_EXPIRY_HOURS),
        }
        return jwt.encode(payload, Config.JWT_SECRET, algorithm="HS256")

    @staticmethod
    def verify_jwt(token: str) -> Dict:
        """Verify and decode JWT token."""
        try:
            payload = jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError as exc:
            raise ValueError("Token has expired") from exc
        except jwt.InvalidTokenError as exc:
            raise ValueError("Invalid token") from exc

    @staticmethod
    def register_user(email: str, password: str) -> Tuple[bool, str, Optional[Dict]]:
        """Register a new user."""
        # Validate email
        if not validate_email(email):
            return False, "Invalid email format", None

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
            password_hash = AuthService.hash_password(password)

            # Insert user
            user_result = get_db().execute_one(
                """
                INSERT INTO users (email, password_hash, created_at)
                VALUES (%s, %s, %s)
                RETURNING id, email, is_admin, created_at
                """,
                (email, password_hash, datetime.now(timezone.utc)),
            )

            if not user_result:
                logger.error("User insert failed: No user returned from DB.")
                return False, "Registration failed", None

            # Log activity
            log_activity(
                user_result["id"],
                "user_registered",
                "user",
                user_result["id"],
                f"User registered: {email}",
            )

            return True, "User registered successfully", user_result

        except Exception as e:
            logger.error("Error registering user: %s", e)
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
            if not AuthService.verify_password(password, user["password_hash"]):
                return False, "Invalid email or password", None

            # Update last login
            get_db().execute_modify(
                "UPDATE users SET last_login = %s WHERE id = %s",
                (datetime.now(timezone.utc), user["id"]),
            )

            # Generate JWT token
            token = AuthService.generate_jwt(
                user["id"], user["email"], user["is_admin"]
            )

            # Log activity
            log_activity(
                user["id"], "user_login", "user", user["id"], f"User logged in: {email}"
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
            logger.error("Error during authentication: %s", e)
            return False, "Authentication failed", None
