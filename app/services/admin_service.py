"""
Admin service - handles admin-related business logic.
Follows Single Responsibility Principle.
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, List
import logging
from app.db import get_db

logger = logging.getLogger(__name__)


class AdminService:
    """Service class for admin operations."""

    @staticmethod
    def get_all_users() -> List[Dict]:
        """Get list of all users (admin only)."""
        query = """
            SELECT id, email, is_admin, created_at, last_login
            FROM users
            ORDER BY created_at DESC
        """
        return get_db().execute_query(query)

    @staticmethod
    def get_system_stats() -> Dict:
        """Get system statistics."""
        # Get total users
        total_users_result = get_db().execute_one("SELECT COUNT(*) as count FROM users")
        total_users = total_users_result["count"]

        # Get active users (logged in within last 30 days)
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        active_users_result = get_db().execute_one(
            "SELECT COUNT(*) as count FROM users WHERE last_login >= %s",
            (thirty_days_ago,),
        )
        active_users = active_users_result["count"]

        # Get total files
        total_files_result = get_db().execute_one("SELECT COUNT(*) as count FROM files")
        total_files = total_files_result["count"]

        # Get recent activity (last 7 days)
        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
        recent_activity_result = get_db().execute_one(
            "SELECT COUNT(*) as count FROM activity_logs WHERE created_at >= %s",
            (seven_days_ago,),
        )
        recent_activity = recent_activity_result["count"]

        return {
            "totalUsers": total_users,
            "activeUsers": active_users,
            "totalFiles": total_files,
            "recentActivity": recent_activity,
        }

    @staticmethod
    def get_activity_logs(limit: int = 50) -> List[Dict]:
        """Get recent activity logs."""
        query = """
            SELECT al.id, al.user_id, al.action, al.resource_type,
                   al.resource_id, al.details, al.created_at, u.email as user_email
            FROM activity_logs al
            LEFT JOIN users u ON al.user_id = u.id
            ORDER BY al.created_at DESC
            LIMIT %s
        """
        return get_db().execute_query(query, (limit,))
