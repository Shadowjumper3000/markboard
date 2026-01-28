"""
Refactored File Service - business logic only.
Uses FileRepository for data access and FileFormatter for formatting.
Follows Single Responsibility Principle and Dependency Inversion.
"""

import logging
import mimetypes
from typing import Dict, List, Optional, Tuple

from app.utils.activity_logger import log_activity
from app.core.repositories.file_repository import FileRepository
from app.infrastructure.storage.file_storage import file_storage
from app.core.permissions import check_file_access
from app.infrastructure.security.sanitizer import sanitize_filename
from app.utils.formatters import FileFormatter

logger = logging.getLogger(__name__)


class FileService:
    """Service class for file business logic operations."""

    @staticmethod
    def get_user_files(user_id: int) -> List[Dict]:
        """Get all files accessible to the user (owned or team files)."""
        files = FileRepository.get_user_files(user_id)

        # Format file sizes
        for file in files:
            file["size_formatted"] = FileFormatter.format_file_size(file["file_size"])

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
        if team_id and not FileRepository.check_team_membership(team_id, owner_id):
            return False, "Access denied to team", None

        # Check for duplicate file names
        if FileRepository.check_duplicate_file(clean_name, owner_id, team_id):
            return False, "File with this name already exists", None

        try:
            # Create file record
            file_id = FileRepository.create_file(clean_name, owner_id, team_id, "")

            # Generate file path and save content
            file_path = file_storage.generate_file_path(file_id, clean_name)
            file_size, checksum = file_storage.save_file(file_path, content)

            # Determine MIME type
            mime_type, _ = mimetypes.guess_type(clean_name)
            if not mime_type:
                mime_type = "text/plain"

            # Update file record with storage info
            FileRepository.update_file_storage_info(
                file_id, file_path, file_size, checksum, mime_type
            )

            # Get the complete file record
            file_record = FileRepository.get_file_by_id(file_id)
            file_record["size_formatted"] = FileFormatter.format_file_size(file_size)

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

        file_record = FileRepository.get_file_by_id(file_id)

        if not file_record:
            return False, "File not found", None

        try:
            # Read file content
            content = file_storage.read_file(file_record["file_path"])
            file_record["content"] = content
            file_record["size_formatted"] = FileFormatter.format_file_size(
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

        file_record = FileRepository.get_file_by_id(file_id)
        if not file_record:
            return False, "File not found", None

        # Check if no updates provided
        if content is None and (name is None or not name.strip()):
            return False, "No updates provided", None

        try:
            # Validate name early if provided
            if name is not None and name.strip():
                clean_name = sanitize_filename(name.strip())
                if not clean_name:
                    return False, "Invalid file name", None

            # Update content if provided
            if content is not None:
                file_size, checksum = file_storage.save_file(
                    file_record["file_path"], content
                )
                FileRepository.update_file_content(file_id, file_size, checksum)

            # Update name if provided
            if name and name.strip():
                clean_name = sanitize_filename(name.strip())
                # Check for duplicate
                if FileRepository.check_duplicate_file(
                    clean_name, file_record["owner_id"], file_record["team_id"]
                ):
                    if clean_name != file_record["name"]:
                        return False, "File with this name already exists", None

                # Generate new path and rename
                new_path = file_storage.generate_file_path(file_id, clean_name)
                if file_storage.move_file(file_record["file_path"], new_path):
                    FileRepository.update_file_name(file_id, clean_name, new_path)

            # Get updated file record
            updated_file = FileRepository.get_file_by_id(file_id)
            updated_file["size_formatted"] = FileFormatter.format_file_size(
                updated_file["file_size"]
            )

            # Log activity
            log_activity(
                user_id,
                "file_updated",
                "file",
                file_id,
                f"Updated file: {updated_file['name']}",
            )

            return True, "File updated successfully", updated_file

        except Exception as e:
            logger.error("Error updating file: %s", e)
            return False, "Failed to update file", None

    @staticmethod
    def delete_file(file_id: int, user_id: int) -> Tuple[bool, str]:
        """Delete a file."""
        if not check_file_access(user_id, file_id):
            return False, "Access denied"

        file_record = FileRepository.get_file_by_id(file_id)
        if not file_record:
            return False, "File not found"

        try:
            # Delete physical file
            file_storage.delete_file(file_record["file_path"])

            # Delete database record
            FileRepository.delete_file(file_id)

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
        """Get file content if user has access."""
        if not check_file_access(user_id, file_id):
            return False, "Access denied", None

        file_record = FileRepository.get_file_by_id(file_id)
        if not file_record:
            return False, "File not found", None

        try:
            content = file_storage.read_file(file_record["file_path"])
            return True, "Success", content
        except FileNotFoundError:
            logger.error("File content not found: %s", file_record["file_path"])
            return False, "File content not found", None
        except Exception as e:
            logger.error("Error reading file: %s", e)
            return False, "Failed to read file", None

    @staticmethod
    def get_file_name(file_id: int, user_id: int) -> Tuple[bool, str, Optional[str]]:
        """Get file name if user has access."""
        if not check_file_access(user_id, file_id):
            return False, "Access denied", None

        file_record = FileRepository.get_file_by_id(file_id)
        if not file_record:
            return False, "File not found", None

        return True, "Success", file_record["name"]
