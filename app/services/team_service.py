"""
Team service - handles all team-related business logic.
Follows Single Responsibility Principle.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
import logging
from app.db import get_db
from app.activity import log_activity

logger = logging.getLogger(__name__)


class TeamService:
    """Service class for team operations."""

    @staticmethod
    def get_user_team_count(user_id: int) -> int:
        """Get the number of teams the user is a member of."""
        result = get_db().execute_one(
            """
            SELECT COUNT(DISTINCT t.id) as count
            FROM teams t
            INNER JOIN team_members tm ON t.id = tm.team_id
            WHERE tm.user_id = %s
            """,
            (user_id,),
        )
        return result["count"]

    @staticmethod
    def get_user_teams(user_id: int) -> List[Dict]:
        """Get list of teams that the user is a member of."""
        query = """
            SELECT DISTINCT t.id, t.name, t.description, t.owner_id,
                   t.created_at, COUNT(DISTINCT f.id) as file_count,
                   COUNT(DISTINCT tm2.id) as member_count, tm.role
            FROM teams t
            LEFT JOIN files f ON t.id = f.team_id
            LEFT JOIN team_members tm2 ON t.id = tm2.team_id
            INNER JOIN team_members tm ON t.id = tm.team_id
            WHERE tm.user_id = %s
            GROUP BY t.id, t.name, t.description, t.owner_id, t.created_at, tm.role
            ORDER BY t.created_at DESC
        """
        return get_db().execute_query(query, (user_id,))

    @staticmethod
    def get_team_details(team_id: int, user_id: int) -> Optional[Dict]:
        """Get detailed team information if user has access."""
        # Check if user is a member of the team
        member_check = get_db().execute_one(
            "SELECT role FROM team_members WHERE team_id = %s AND user_id = %s",
            (team_id, user_id),
        )

        if not member_check:
            return None

        # Get team details with stats
        team_query = """
            SELECT t.id, t.name, t.description, t.owner_id, t.created_at,
                   COUNT(DISTINCT f.id) as file_count,
                   COUNT(DISTINCT tm.id) as member_count
            FROM teams t
            LEFT JOIN files f ON t.id = f.team_id
            LEFT JOIN team_members tm ON t.id = tm.team_id
            WHERE t.id = %s
            GROUP BY t.id, t.name, t.description, t.owner_id, t.created_at
        """

        team = get_db().execute_one(team_query, (team_id,))
        if team:
            team["role"] = member_check["role"]

        return team

    @staticmethod
    def create_team(
        name: str, description: str, owner_id: int
    ) -> Tuple[bool, str, Optional[int]]:
        """Create a new team and add the owner as a member."""
        # Check if team name already exists
        existing = get_db().execute_one("SELECT id FROM teams WHERE name = %s", (name,))
        if existing:
            return False, "Team name already exists", None

        try:
            # Insert team (MySQL: no RETURNING id)
            cursor = get_db().execute_modify(
                """
                INSERT INTO teams (name, description, owner_id, created_at)
                VALUES (%s, %s, %s, %s)
                """,
                (name, description, owner_id, datetime.now(timezone.utc)),
            )
            team_id = cursor.lastrowid

            # Add owner as admin member
            get_db().execute_modify(
                """
                INSERT INTO team_members (team_id, user_id, role, joined_at)
                VALUES (%s, %s, %s, %s)
                """,
                (team_id, owner_id, "admin", datetime.now(timezone.utc)),
            )

            # Log activity
            log_activity(
                owner_id, "team_created", "team", team_id, f"Created team: {name}"
            )

            return True, "Team created successfully", team_id

        except Exception as e:
            logger.error("Error creating team: %s", e)
            return False, "Failed to create team", None

    @staticmethod
    def join_team(team_id: int, user_id: int) -> Tuple[bool, str]:
        """Add user to a team."""
        # Check if team exists
        team = get_db().execute_one("SELECT name FROM teams WHERE id = %s", (team_id,))
        if not team:
            return False, "Team not found"

        # Check if user is already a member
        existing_member = get_db().execute_one(
            "SELECT id FROM team_members WHERE team_id = %s AND user_id = %s",
            (team_id, user_id),
        )
        if existing_member:
            return False, "Already a member of this team"

        try:
            # Add user as member
            get_db().execute_modify(
                """
                INSERT INTO team_members (team_id, user_id, role, joined_at)
                VALUES (%s, %s, %s, %s)
                """,
                (team_id, user_id, "member", datetime.now(timezone.utc)),
            )

            # Log activity
            log_activity(
                user_id, "team_joined", "team", team_id, f"Joined team: {team['name']}"
            )

            return True, "Successfully joined team"

        except Exception as e:
            logger.error("Error joining team: %s", e)
            return False, "Failed to join team"

    @staticmethod
    def get_available_teams(user_id: int) -> List[Dict]:
        """Get teams that user can join (not already a member of)."""
        query = """
            SELECT t.id, t.name, t.description, t.owner_id, t.created_at,
                   COUNT(DISTINCT f.id) as file_count,
                   COUNT(DISTINCT tm.id) as member_count
            FROM teams t
            LEFT JOIN files f ON t.id = f.team_id
            LEFT JOIN team_members tm ON t.id = tm.team_id
            WHERE t.id NOT IN (
                SELECT team_id FROM team_members WHERE user_id = %s
            )
            GROUP BY t.id, t.name, t.description, t.owner_id, t.created_at
            ORDER BY t.created_at DESC
        """
        return get_db().execute_query(query, (user_id,))

    @staticmethod
    def leave_team(team_id: int, user_id: int) -> Tuple[bool, str]:
        """Remove user from team."""
        # Check if user is a member
        member = get_db().execute_one(
            "SELECT role FROM team_members WHERE team_id = %s AND user_id = %s",
            (team_id, user_id),
        )
        if not member:
            return False, "Not a member of this team"

        # Check if user is the owner
        team = get_db().execute_one(
            "SELECT name, owner_id FROM teams WHERE id = %s", (team_id,)
        )
        if not team:
            return False, "Team not found"

        if team["owner_id"] == user_id:
            return (
                False,
                "Team owner cannot leave the team. Transfer ownership or disband the team instead.",
            )

        try:
            # Remove user from team
            get_db().execute_modify(
                "DELETE FROM team_members WHERE team_id = %s AND user_id = %s",
                (team_id, user_id),
            )

            # Log activity
            log_activity(
                user_id, "team_left", "team", team_id, f"Left team: {team['name']}"
            )

            return True, "Successfully left team"

        except Exception as e:
            logger.error("Error leaving team: %s", e)
            return False, "Failed to leave team"

    @staticmethod
    def disband_team(team_id: int, user_id: int) -> Tuple[bool, str]:
        """Disband a team (owner only)."""
        # Check if team exists and user is owner
        team = get_db().execute_one(
            "SELECT name, owner_id FROM teams WHERE id = %s", (team_id,)
        )
        if not team:
            return False, "Team not found"

        if team["owner_id"] != user_id:
            return False, "Only team owner can disband the team"

        try:
            # Check if team has files
            file_count = get_db().execute_one(
                "SELECT COUNT(*) as count FROM files WHERE team_id = %s", (team_id,)
            )

            if file_count["count"] > 0:
                # Transfer files to personal ownership before disbanding
                get_db().execute_modify(
                    "UPDATE files SET team_id = NULL WHERE team_id = %s",
                    (team_id,),
                )

            # Delete team members first (foreign key constraint)
            get_db().execute_modify(
                "DELETE FROM team_members WHERE team_id = %s", (team_id,)
            )

            # Delete team
            get_db().execute_modify("DELETE FROM teams WHERE id = %s", (team_id,))

            # Log activity
            log_activity(
                user_id,
                "team_deleted",
                "team",
                team_id,
                f"Disbanded team: {team['name']}",
            )

            return (
                True,
                "Team disbanded successfully. All team files have been transferred to your personal ownership.",
            )
        except Exception as e:
            logger.error("Error disbanding team: %s", e)
        return False, "Failed to disband team"

    @staticmethod
    def get_team_users(
        team_id: int, requesting_user_id: int
    ) -> Tuple[bool, str, List[Dict]]:
        """Get list of team members."""
        # Check if requesting user is a member of the team
        member_check = get_db().execute_one(
            "SELECT role FROM team_members WHERE team_id = %s AND user_id = %s",
            (team_id, requesting_user_id),
        )

        if not member_check:
            return False, "Access denied", []

        # Get team members
        query = """
            SELECT u.id, u.email, tm.role, tm.joined_at
            FROM users u
            INNER JOIN team_members tm ON u.id = tm.user_id
            WHERE tm.team_id = %s
            ORDER BY tm.joined_at ASC
        """

        users = get_db().execute_query(query, (team_id,))
        return True, "Success", users

    @staticmethod
    def kick_user_from_team(
        team_id: int, target_user_id: int, kicking_user_id: int
    ) -> Tuple[bool, str]:
        """Remove a user from team (admin/owner only)."""
        # Check if kicking user is admin or owner
        kicker_member = get_db().execute_one(
            "SELECT role FROM team_members WHERE team_id = %s AND user_id = %s",
            (team_id, kicking_user_id),
        )

        if not kicker_member or kicker_member["role"] not in ["admin", "owner"]:
            return False, "Insufficient permissions"

        # Check if target user is a member
        target_member = get_db().execute_one(
            "SELECT role FROM team_members WHERE team_id = %s AND user_id = %s",
            (team_id, target_user_id),
        )

        if not target_member:
            return False, "User is not a member of this team"

        # Get team info for logging
        team = get_db().execute_one(
            "SELECT name, owner_id FROM teams WHERE id = %s", (team_id,)
        )

        if not team:
            return False, "Team not found"

        # Prevent kicking the team owner
        if team["owner_id"] == target_user_id:
            return False, "Cannot kick the team owner"

        try:
            # Remove user from team
            get_db().execute_modify(
                "DELETE FROM team_members WHERE team_id = %s AND user_id = %s",
                (team_id, target_user_id),
            )

            # Get target user email for logging
            target_user = get_db().execute_one(
                "SELECT email FROM users WHERE id = %s", (target_user_id,)
            )

            # Log activity
            log_activity(
                kicking_user_id,
                "team_member_kicked",
                "team",
                team_id,
                f"Kicked {target_user['email']} from team: {team['name']}",
            )

            return True, "User successfully removed from team"

        except Exception as e:
            logger.error("Error kicking user from team: %s", e)
            return False, "Failed to remove user from team"
