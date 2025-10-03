"""
File access permission utilities.
"""

from app.db import get_db


def check_file_access(user_id: int, file_id: int) -> bool:
    """Check if user has access to a file (owner or team member)."""

    query = """
        SELECT f.id
        FROM files f
        LEFT JOIN team_members tm ON f.team_id = tm.team_id AND tm.user_id = %s
        WHERE f.id = %s AND (f.owner_id = %s OR tm.user_id IS NOT NULL)
    """

    result = get_db().execute_one(query, (user_id, file_id, user_id))
    return result is not None


__all__ = ["check_file_access"]
