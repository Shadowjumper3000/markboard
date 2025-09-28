"""
File management endpoints.
"""

from datetime import datetime, timezone
from flask import Blueprint, request, jsonify, g
from app.db import db
from app.file_storage import file_storage
from app.utils import (
    require_auth,
    check_file_access,
    sanitize_filename,
    log_activity,
    format_error_response,
    format_success_response,
)
import logging
import mimetypes

logger = logging.getLogger(__name__)

files_bp = Blueprint("files", __name__, url_prefix="/files")


def _format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    size = float(size_bytes)
    i = 0

    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1

    return f"{size:.1f} {size_names[i]}"


@files_bp.route("", methods=["GET"])
@require_auth
def list_files():
    """Get list of files for authenticated user."""
    try:
        user_id = g.current_user_id

        query = """
            SELECT DISTINCT f.id, f.name, f.file_size, f.mime_type,
                   f.created_at, f.updated_at, f.owner_id, f.team_id
            FROM files f
            LEFT JOIN team_members tm ON f.team_id = tm.team_id 
                     AND tm.user_id = %s
            WHERE (f.owner_id = %s OR tm.user_id IS NOT NULL) 
                  AND f.deleted_at IS NULL
            ORDER BY f.updated_at DESC
        """

        files = db.execute_query(query, (user_id, user_id))

        # Convert datetime objects to ISO format and add file size info
        for file in files:
            file["created_at"] = file["created_at"].isoformat()
            file["updated_at"] = file["updated_at"].isoformat()
            # Convert file size to human readable format
            file["size_formatted"] = _format_file_size(file["file_size"])

        return format_success_response({"files": files})

    except Exception as e:
        logger.error(f"List files error: {e}")
        return format_error_response("Internal server error", 500)


