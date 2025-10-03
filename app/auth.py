"""
Authentication endpoints - refactored to use services.
"""

import logging
from flask import Blueprint, request
from app.response_format import format_error_response, format_success_response
from app.services.auth_service import AuthService

logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    """Register a new user."""
    try:
        data = request.get_json()
        if data is None:
            return format_error_response("Request body is required", 400)

        email = data.get("email", "").strip().lower()
        password = data.get("password", "")

        if not email or not password:
            return format_error_response("Email and password are required", 400)

        success, message, user_data = AuthService.register_user(email, password)

        if not success:
            # Only pass the error message, not user_data, to avoid serialization issues
            return format_error_response(message, 400)

        return format_success_response(user_data, message, 201)

    except Exception as e:
        print("REGISTER ENDPOINT ERROR:", repr(e))  # DEBUG
        logger.error("Registration error: %s", e)
        return format_error_response("Internal server error", 500)


@auth_bp.route("/login", methods=["POST"])
def login():
    """Authenticate user and return JWT token."""
    try:
        data = request.get_json()
        if not data:
            return format_error_response("Request body is required", 400)

        email = data.get("email", "").strip().lower()
        password = data.get("password", "")

        success, message, auth_data = AuthService.authenticate_user(email, password)

        if not success:
            return format_error_response(message, 401)

        return format_success_response(auth_data, message)

    except Exception as e:
        logger.error("Login error: %s", e)
        return format_error_response("Internal server error", 500)
