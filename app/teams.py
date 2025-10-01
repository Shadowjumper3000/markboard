"""
Team management endpoints.
"""

from datetime import datetime, timezone
import logging
from flask import Blueprint, g, request
from app.db import db
from app.utils import (
    require_auth,
    format_error_response,
    format_success_response,
    log_activity,
)

logger = logging.getLogger(__name__)

teams_bp = Blueprint("teams", __name__, url_prefix="/teams")


# Endpoint to get the total count of teams
@teams_bp.route("/count", methods=["GET"])
@require_auth
def get_team_count():
    """Get the number of teams the authenticated user is a member of."""
    try:
        user_id = g.current_user_id
        result = db.execute_one(
            """
            SELECT COUNT(DISTINCT t.id) as count
            FROM teams t
            INNER JOIN team_members tm ON t.id = tm.team_id
            WHERE tm.user_id = %s
            """,
            (user_id,),
        )
        return format_success_response({"count": result["count"]})
    except Exception as e:
        logger.error("Get team count error: %s", e)
        return format_error_response("Internal server error", 500)


@teams_bp.route("", methods=["GET"])
@require_auth
def list_teams():
    """Get list of teams that the authenticated user is a member of."""
    try:
        user_id = g.current_user_id

        # Get teams where user is a member
        query = """
            SELECT DISTINCT t.id, t.name, t.description, t.owner_id,
                   t.created_at, COUNT(DISTINCT f.id) as file_count,
                   COUNT(DISTINCT tm2.id) as member_count, tm.role
            FROM teams t
            INNER JOIN team_members tm ON t.id = tm.team_id
            LEFT JOIN files f ON t.id = f.team_id AND f.deleted_at IS NULL
            LEFT JOIN team_members tm2 ON t.id = tm2.team_id
            WHERE tm.user_id = %s
            GROUP BY t.id, t.name, t.description, t.owner_id, t.created_at, tm.role
            ORDER BY t.name
        """

        teams = db.execute_query(query, (user_id,))

        # Convert datetime objects to ISO format
        for team in teams:
            team["created_at"] = team["created_at"].isoformat()

        return format_success_response({"teams": teams})

    except Exception as e:
        logger.error("List teams error: %s", e)
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
            return format_error_response("Request body required", 400)

        name = data.get("name", "").strip()
        description = data.get("description", "").strip()

        if not name:
            return format_error_response("Team name required", 400)

        if len(name) > 100:
            return format_error_response("Team name too long", 400)

        if len(description) > 500:
            return format_error_response("Team description too long", 400)

        # Create the team
        now = datetime.now(timezone.utc)
        team_id = db.execute_modify(
            """
            INSERT INTO teams (name, description, owner_id, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (name, description, user_id, now, now),
        )

        # Add creator as admin member
        db.execute_modify(
            """
            INSERT INTO team_members (team_id, user_id, role, joined_at)
            VALUES (%s, %s, %s, %s)
            """,
            (team_id, user_id, "admin", now),
        )

        # Log activity
        log_activity(user_id, "create", "team", team_id, f"Created team: {name}")

        # Return created team data
        team_data = {
            "id": team_id,
            "name": name,
            "description": description,
            "owner_id": user_id,
            "created_at": now.isoformat(),
        }

        logger.info("Team created: %s (ID: %d) by user %d", name, team_id, user_id)

        return format_success_response(team_data, "Team created successfully", 201)

    except Exception as e:
        logger.error("Create team error: %s", e)
        return format_error_response("Internal server error", 500)


@teams_bp.route("/<int:team_id>/join", methods=["POST"])
@require_auth
def join_team(team_id):
    """Join an existing team."""
    try:
        user_id = g.current_user_id

        # Check if team exists
        team = db.execute_one("SELECT id, name FROM teams WHERE id = %s", (team_id,))

        if not team:
            return format_error_response("Team not found", 404)

        # Check if user is already a member
        existing_member = db.execute_one(
            "SELECT id FROM team_members WHERE team_id = %s AND user_id = %s",
            (team_id, user_id),
        )

        if existing_member:
            return format_error_response("Already a member of this team", 400)

        # Add user as member
        now = datetime.now(timezone.utc)
        db.execute_modify(
            """
            INSERT INTO team_members (team_id, user_id, role, joined_at)
            VALUES (%s, %s, %s, %s)
            """,
            (team_id, user_id, "member", now),
        )

        # Log activity
        log_activity(user_id, "join", "team", team_id, f"Joined team: {team['name']}")

        logger.info("User %d joined team %s (ID: %d)", user_id, team["name"], team_id)

        return format_success_response(
            {"message": f"Successfully joined {team['name']}"}
        )

    except Exception as e:
        logger.error("Join team error: %s", e)
        return format_error_response("Internal server error", 500)


@teams_bp.route("/available", methods=["GET"])
@require_auth
def get_available_teams():
    """Get list of teams that the user can join (not already a member of)."""
    try:
        user_id = g.current_user_id

        # Get teams where user is NOT a member
        query = """
            SELECT t.id, t.name, t.description, t.owner_id, t.created_at,
                   COUNT(DISTINCT f.id) as file_count,
                   COUNT(DISTINCT tm.id) as member_count
            FROM teams t
            LEFT JOIN files f ON t.id = f.team_id AND f.deleted_at IS NULL
            LEFT JOIN team_members tm ON t.id = tm.team_id
            WHERE t.id NOT IN (
                SELECT team_id FROM team_members WHERE user_id = %s
            )
            GROUP BY t.id, t.name, t.description, t.owner_id, t.created_at
            ORDER BY t.name
        """

        teams = db.execute_query(query, (user_id,))

        # Convert datetime objects to ISO format
        for team in teams:
            team["created_at"] = team["created_at"].isoformat()

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

        # Check if user is a member of the team
        team_member = db.execute_one(
            "SELECT id FROM team_members WHERE team_id = %s AND user_id = %s",
            (team_id, user_id),
        )

        if not team_member:
            return format_error_response("Not a member of this team", 400)

        # Get team info for logging
        team = db.execute_one(
            "SELECT name, owner_id FROM teams WHERE id = %s", (team_id,)
        )

        if not team:
            return format_error_response("Team not found", 404)

        # Check if user is the owner
        if team["owner_id"] == user_id:
            return format_error_response(
                "Team owners cannot leave. Transfer ownership or disband team.", 400
            )

        # Remove user from team
        db.execute_modify(
            "DELETE FROM team_members WHERE team_id = %s AND user_id = %s",
            (team_id, user_id),
        )

        # Log activity
        log_activity(user_id, "leave", "team", team_id, f"Left team: {team['name']}")

        logger.info("User %d left team %s (ID: %d)", user_id, team["name"], team_id)

        return format_success_response({"message": f"Successfully left {team['name']}"})

    except Exception as e:
        logger.error("Leave team error: %s", e)
        return format_error_response("Internal server error", 500)


@teams_bp.route("/<int:team_id>", methods=["DELETE"])
@require_auth
def disband_team(team_id):
    """Disband a team (only owner can do this)."""
    try:
        user_id = g.current_user_id

        # Get team info and check ownership
        team = db.execute_one(
            "SELECT name, owner_id FROM teams WHERE id = %s", (team_id,)
        )

        if not team:
            return format_error_response("Team not found", 404)

        if team["owner_id"] != user_id:
            return format_error_response("Only team owners can disband teams", 403)

        # Check if team has files
        file_count = db.execute_one(
            "SELECT COUNT(*) as count FROM files WHERE team_id = %s AND deleted_at IS NULL",
            (team_id,),
        )

        if file_count and file_count["count"] > 0:
            return format_error_response(
                "Cannot disband team with files. Move or delete files first.", 400
            )

        # Remove all team members first
        db.execute_modify("DELETE FROM team_members WHERE team_id = %s", (team_id,))

        # Delete the team
        db.execute_modify("DELETE FROM teams WHERE id = %s", (team_id,))

        # Log activity
        log_activity(
            user_id, "disband", "team", team_id, f"Disbanded team: {team['name']}"
        )

        logger.info(
            "Team disbanded: %s (ID: %d) by user %d", team["name"], team_id, user_id
        )

        return format_success_response(
            {"message": f"Successfully disbanded {team['name']}"}
        )

    except Exception as e:
        logger.error("Disband team error: %s", e)
        return format_error_response("Internal server error", 500)


# List users in a team
@teams_bp.route("/<int:team_id>/users", methods=["GET"])
@require_auth
def list_team_users(team_id):
    """Get list of users in a team."""
    try:
        user_id = g.current_user_id

        # Check if requesting user is a member of the team
        team_member = db.execute_one(
            "SELECT id FROM team_members WHERE team_id = %s AND user_id = %s",
            (team_id, user_id),
        )
        if not team_member:
            return format_error_response("Team not found or access denied", 404)

        # Get all users in the team
        query = """
            SELECT u.id, u.email, u.is_admin, u.created_at, tm.role
            FROM users u
            INNER JOIN team_members tm ON u.id = tm.user_id
            WHERE tm.team_id = %s
            ORDER BY u.email
        """
        users = db.execute_query(query, (team_id,))

        # Convert datetimes to isoformat
        for user in users:
            if user.get("created_at"):
                user["created_at"] = user["created_at"].isoformat()

        return format_success_response({"users": users})
    except Exception as e:
        logger.error("List team users error: %s", e)
        return format_error_response("Internal server error", 500)


# Kick a user from a team
@teams_bp.route("/<int:team_id>/kick", methods=["POST"])
@require_auth
def kick_user_from_team(team_id):
    """Kick a user from a team (admin/owner only)."""
    try:
        user_id = g.current_user_id
        data = request.get_json()
        target_user_id = data.get("user_id")
        if not target_user_id:
            return format_error_response("user_id is required", 400)

        # Check if the requester is an admin or owner in the team
        member = db.execute_one(
            "SELECT role FROM team_members WHERE team_id = %s AND user_id = %s",
            (team_id, user_id),
        )
        if not member or member["role"] not in ("admin", "owner"):
            return format_error_response(
                "Only team admins or owners can kick members", 403
            )

        # Prevent kicking the owner
        team = db.execute_one("SELECT owner_id FROM teams WHERE id = %s", (team_id,))
        if team and target_user_id == team["owner_id"]:
            return format_error_response("Cannot kick the team owner", 400)

        # Check if target user is a member
        target_member = db.execute_one(
            "SELECT id FROM team_members WHERE team_id = %s AND user_id = %s",
            (team_id, target_user_id),
        )
        if not target_member:
            return format_error_response("User is not a member of this team", 404)

        # Remove the user from the team
        db.execute_modify(
            "DELETE FROM team_members WHERE team_id = %s AND user_id = %s",
            (team_id, target_user_id),
        )

        # Log activity
        log_activity(
            user_id,
            "kick",
            "team",
            team_id,
            f"Kicked user {target_user_id} from team {team_id}",
        )

        return format_success_response({"message": "User kicked from team"})
    except Exception as e:
        logger.error("Kick user from team error: %s", e)
        return format_error_response("Internal server error", 500)
