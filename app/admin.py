"""
Admin endpoints for system management.
"""

import logging
from datetime import datetime, timezone, timedelta
from flask import Blueprint, request
from app.db import db
from app.utils import (
    require_auth,
    require_admin,
    format_error_response,
    format_success_response,
)

logger = logging.getLogger(__name__)

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/users", methods=["GET"])
@require_auth
@require_admin
def list_users():
    """Get list of all users (admin only)."""
    try:
        query = """
            SELECT
                u.id,
                u.email,
                u.is_admin,
                u.created_at,
                COUNT(f.id) as file_count,
                MAX(al.created_at) as last_active
            FROM users u
            LEFT JOIN files f ON u.id = f.owner_id AND f.deleted_at IS NULL
            LEFT JOIN activity_logs al ON u.id = al.user_id
            GROUP BY u.id, u.email, u.is_admin, u.created_at
            ORDER BY u.created_at DESC
        """

        users = db.execute_query(query)

        # Format the response
        formatted_users = []
        for user in users:
            # Calculate last active status
            last_active = "Never"
            if user["last_active"]:
                now = datetime.now(timezone.utc)
                if user["last_active"].tzinfo is None:
                    last_active_dt = user["last_active"].replace(tzinfo=timezone.utc)
                else:
                    last_active_dt = user["last_active"]

                diff = now - last_active_dt
                if diff.days == 0:
                    if diff.seconds < 3600:
                        last_active = f"{diff.seconds // 60} minutes ago"
                    else:
                        last_active = f"{diff.seconds // 3600} hours ago"
                elif diff.days == 1:
                    last_active = "1 day ago"
                else:
                    last_active = f"{diff.days} days ago"

            # Determine status
            status = "active"
            if user["last_active"]:
                if user["last_active"].tzinfo is None:
                    last_active_dt = user["last_active"].replace(tzinfo=timezone.utc)
                else:
                    last_active_dt = user["last_active"]

                if (datetime.now(timezone.utc) - last_active_dt).days > 7:
                    status = "inactive"

            formatted_users.append(
                {
                    "id": str(user["id"]),
                    "email": user["email"],
                    "name": user["email"].split("@")[0].replace(".", " ").title(),
                    "role": "admin" if user["is_admin"] else "user",
                    "createdAt": user["created_at"].strftime("%Y-%m-%d"),
                    "fileCount": user["file_count"] or 0,
                    "lastActive": last_active,
                    "status": status,
                }
            )

        return format_success_response({"users": formatted_users})

    except Exception as e:
        logger.error("List users error: %s", e)
        return format_error_response("Internal server error", 500)


@admin_bp.route("/activity", methods=["GET"])
@require_auth
@require_admin
def get_recent_activity():
    """Get recent system activity (admin only)."""
    try:
        limit = min(int(request.args.get("limit", 50)), 100)

        query = """
            SELECT
                al.id,
                al.action,
                al.resource_type,
                al.resource_id,
                al.details,
                al.created_at,
                u.email,
                COALESCE(f.name, '') as resource_name
            FROM activity_logs al
            JOIN users u ON al.user_id = u.id
            LEFT JOIN files f ON al.resource_type = 'file' AND al.resource_id = f.id
            ORDER BY al.created_at DESC
            LIMIT %s
        """

        activities = db.execute_query(query, (limit,))

        # Format the activities
        formatted_activities = []
        for activity in activities:
            # Calculate time ago
            now = datetime.now(timezone.utc)
            if activity["created_at"].tzinfo is None:
                created_at = activity["created_at"].replace(tzinfo=timezone.utc)
            else:
                created_at = activity["created_at"]

            diff = now - created_at
            if diff.days == 0:
                if diff.seconds < 60:
                    timestamp = "Just now"
                elif diff.seconds < 3600:
                    timestamp = f"{diff.seconds // 60} minutes ago"
                else:
                    timestamp = f"{diff.seconds // 3600} hours ago"
            elif diff.days == 1:
                timestamp = "1 day ago"
            else:
                timestamp = f"{diff.days} days ago"

            # Get user name
            user_name = activity["email"].split("@")[0].replace(".", " ").title()

            # Format action description
            action_desc = (
                activity["details"]
                or f"{activity['action']} {activity['resource_type']}"
            )

            # Determine activity type for icon
            activity_type = "login"
            if activity["action"] in ["create", "update", "delete"]:
                activity_type = f"file_{activity['action']}d"
            elif activity["action"] == "login":
                activity_type = "login"
            elif activity["action"] == "signup":
                activity_type = "login"

            formatted_activities.append(
                {
                    "id": str(activity["id"]),
                    "type": activity_type,
                    "user": user_name,
                    "action": action_desc,
                    "timestamp": timestamp,
                }
            )

        return format_success_response({"activities": formatted_activities})

    except Exception as e:
        logger.error("Get recent activity error: %s", e)
        return format_error_response("Internal server error", 500)


@admin_bp.route("/stats", methods=["GET"])
@require_auth
@require_admin
def get_system_stats():
    """Get system statistics (admin only)."""
    try:
        # Get total users
        total_users = db.execute_one("SELECT COUNT(*) as count FROM users")["count"]

        # Get active users (logged in within last 7 days)
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        active_users = db.execute_one(
            "SELECT COUNT(DISTINCT user_id) as count FROM activity_logs WHERE created_at >= %s",
            (week_ago,),
        )["count"]

        # Get total files
        total_files = db.execute_one(
            "SELECT COUNT(*) as count FROM files WHERE deleted_at IS NULL"
        )["count"]

        # Get recent activity count (last 24 hours)
        day_ago = datetime.now(timezone.utc) - timedelta(days=1)
        recent_activity = db.execute_one(
            "SELECT COUNT(*) as count FROM activity_logs WHERE created_at >= %s",
            (day_ago,),
        )["count"]

        return format_success_response(
            {
                "totalUsers": total_users,
                "activeUsers": active_users,
                "totalFiles": total_files,
                "recentActivity": recent_activity,
            }
        )

    except Exception as e:
        logger.error("Get system stats error: %s", e)
        return format_error_response("Internal server error", 500)


@admin_bp.route("/files", methods=["GET"])
@require_auth
@require_admin
def list_all_files():
    """Get list of all files in the system (admin only)."""
    try:
        query = """
            SELECT
                f.id,
                f.name,
                f.created_at,
                f.updated_at,
                u.email as owner_email,
                t.name as team_name,
                LENGTH(f.content) as size_bytes
            FROM files f
            JOIN users u ON f.owner_id = u.id
            LEFT JOIN teams t ON f.team_id = t.id
            WHERE f.deleted_at IS NULL
            ORDER BY f.updated_at DESC
        """

        files = db.execute_query(query)

        # Format the files
        formatted_files = []
        for file in files:
            # Format size
            size_bytes = file["size_bytes"] or 0
            if size_bytes < 1024:
                size = f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                size = f"{size_bytes / 1024:.1f} KB"
            else:
                size = f"{size_bytes / (1024 * 1024):.1f} MB"

            formatted_files.append(
                {
                    "id": str(file["id"]),
                    "name": file["name"],
                    "owner": file["owner_email"]
                    .split("@")[0]
                    .replace(".", " ")
                    .title(),
                    "team": file["team_name"] or "Personal",
                    "size": size,
                    "createdAt": file["created_at"].isoformat(),
                    "updatedAt": file["updated_at"].isoformat(),
                }
            )

        return format_success_response({"files": formatted_files})

    except Exception as e:
        logger.error("List all files error: %s", e)
        return format_error_response("Internal server error", 500)
