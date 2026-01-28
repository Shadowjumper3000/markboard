"""
Authentication middleware decorators for Flask.
Separated from service logic following Separation of Concerns.
"""

import logging
from functools import wraps

from flask import g, jsonify, request

from app.infrastructure.database.connection import get_db
from app.infrastructure.security.jwt_service import JwtService

logger = logging.getLogger(__name__)


def verify_jwt(token: str):
    """Wrapper for JwtService.verify_token for testing."""
    return JwtService.verify_token(token)


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
            payload = verify_jwt(token)

            # Store user info in Flask's g object for use in the view
            g.current_user_id = payload["user_id"]
            g.current_user_email = payload["email"]

        except IndexError:
            return jsonify({"error": "Invalid authorization header format"}), 401
        except ValueError as e:
            return jsonify({"error": str(e)}), 401
        except Exception as e:
            logger.error("Auth error: %s", e)
            return jsonify({"error": "Authentication failed"}), 401

        return f(*args, **kwargs)

    return decorated_function


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
