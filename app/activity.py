"""
Activity logging utilities.
"""

import logging
from datetime import datetime, timezone
from typing import Optional
from app.db import get_db

logger = logging.getLogger(__name__)

__all__ = ["log_activity"]


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
        get_db().execute_modify(query, params)
    except Exception as e:
        logger.error("Failed to log activity: %s", e)