@files_bp.route("", methods=["POST"])
@require_auth
def create_file():
    """Create a new file."""
    try:
        user_id = g.current_user_id
        data = request.get_json()

        if not data:
            return format_error_response("Request body required", 400)

        name = data.get("name", "").strip()
        content = data.get("content", "")
        team_id = data.get("team_id")

        if not name:
            return format_error_response("File name required", 400)

        # Sanitize filename
        name = sanitize_filename(name)

        # Validate team access if team_id provided
        if team_id:
            team_member = db.execute_one(
                "SELECT id FROM team_members WHERE team_id = %s AND user_id = %s",
                (team_id, user_id),
            )
            if not team_member:
                return format_error_response("Access denied to team", 403)

        # Create file record first to get ID
        now = datetime.now(timezone.utc)
        mime_type = mimetypes.guess_type(name)[0] or "text/markdown"

        file_id = db.execute_modify(
            """
            INSERT INTO files (name, file_path, file_size, mime_type, 
                             owner_id, team_id, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (name, "", 0, mime_type, user_id, team_id, now, now),
        )

        # Generate file path and save content to filesystem
        file_path = file_storage.generate_file_path(file_id, name)
        file_size, checksum = file_storage.save_file(file_path, content)

        # Update database with actual file path, size, and checksum
        db.execute_modify(
            """
            UPDATE files SET file_path = %s, file_size = %s, checksum = %s
            WHERE id = %s
            """,
            (file_path, file_size, checksum, file_id),
        )

        # Log activity
        log_activity(user_id, "create", "file", file_id, f"Created file: {name}")

        # Return created file metadata
        file_data = {
            "id": file_id,
            "name": name,
            "file_size": file_size,
            "size_formatted": _format_file_size(file_size),
            "mime_type": mime_type,
            "owner_id": user_id,
            "team_id": team_id,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
        }

        logger.info(
            f"File created: {name} (ID: {file_id}, {file_size} bytes) by user {user_id}"
        )

        return format_success_response(file_data, "File created successfully", 201)

    except Exception as e:
        logger.error(f"Create file error: {e}")
        return format_error_response("Internal server error", 500)


@files_bp.route("/<int:file_id>", methods=["GET"])
@require_auth
def get_file(file_id):
    """Get file by ID with content."""
    try:
        user_id = g.current_user_id

        # Check access
        if not check_file_access(user_id, file_id):
            return format_error_response("File not found or access denied", 404)

        # Get file metadata
        file_data = db.execute_one(
            """
            SELECT id, name, file_path, file_size, mime_type, checksum,
                   owner_id, team_id, created_at, updated_at
            FROM files
            WHERE id = %s AND deleted_at IS NULL
            """,
            (file_id,),
        )

        if not file_data:
            return format_error_response("File not found", 404)

        # Read file content from filesystem
        try:
            content = file_storage.read_file(file_data["file_path"])
        except FileNotFoundError:
            logger.error(
                f"File content missing for ID {file_id}: {file_data['file_path']}"
            )
            return format_error_response("File content not found", 404)

        # Verify file integrity
        if file_data["checksum"]:
            if not file_storage.verify_file_integrity(
                file_data["file_path"], file_data["checksum"]
            ):
                logger.warning(f"File integrity check failed for ID {file_id}")

        # Convert datetime objects to ISO format
        file_data["created_at"] = file_data["created_at"].isoformat()
        file_data["updated_at"] = file_data["updated_at"].isoformat()
        file_data["content"] = content
        file_data["size_formatted"] = _format_file_size(file_data["file_size"])

        # Remove internal fields from response
        file_data.pop("file_path", None)
        file_data.pop("checksum", None)

        # Log activity
        log_activity(
            user_id, "read", "file", file_id, f"Accessed file: {file_data['name']}"
        )

        return format_success_response(file_data)

    except Exception as e:
        logger.error(f"Get file error: {e}")
        return format_error_response("Internal server error", 500)


@files_bp.route("/<int:file_id>", methods=["PATCH"])
@require_auth
def update_file(file_id):
    """Update file name and/or content."""
    try:
        user_id = g.current_user_id
        data = request.get_json()

        if not data:
            return format_error_response("Request body required", 400)

        # Check access
        if not check_file_access(user_id, file_id):
            return format_error_response("File not found or access denied", 404)

        # Get current file data
        current_file = db.execute_one(
            "SELECT name, file_path FROM files WHERE id = %s", (file_id,)
        )

        if not current_file:
            return format_error_response("File not found", 404)

        # Prepare update data
        updates = []
        params = []

        new_name = data.get("name")
        new_content = data.get("content")

        if new_name is not None:
            new_name = sanitize_filename(new_name.strip())
            if not new_name:
                return format_error_response("Invalid file name", 400)
            updates.append("name = %s")
            params.append(new_name)

        # Content is handled separately via filesystem operations
        # (don't add content to database updates since it's not stored in DB)

        if not updates and new_content is None:
            return format_error_response("No updates provided", 400)

        # Always update timestamp if there are any changes (name or content)
        now = datetime.now(timezone.utc)
        if updates or new_content is not None:
            updates.append("updated_at = %s")
            params.append(now)

        # Create file version before update if content is changing
        if new_content is not None:
            # Get current file path
            current_file_full = db.execute_one(
                "SELECT file_path, file_size, checksum FROM files WHERE id = %s",
                (file_id,),
            )

            if current_file_full and current_file_full["file_path"]:
                # Create version
                version_id = db.execute_modify(
                    """
                    INSERT INTO file_versions (file_id, version_path, file_size, checksum, created_at)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        file_id,
                        "",  # Will be updated after file copy
                        current_file_full["file_size"],
                        current_file_full["checksum"],
                        now,
                    ),
                )

                # Copy current file to version location
                try:
                    version_path = file_storage.generate_version_path(
                        file_id, version_id, current_file["name"]
                    )
                    # Check if source file exists before copying
                    if file_storage.file_exists(current_file_full["file_path"]):
                        file_storage.copy_file(
                            current_file_full["file_path"], version_path
                        )

                        # Update version record with actual path
                        db.execute_modify(
                            "UPDATE file_versions SET version_path = %s WHERE id = %s",
                            (version_path, version_id),
                        )
                except Exception as e:
                    logger.warning(f"Failed to create file version: {e}")
                    # Continue with update even if versioning fails

        # Handle content update - save to filesystem
        if new_content is not None:
            if current_file and current_file["file_path"]:
                # Save new content and get updated file info
                file_size, checksum = file_storage.save_file(
                    current_file["file_path"], new_content
                )

                # Add file size and checksum to updates
                updates.extend(["file_size = %s", "checksum = %s"])
                params.extend([file_size, checksum])

        # Update file metadata in database (only if there are updates)
        if updates:
            # Add file_id as the last parameter for WHERE clause
            params.append(file_id)
            query = f"UPDATE files SET {', '.join(updates)} WHERE id = %s"
            db.execute_modify(query, tuple(params))

        # Log activity
        changes = []
        if new_name is not None:
            changes.append(f"name: {current_file['name']} -> {new_name}")
        if new_content is not None:
            changes.append("content updated")

        log_activity(
            user_id, "update", "file", file_id, f"Updated file: {'; '.join(changes)}"
        )

        # Get updated file data
        updated_file = db.execute_one(
            """
            SELECT id, name, owner_id, team_id, created_at, updated_at
            FROM files
            WHERE id = %s
            """,
            (file_id,),
        )

        updated_file["created_at"] = updated_file["created_at"].isoformat()
        updated_file["updated_at"] = updated_file["updated_at"].isoformat()

        logger.info(f"File updated: ID {file_id} by user {user_id}")

        return format_success_response(updated_file, "File updated successfully")

    except Exception as e:
        logger.error(f"Update file error: {e}")
        return format_error_response("Internal server error", 500)


@files_bp.route("/<int:file_id>", methods=["DELETE"])
@require_auth
def delete_file(file_id):
    """Delete file (soft delete)."""
    try:
        user_id = g.current_user_id

        # Check access
        if not check_file_access(user_id, file_id):
            return format_error_response("File not found or access denied", 404)

        # Get file name for logging
        file_data = db.execute_one("SELECT name FROM files WHERE id = %s", (file_id,))

        if not file_data:
            return format_error_response("File not found", 404)

        # Soft delete - mark as deleted
        now = datetime.now(timezone.utc)
        db.execute_modify(
            "UPDATE files SET deleted_at = %s WHERE id = %s", (now, file_id)
        )

        # Log activity
        log_activity(
            user_id, "delete", "file", file_id, f"Deleted file: {file_data['name']}"
        )

        logger.info(
            f"File deleted: {file_data['name']} (ID: {file_id}) by user {user_id}"
        )

        return "", 204

    except Exception as e:
        logger.error(f"Delete file error: {e}")
        return format_error_response("Internal server error", 500)
