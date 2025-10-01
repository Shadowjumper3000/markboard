"""
Authentication endpoints and utilities.
"""
import logging
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from flask import Blueprint, request
from app.db import db
from app.config import Config
from app.utils import (
    validate_email,
    validate_password,
    log_activity,
    format_error_response,
    format_success_response,
)

logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    salt = bcrypt.gensalt(rounds=Config.BCRYPT_ROUNDS)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash."""
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def generate_jwt(user_id: int, email: str, is_admin: bool = False) -> str:
    """Generate JWT token for user."""
    payload = {
        "user_id": user_id,
        "email": email,
        "is_admin": is_admin,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(hours=Config.JWT_EXPIRY_HOURS),
    }

    return jwt.encode(payload, Config.JWT_SECRET, algorithm="HS256")


def verify_jwt(token: str) -> dict:
    """Verify and decode JWT token."""
    try:
        payload = jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError as exc:
        raise jwt.ExpiredSignatureError("Token has expired") from exc
    except jwt.InvalidTokenError as exc:
        raise jwt.InvalidTokenError("Invalid token") from exc


def get_current_user():
    """Get current user from JWT token in request header."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    token = auth_header.split(" ")[1]
    try:
        payload = verify_jwt(token)
        user = db.execute_one(
            "SELECT id, email, is_admin, created_at FROM users WHERE id = %s",
            (payload["user_id"],),
        )
        return user
    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        return None
    except jwt.InvalidTokenError:
        logger.warning("Invalid token")
        return None
    except Exception as e:
        logger.error("Unexpected error in get_current_user: %s", e)
        return None


@auth_bp.route("/signup", methods=["POST"])
def signup():
    """Create new user account."""
    try:
        data = request.get_json()

        if not data:
            return format_error_response("Request body required", 400)

        email = data.get("email", "").strip().lower()
        password = data.get("password", "")

        # Validation
        if not email or not password:
            return format_error_response("Email and password required", 400)

        if not validate_email(email):
            return format_error_response("Invalid email format", 400)

        is_valid, password_error = validate_password(password)
        if not is_valid:
            return format_error_response(password_error, 400)

        # Check if user already exists
        existing_user = db.execute_one(
            "SELECT id FROM users WHERE email = %s", (email,)
        )

        if existing_user:
            return format_error_response("Email already registered", 409)

        # Hash password and create user
        hashed_password = hash_password(password)

        user_id = db.execute_modify(
            "INSERT INTO users (email, password_hash, is_admin, created_at) VALUES (%s, %s, %s, %s)",
            (email, hashed_password, False, datetime.now(timezone.utc)),
        )

        # Log signup activity
        log_activity(user_id, "signup", "user", user_id)

        logger.info("New user created: %s (ID: %s)", email, user_id)

        return format_success_response(
            {"user_id": user_id, "email": email}, "Account created successfully", 201
        )

    except Exception as e:
        logger.error("Signup error: %s", e)
        return format_error_response("Internal server error", 500)


@auth_bp.route("/login", methods=["POST"])
def login():
    """Authenticate user and return JWT token."""
    try:
        data = request.get_json()

        if not data:
            return format_error_response("Request body required", 400)

        email = data.get("email", "").strip().lower()
        password = data.get("password", "")

        if not email or not password:
            return format_error_response("Email and password required", 400)

        # Find user
        user = db.execute_one(
            "SELECT id, email, password_hash, is_admin FROM users WHERE email = %s",
            (email,),
        )

        if not user or not verify_password(password, user["password_hash"]):
            # Log failed login attempt
            if user:
                log_activity(user["id"], "login_failed", "user", user["id"])
            return format_error_response("Invalid credentials", 401)

        # Generate JWT token
        token = generate_jwt(user["id"], user["email"], user["is_admin"])

        # Log successful login
        log_activity(user["id"], "login", "user", user["id"])

        logger.info("User logged in: %s (ID: %s)", email, user["id"])

        return format_success_response(
            {
                "token": token,
                "user_id": user["id"],
                "email": user["email"],
                "is_admin": user["is_admin"],
            }
        )
    except KeyError as e:
        logger.error("Missing key in request data: %s", e)
        return format_error_response("Invalid request data", 400)
    except ValueError as e:
        logger.error("Value error: %s", e)
        return format_error_response("Invalid input", 400)
    except Exception as e:
        logger.error("Unexpected login error: %s", e)
        return format_error_response("Internal server error", 500)


@auth_bp.route("/me", methods=["GET"])
def get_me():
    """Get current user information from JWT token."""
    try:
        user = get_current_user()
        if not user:
            return format_error_response("Authentication required", 401)

        return format_success_response(
            {
                "id": user["id"],
                "email": user["email"],
                "is_admin": user["is_admin"],
                "created_at": (
                    user["created_at"].isoformat() if user["created_at"] else None
                ),
            }
        )

    except KeyError as e:
        logger.error("Missing key in user data: %s", e)
        return format_error_response("Invalid user data", 400)
    except ValueError as e:
        logger.error("Value error in user data: %s", e)
        return format_error_response("Invalid input", 400)
    except jwt.ExpiredSignatureError as e:
        logger.error("Token has expired: %s", e)
        return format_error_response("Token has expired", 401)
    except jwt.InvalidTokenError as e:
        logger.error("Invalid token: %s", e)
        return format_error_response("Invalid token", 401)
    except Exception as e:
        logger.error("Unexpected error in get_me: %s", e)
        return format_error_response("Internal server error", 500)
