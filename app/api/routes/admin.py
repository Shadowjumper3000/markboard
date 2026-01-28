"""
Admin endpoints - refactored to use services.
"""

import logging
from flask import Blueprint, request
from app.api.middleware.auth_decorators import require_auth, require_admin
from app.api.response_formatter import format_error_response, format_success_response
from app.core.services.admin_service import AdminService

logger = logging.getLogger(__name__)

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/users", methods=["GET"])
@require_auth
@require_admin
def get_users():
    """Get list of all users (admin only)."""
    try:
        users = AdminService.get_all_users()
        return format_success_response({"users": users})
    except Exception as e:
        logger.error("List users error: %s", e)
        return format_error_response("Internal server error", 500)


@admin_bp.route("/stats", methods=["GET"])
@require_auth
@require_admin
def get_stats():
    """Get system statistics (admin only)."""
    try:
        stats = AdminService.get_system_stats()
        return format_success_response(stats)
    except Exception as e:
        logger.error("Get stats error: %s", e)
        return format_error_response("Internal server error", 500)


@admin_bp.route("/activity", methods=["GET"])
@require_auth
@require_admin
def get_activity():
    """Get recent activity logs (admin only)."""
    try:
        # Get limit parameter from query string
        limit = request.args.get("limit", "50")
        try:
            limit = int(limit)
            if limit <= 0 or limit > 1000:
                return format_error_response("Limit must be between 1 and 1000", 400)
        except ValueError:
            return format_error_response("Limit must be a valid integer", 400)

        activities = AdminService.get_activity_logs(limit)
        return format_success_response({"activities": activities})
    except Exception as e:
        logger.error("Get activity error: %s", e)
        return format_error_response("Internal server error", 500)


@admin_bp.route("/teams", methods=["GET"])
@require_auth
@require_admin
def get_teams():
    """Get list of all teams (admin only)."""
    try:
        teams = AdminService.get_all_teams()
        return format_success_response({"teams": teams})
    except Exception as e:
        logger.error("List teams error: %s", e)
        return format_error_response("Internal server error", 500)
