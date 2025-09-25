"""
Authentication endpoints and utilities.
"""

import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from flask import Blueprint, request, jsonify
from app.db import db
from app.config import Config
from app.utils import (
    validate_email,
    validate_password,
    log_activity,
    format_error_response,
    format_success_response,
)
import logging

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


def generate_jwt(user_id: int, email: str) -> str:
    """Generate JWT token for user."""
    payload = {
        "user_id": user_id,
        "email": email,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(hours=Config.JWT_EXPIRY_HOURS),
    }

    return jwt.encode(payload, Config.JWT_SECRET, algorithm="HS256")


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

        logger.info(f"New user created: {email} (ID: {user_id})")

        return format_success_response(
            {"user_id": user_id, "email": email}, "Account created successfully", 201
        )

    except Exception as e:
        logger.error(f"Signup error: {e}")
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
            "SELECT id, email, password_hash FROM users WHERE email = %s", (email,)
        )

        if not user or not verify_password(password, user["password_hash"]):
            # Log failed login attempt
            if user:
                log_activity(user["id"], "login_failed", "user", user["id"])
            return format_error_response("Invalid credentials", 401)

        # Generate JWT token
        token = generate_jwt(user["id"], user["email"])

        # Log successful login
        log_activity(user["id"], "login", "user", user["id"])

        logger.info(f"User logged in: {email} (ID: {user['id']})")

        return format_success_response(
            {"token": token, "user_id": user["id"], "email": user["email"]}
        )

    except Exception as e:
        logger.error(f"Login error: {e}")
        return format_error_response("Internal server error", 500)
