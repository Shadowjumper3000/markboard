"""
Team management endpoints - refactored to use services.
"""

import logging
from flask import Blueprint, g, request
from app.api.middleware.auth_decorators import require_auth
from app.api.response_formatter import format_error_response, format_success_response
from app.core.services.team_service import TeamService

logger = logging.getLogger(__name__)

teams_bp = Blueprint("teams", __name__)


@teams_bp.route("/count", methods=["GET"])
@require_auth
def get_team_count():
    """Get the number of teams the authenticated user is a member of."""
    try:
        user_id = g.current_user_id
        count = TeamService.get_user_team_count(user_id)
        return format_success_response({"count": count})
    except Exception as e:
        logger.error("Get team count error: %s", e)
        return format_error_response("Internal server error", 500)


@teams_bp.route("", methods=["GET"])
@require_auth
def list_teams():
    """Get list of teams that the authenticated user is a member of."""
    try:
        user_id = g.current_user_id
        teams = TeamService.get_user_teams(user_id)
        return format_success_response({"teams": teams})
    except Exception as e:
        logger.error("List teams error: %s", e)
        return format_error_response("Internal server error", 500)


@teams_bp.route("/<int:team_id>", methods=["GET"])
@require_auth
def get_team(team_id):
    """Get detailed team information."""
    try:
        user_id = g.current_user_id
        team = TeamService.get_team_details(team_id, user_id)

        if not team:
            return format_error_response("Team not found or access denied", 404)

        return format_success_response(team)
    except Exception as e:
        logger.error("Get team error: %s", e)
        return format_error_response("Internal server error", 500)


@teams_bp.route("", methods=["POST"])
@require_auth
def create_team():
    """Create a new team."""
    try:
        user_id = g.current_user_id
        data = request.get_json()

        if not data:
            return format_error_response("Request body is required", 400)

        name = data.get("name", "").strip()
        description = data.get("description", "").strip()

        if not name:
            return format_error_response("Team name is required", 400)

        if len(name) > 100:
            return format_error_response(
                "Team name must be 100 characters or less", 400
            )

        if len(description) > 500:
            return format_error_response(
                "Description must be 500 characters or less", 400
            )

        success, message, team_id = TeamService.create_team(name, description, user_id)

        if not success:
            return format_error_response(message, 400)

        # Return the created team details
        team = TeamService.get_team_details(team_id, user_id)
        return format_success_response(team, message, 201)

    except Exception as e:
        logger.error("Create team error: %s", e)
        return format_error_response("Internal server error", 500)


@teams_bp.route("/<int:team_id>/join", methods=["POST"])
@require_auth
def join_team(team_id):
    """Join a team by team ID (deprecated - use join by code instead)."""
    try:
        user_id = g.current_user_id
        success, message = TeamService.join_team(team_id, user_id)

        if not success:
            status_code = 404 if "not found" in message.lower() else 400
            return format_error_response(message, status_code)

        return format_success_response({"message": message})
    except Exception as e:
        logger.error("Join team error: %s", e)
        return format_error_response("Internal server error", 500)


@teams_bp.route("/join", methods=["POST"])
@require_auth
def join_team_by_code():
    """Join a team using an invite code."""
    try:
        user_id = g.current_user_id
        data = request.get_json()

        if not data:
            return format_error_response("Request body is required", 400)

        invite_code = data.get("invite_code", "").strip()

        if not invite_code:
            return format_error_response("Invite code is required", 400)

        success, message = TeamService.join_team_by_code(invite_code, user_id)

        if not success:
            return format_error_response(message, 400)

        return format_success_response({"message": message})
    except Exception as e:
        logger.error("Join team by code error: %s", e)
        return format_error_response("Internal server error", 500)


@teams_bp.route("/available", methods=["GET"])
@require_auth
def get_available_teams():
    """Get teams that the user can join."""
    try:
        user_id = g.current_user_id
        teams = TeamService.get_available_teams(user_id)
        return format_success_response({"teams": teams})
    except Exception as e:
        logger.error("Get available teams error: %s", e)
        return format_error_response("Internal server error", 500)


@teams_bp.route("/<int:team_id>/leave", methods=["POST"])
@require_auth
def leave_team(team_id):
    """Leave a team."""
    try:
        user_id = g.current_user_id
        success, message = TeamService.leave_team(team_id, user_id)

        if not success:
            return format_error_response(message, 400)

        return format_success_response({"message": message})
    except Exception as e:
        logger.error("Leave team error: %s", e)
        return format_error_response("Internal server error", 500)


@teams_bp.route("/<int:team_id>", methods=["DELETE"])
@require_auth
def disband_team(team_id):
    """Disband a team (owner only)."""
    try:
        user_id = g.current_user_id
        success, message = TeamService.disband_team(team_id, user_id)

        if not success:
            return format_error_response(
                message, 400 if "not found" not in message.lower() else 404
            )

        return format_success_response({"message": message})
    except Exception as e:
        logger.error("Disband team error: %s", e)
        return format_error_response("Internal server error", 500)


@teams_bp.route("/<int:team_id>/users", methods=["GET"])
@require_auth
def list_team_users(team_id):
    """Get list of team members."""
    try:
        user_id = g.current_user_id
        success, message, users = TeamService.get_team_users(team_id, user_id)

        if not success:
            return format_error_response(message, 403)

        return format_success_response({"users": users})
    except Exception as e:
        logger.error("List team users error: %s", e)
        return format_error_response("Internal server error", 500)


@teams_bp.route("/<int:team_id>/kick", methods=["POST"])
@require_auth
def kick_user_from_team(team_id):
    """Remove a user from team (admin/owner only)."""
    try:
        user_id = g.current_user_id
        data = request.get_json()

        if not data or "user_id" not in data:
            return format_error_response("user_id is required", 400)

        target_user_id = data["user_id"]

        if not isinstance(target_user_id, int):
            return format_error_response("user_id must be an integer", 400)

        success, message = TeamService.kick_user_from_team(
            team_id, target_user_id, user_id
        )

        if not success:
            return format_error_response(
                message, 403 if "permission" in message.lower() else 400
            )

        return format_success_response({"message": message})
    except Exception as e:
        logger.error("Kick user error: %s", e)
        return format_error_response("Internal server error", 500)
