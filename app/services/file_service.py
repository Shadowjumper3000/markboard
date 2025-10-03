"""
File service - handles all file-related business logic.
Follows Single Responsibility Principle.
"""

import mimetypes
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
import logging
from app.db import get_db
from app.file_storage import file_storage
from app.permissions import check_file_access
from app.security import sanitize_filename
from app.activity import log_activity

logger = logging.getLogger(__name__)


class FileService:
    """Service class for file operations."""

    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Format file size in human readable format."""
        if size_bytes == 0:
            return "0 B"

        size_names = ["B", "KB", "MB", "GB", "TB"]
        size_bytes = float(size_bytes)
        i = 0

        while size_bytes >= 1024.0 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1

        return f"{size_bytes:.1f} {size_names[i]}"

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

        files = get_db().execute_query(query, (user_id, user_id))

        # Format file sizes
        for file in files:
            file["size_formatted"] = FileService.format_file_size(file["file_size"])

        return files

    @staticmethod
    def create_file(
        name: str, content: str, owner_id: int, team_id: Optional[int] = None
    ) -> Tuple[bool, str, Optional[Dict]]:
        """Create a new file."""
        # Validate file name
        if not name or not name.strip():
            return False, "File name is required", None

        clean_name = sanitize_filename(name.strip())
        if not clean_name:
            return False, "Invalid file name", None

        # Check team access if team_id provided
        if team_id:
            team_member = get_db().execute_one(
                "SELECT id FROM team_members WHERE team_id = %s AND user_id = %s",
                (team_id, owner_id),
            )
            if not team_member:
                return False, "Access denied to team", None

        # Check for duplicate file names in the same context
        if team_id:
            existing = get_db().execute_one(
                "SELECT id FROM files WHERE name = %s AND team_id = %s",
                (clean_name, team_id),
            )
        else:
            existing = get_db().execute_one(
                "SELECT id FROM files WHERE name = %s AND owner_id = %s AND team_id IS NULL",
                (clean_name, owner_id),
            )

        if existing:
            return False, "File with this name already exists", None

        try:
            # Insert file record
            file_result = get_db().execute_one(
                """
                INSERT INTO files (name, owner_id, team_id, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    clean_name,
                    owner_id,
                    team_id,
                    datetime.now(timezone.utc),
                    datetime.now(timezone.utc),
                ),
            )

            file_id = file_result["id"]

            # Generate file path and save content
            file_path = file_storage.generate_file_path(file_id, clean_name)
            file_size, checksum = file_storage.save_file(file_path, content)

            # Determine MIME type
            mime_type, _ = mimetypes.guess_type(clean_name)
            if not mime_type:
                mime_type = "text/plain"

            # Update file record with storage info
            get_db().execute_modify(
                """
                UPDATE files
                SET file_path = %s, file_size = %s, checksum = %s, mime_type = %s
                WHERE id = %s
                """,
                (file_path, file_size, checksum, mime_type, file_id),
            )

            # Get the complete file record
            file_record = get_db().execute_one(
                """
                SELECT id, name, file_size, mime_type, owner_id, team_id,
                       created_at, updated_at
                FROM files WHERE id = %s
                """,
                (file_id,),
            )

            file_record["size_formatted"] = FileService.format_file_size(file_size)

            # Log activity
            activity_details = f"Created file: {clean_name}"
            if team_id:
                activity_details += " (Team file)"

            log_activity(owner_id, "file_created", "file", file_id, activity_details)

            return True, "File created successfully", file_record

        except Exception as e:
            logger.error("Error creating file: %s", e)
            return False, "Failed to create file", None

    @staticmethod
    def get_file_details(
        file_id: int, user_id: int
    ) -> Tuple[bool, str, Optional[Dict]]:
        """Get file details if user has access."""
        if not check_file_access(user_id, file_id):
            return False, "Access denied", None

        file_record = get_db().execute_one(
            """
            SELECT id, name, file_path, file_size, mime_type, owner_id,
                   team_id, created_at, updated_at
            FROM files WHERE id = %s
            """,
            (file_id,),
        )

        if not file_record:
            return False, "File not found", None

        try:
            # Read file content
            content = file_storage.read_file(file_record["file_path"])
            file_record["content"] = content
            file_record["size_formatted"] = FileService.format_file_size(
                file_record["file_size"]
            )

            # Log activity
            log_activity(
                user_id,
                "file_viewed",
                "file",
                file_id,
                f"Viewed file: {file_record['name']}",
            )

            return True, "Success", file_record

        except FileNotFoundError:
            logger.error("File content not found: %s", file_record["file_path"])
            return False, "File content not found", None
        except Exception as e:
            logger.error("Error reading file: %s", e)
            return False, "Failed to read file", None

    @staticmethod
    def update_file(
        file_id: int,
        user_id: int,
        name: Optional[str] = None,
        content: Optional[str] = None,
    ) -> Tuple[bool, str, Optional[Dict]]:
        """Update file name and/or content."""
        if not check_file_access(user_id, file_id):
            return False, "Access denied", None

        # Get current file record
        file_record = get_db().execute_one(
            """
            SELECT id, name, file_path, owner_id, team_id
            FROM files WHERE id = %s
            """,
            (file_id,),
        )

        if not file_record:
            return False, "File not found", None

        updates = {}
        update_content = False

        # Handle name update
        if name is not None:
            clean_name = sanitize_filename(name.strip()) if name.strip() else None
            if not clean_name:
                return False, "Invalid file name", None

            # Check for duplicate names
            if file_record["team_id"]:
                existing = get_db().execute_one(
                    "SELECT id FROM files WHERE name = %s AND team_id = %s AND id != %s",
                    (clean_name, file_record["team_id"], file_id),
                )
            else:
                existing = get_db().execute_one(
                    "SELECT id FROM files WHERE name = %s AND owner_id = %s AND team_id IS NULL AND id != %s",
                    (clean_name, file_record["owner_id"], file_id),
                )

            if existing:
                return False, "File with this name already exists", None

            updates["name"] = clean_name

        # Handle content update
        if content is not None:
            update_content = True
            updates["updated_at"] = datetime.now(timezone.utc)

        if not updates and not update_content:
            return False, "No updates provided", None

        try:
            # Update content if provided
            if update_content:
                file_size, checksum = file_storage.save_file(
                    file_record["file_path"], content
                )
                updates["file_size"] = file_size
                updates["checksum"] = checksum

            # Update database record
            if updates:
                set_clause = ", ".join([f"{key} = %s" for key in updates.keys()])
                query = f"UPDATE files SET {set_clause} WHERE id = %s"
                params = list(updates.values()) + [file_id]

                get_db().execute_modify(query, tuple(params))

            # Get updated file record
            updated_file = get_db().execute_one(
                """
                SELECT id, name, file_size, mime_type, owner_id, team_id,
                       created_at, updated_at
                FROM files WHERE id = %s
                """,
                (file_id,),
            )

            updated_file["size_formatted"] = FileService.format_file_size(
                updated_file["file_size"]
            )

            # Log activity
            changes = []
            if name is not None:
                changes.append(f"name to '{updates['name']}'")
            if content is not None:
                changes.append("content")

            activity_details = f"Updated file {file_record['name']}: " + ", ".join(
                changes
            )
            log_activity(user_id, "file_edited", "file", file_id, activity_details)

            return True, "File updated successfully", updated_file

        except Exception as e:
            logger.error("Error updating file: %s", e)
            return False, "Failed to update file", None

    @staticmethod
    def delete_file(file_id: int, user_id: int) -> Tuple[bool, str]:
        """Delete a file."""
        if not check_file_access(user_id, file_id):
            return False, "Access denied"

        # Get file record
        file_record = get_db().execute_one(
            "SELECT name, file_path FROM files WHERE id = %s",
            (file_id,),
        )

        if not file_record:
            return False, "File not found"

        try:
            # Delete from database first
            get_db().execute_modify("DELETE FROM files WHERE id = %s", (file_id,))

            # Delete physical file
            file_storage.delete_file(file_record["file_path"])

            # Log activity
            log_activity(
                user_id,
                "file_deleted",
                "file",
                file_id,
                f"Deleted file: {file_record['name']}",
            )

            return True, "File deleted successfully"

        except Exception as e:
            logger.error("Error deleting file: %s", e)
            return False, "Failed to delete file"

    @staticmethod
    def get_file_content(file_id: int, user_id: int) -> Tuple[bool, str, Optional[str]]:
        """Get file content only (used by download functionality)."""
        if not check_file_access(user_id, file_id):
            return False, "Access denied", None

        file_record = get_db().execute_one(
            "SELECT name, file_path FROM files WHERE id = %s",
            (file_id,),
        )

        if not file_record:
            return False, "File not found", None

        try:
            content = file_storage.read_file(file_record["file_path"])
            return True, "Success", content
        except FileNotFoundError:
            logger.error("File content not found: %s", file_record["file_path"])
            return False, "File content not found", None
        except Exception as e:
            logger.error("Error reading file content: %s", e)
            return False, "Failed to read file content", None

    @staticmethod
    def get_file_name(file_id: int, user_id: int) -> Tuple[bool, str, Optional[str]]:
        """Get file name only (used by download functionality)."""
        if not check_file_access(user_id, file_id):
            return False, "Access denied", None

        file_record = get_db().execute_one(
            "SELECT name FROM files WHERE id = %s",
            (file_id,),
        )

        if not file_record:
            return False, "File not found", None

        return True, "Success", file_record["name"]
