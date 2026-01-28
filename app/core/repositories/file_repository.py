"""
File repository - data access layer for files.
Follows Repository Pattern and separates data access from business logic.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional

from app.infrastructure.database.connection import get_db

logger = logging.getLogger(__name__)


class FileRepository:
    """Repository for file data access operations."""

    @staticmethod
    def get_user_files(user_id: int) -> List[Dict]:
        """Get all files accessible to the user (owned or team files)."""
        query = """
            SELECT f.id, f.name, f.file_size, f.mime_type, f.owner_id,
                   f.team_id, f.created_at, f.updated_at
            FROM files f
            LEFT JOIN team_members tm ON f.team_id = tm.team_id AND tm.user_id = %s
            WHERE f.owner_id = %s OR tm.user_id IS NOT NULL
            ORDER BY f.updated_at DESC
        """
        return get_db().execute_query(query, (user_id, user_id))

    @staticmethod
    def get_file_by_id(file_id: int) -> Optional[Dict]:
        """Get file record by ID."""
        return get_db().execute_one(
            """
            SELECT id, name, file_path, file_size, mime_type, owner_id,
                   team_id, created_at, updated_at
            FROM files WHERE id = %s
            """,
            (file_id,),
        )

    @staticmethod
    def check_duplicate_file(name: str, owner_id: int, team_id: Optional[int]) -> bool:
        """Check if a file with the same name exists in the same context."""
        if team_id:
            existing = get_db().execute_one(
                "SELECT id FROM files WHERE name = %s AND team_id = %s",
                (name, team_id),
            )
        else:
            existing = get_db().execute_one(
                "SELECT id FROM files WHERE name = %s AND owner_id = %s AND team_id IS NULL",
                (name, owner_id),
            )
        return existing is not None

    @staticmethod
    def create_file(
        name: str, owner_id: int, team_id: Optional[int], file_path: str
    ) -> int:
        """Create a new file record and return its ID."""
        return get_db().execute_modify(
            """
            INSERT INTO files (name, owner_id, team_id, file_path, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                name,
                owner_id,
                team_id,
                file_path,
                datetime.now(timezone.utc),
                datetime.now(timezone.utc),
            ),
        )

    @staticmethod
    def update_file_storage_info(
        file_id: int, file_path: str, file_size: int, checksum: str, mime_type: str
    ) -> None:
        """Update file record with storage information."""
        get_db().execute_modify(
            """
            UPDATE files
            SET file_path = %s, file_size = %s, checksum = %s, mime_type = %s
            WHERE id = %s
            """,
            (file_path, file_size, checksum, mime_type, file_id),
        )

    @staticmethod
    def update_file_content(file_id: int, file_size: int, checksum: str) -> None:
        """Update file content metadata."""
        get_db().execute_modify(
            """
            UPDATE files
            SET file_size = %s, checksum = %s, updated_at = %s
            WHERE id = %s
            """,
            (file_size, checksum, datetime.now(timezone.utc), file_id),
        )

    @staticmethod
    def update_file_name(file_id: int, new_name: str, new_path: str) -> None:
        """Update file name and path."""
        get_db().execute_modify(
            """
            UPDATE files
            SET name = %s, file_path = %s, updated_at = %s
            WHERE id = %s
            """,
            (new_name, new_path, datetime.now(timezone.utc), file_id),
        )

    @staticmethod
    def delete_file(file_id: int) -> None:
        """Delete a file record."""
        get_db().execute_modify("DELETE FROM files WHERE id = %s", (file_id,))

    @staticmethod
    def check_team_membership(team_id: int, user_id: int) -> bool:
        """Check if user is a member of the team."""
        result = get_db().execute_one(
            "SELECT id FROM team_members WHERE team_id = %s AND user_id = %s",
            (team_id, user_id),
        )
        return result is not None
