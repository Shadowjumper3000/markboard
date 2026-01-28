"""
JWT token management service.
Follows Single Responsibility Principle - only handles JWT operations.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Dict

import jwt

from config import Config

logger = logging.getLogger(__name__)


class JwtService:
    """Service for JWT token generation and verification."""

    @staticmethod
    def generate_token(user_id: int, email: str, is_admin: bool = False) -> str:
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
    def verify_token(token: str) -> Dict:
        """Verify and decode JWT token."""
        try:
            payload = jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError as exc:
            raise ValueError("Token has expired") from exc
        except jwt.InvalidTokenError as exc:
            raise ValueError("Invalid token") from exc
