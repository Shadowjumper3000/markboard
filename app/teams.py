"""
Team management endpoints.
"""

from flask import Blueprint, jsonify, g
from app.db import db
from app.utils import require_auth, format_error_response, format_success_response
import logging

logger = logging.getLogger(__name__)

teams_bp = Blueprint("teams", __name__, url_prefix="/teams")


@teams_bp.route("", methods=["GET"])
@require_auth
def list_teams():
    """Get list of teams that the authenticated user is a member of."""
    try:
        user_id = g.current_user_id

        # Get teams where user is a member
        query = """
            SELECT DISTINCT t.id, t.name, t.description, t.owner_id, t.created_at,
                   COUNT(f.id) as file_count
            FROM teams t
            INNER JOIN team_members tm ON t.id = tm.team_id
            LEFT JOIN files f ON t.id = f.team_id AND f.deleted_at IS NULL
            WHERE tm.user_id = %s
            GROUP BY t.id, t.name, t.description, t.owner_id, t.created_at
            ORDER BY t.name
        """

        teams = db.execute_query(query, (user_id,))

        # Convert datetime objects to ISO format
        for team in teams:
            team["created_at"] = team["created_at"].isoformat()

        return format_success_response({"teams": teams})

    except Exception as e:
        logger.error(f"List teams error: {e}")
        return format_error_response("Internal server error", 500)


@teams_bp.route("/<int:team_id>", methods=["GET"])
@require_auth
def get_team(team_id):
    """Get team details."""
    try:
        user_id = g.current_user_id

        # Check if user is a member of the team
        team_member = db.execute_one(
            "SELECT id FROM team_members WHERE team_id = %s AND user_id = %s",
            (team_id, user_id),
        )

        if not team_member:
            return format_error_response("Team not found or access denied", 404)

        # Get team details
        team = db.execute_one(
            """
            SELECT t.id, t.name, t.description, t.owner_id, t.created_at,
                   COUNT(f.id) as file_count
            FROM teams t
            LEFT JOIN files f ON t.id = f.team_id AND f.deleted_at IS NULL
            WHERE t.id = %s
            GROUP BY t.id, t.name, t.description, t.owner_id, t.created_at
            """,
            (team_id,),
        )

        if not team:
            return format_error_response("Team not found", 404)

        # Convert datetime objects to ISO format
        team["created_at"] = team["created_at"].isoformat()

        return format_success_response(team)

    except Exception as e:
        logger.error(f"Get team error: {e}")
        return format_error_response("Internal server error", 500)
