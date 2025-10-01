"""
Utility functions for the application.
"""

import re
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from functools import wraps
from flask import request, jsonify, g
import jwt
from app.config import Config
from app.db import db


logger = logging.getLogger(__name__)


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_password(password: str) -> tuple[bool, Optional[str]]:
    """
    Validate password strength.
    Returns (is_valid, error_message).
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"

    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"

    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit"

    return True, None


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent directory traversal."""
    # Remove path separators and keep only safe characters
    sanitized = re.sub(r"[^\w\s.-]", "", filename)
    # Remove leading/trailing dots and spaces
    sanitized = sanitized.strip(". ")
    # Limit length
    return sanitized[:255] if sanitized else "untitled"


def log_activity(
    user_id: int,
    action: str,
    resource_type: str,
    resource_id: Optional[int] = None,
    details: Optional[str] = None,
):
    """Log user activity to the database."""

    try:
        query = """
            INSERT INTO activity_logs (user_id, action, resource_type, resource_id, details, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (
            user_id,
            action,
            resource_type,
            resource_id,
            details,
            datetime.now(timezone.utc),
        )
        db.execute_modify(query, params)
    except Exception as e:
        logger.error("Failed to log activity: %s", e)


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
            payload = jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"])

            # Store user info in Flask's g object for use in the view
            g.current_user_id = payload["user_id"]
            g.current_user_email = payload["email"]

        except IndexError:
            return jsonify({"error": "Invalid authorization header format"}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
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
            user = db.execute_one(
                "SELECT is_admin FROM users WHERE id = %s", (g.current_user_id,)
            )

            if not user or not user["is_admin"]:
                return jsonify({"error": "Admin privileges required"}), 403

        except Exception as e:
            logger.error("Admin check error: %s", e)
            return jsonify({"error": "Authorization check failed"}), 500

        return f(*args, **kwargs)

    return decorated_function


def check_file_access(user_id: int, file_id: int) -> bool:
    """Check if user has access to a file (owner or team member)."""

    query = """
        SELECT f.id
        FROM files f
        LEFT JOIN team_members tm ON f.team_id = tm.team_id AND tm.user_id = %s
        WHERE f.id = %s AND (f.owner_id = %s OR tm.user_id IS NOT NULL)
    """

    result = db.execute_one(query, (user_id, file_id, user_id))
    return result is not None


def format_error_response(
    message: str, status_code: int = 400
) -> tuple[Dict[str, str], int]:
    """Format error response consistently."""
    return {"error": message}, status_code


def format_success_response(
    data: Any = None, message: Optional[str] = None, status_code: int = 200
) -> tuple[Dict[str, Any], int]:
    """Format success response consistently."""
    response = {}
    if data is not None:
        if isinstance(data, dict):
            response.update(data)
        else:
            response["data"] = data
    if message:
        response["message"] = message

    return response, status_code
