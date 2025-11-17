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
        """Get list of all users with file counts and team info (admin only)."""
        query = """
            SELECT u.id, u.email, u.is_admin, u.created_at, u.last_login,
                   COUNT(DISTINCT f.id) as file_count,
                   COUNT(DISTINCT tm.team_id) as team_count,
                   CASE
                       WHEN u.last_login IS NULL THEN 'inactive'
                       WHEN u.last_login >= DATE_SUB(NOW(), INTERVAL 7 DAY) THEN 'active'
                       WHEN u.last_login >= DATE_SUB(NOW(), INTERVAL 30 DAY) THEN 'recent'
                       ELSE 'inactive'
                   END as status,
                   CASE
                       WHEN u.last_login IS NULL THEN 'Never'
                       ELSE DATE_FORMAT(u.last_login, '%Y-%m-%d %H:%i')
                   END as last_active
            FROM users u
            LEFT JOIN files f ON u.id = f.owner_id AND f.deleted_at IS NULL
            LEFT JOIN team_members tm ON u.id = tm.user_id
            GROUP BY u.id, u.email, u.is_admin, u.created_at, u.last_login
            ORDER BY u.created_at DESC
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
        total_files_result = get_db().execute_one(
            "SELECT COUNT(*) as count FROM files WHERE deleted_at IS NULL"
        )
        total_files = total_files_result["count"]

        # Get total teams
        total_teams_result = get_db().execute_one("SELECT COUNT(*) as count FROM teams")
        total_teams = total_teams_result["count"]

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
            "totalTeams": total_teams,
            "recentActivity": recent_activity,
        }

    @staticmethod
    def get_activity_logs(limit: int = 50) -> List[Dict]:
        """Get recent activity logs filtered for user and team creations."""
        query = """
            SELECT al.id, al.user_id, al.action, al.resource_type,
                   al.resource_id, al.details, al.created_at, u.email as user_email
            FROM activity_logs al
            LEFT JOIN users u ON al.user_id = u.id
            WHERE al.action IN ('user_created', 'team_created', 'team_joined')
            ORDER BY al.created_at DESC
            LIMIT %s
        """
        return get_db().execute_query(query, (limit,))

    @staticmethod
    def get_all_teams() -> List[Dict]:
        """Get list of all teams with statistics."""
        query = """
            SELECT t.id, t.name, t.description, t.owner_id, t.created_at,
                   u.email as owner_email,
                   COUNT(DISTINCT f.id) as file_count,
                   COUNT(DISTINCT tm.user_id) as member_count
            FROM teams t
            LEFT JOIN users u ON t.owner_id = u.id
            LEFT JOIN files f ON t.id = f.team_id AND f.deleted_at IS NULL
            LEFT JOIN team_members tm ON t.id = tm.team_id
            GROUP BY t.id, t.name, t.description, t.owner_id, t.created_at, u.email
            ORDER BY t.created_at DESC
        """
        return get_db().execute_query(query)
