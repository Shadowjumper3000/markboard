"""
File management endpoints.
"""

from datetime import datetime, timezone
from flask import Blueprint, request, jsonify, g
from app.db import db
from app.utils import (
    require_auth,
    check_file_access,
    sanitize_filename,
    log_activity,
    format_error_response,
    format_success_response,
)
import logging

logger = logging.getLogger(__name__)

files_bp = Blueprint("files", __name__, url_prefix="/files")


@files_bp.route("", methods=["GET"])
@require_auth
def list_files():
    """Get list of files for authenticated user."""
    try:
        user_id = g.current_user_id

        query = """
            SELECT DISTINCT f.id, f.name, f.created_at, f.updated_at, f.owner_id, f.team_id
            FROM files f
            LEFT JOIN team_members tm ON f.team_id = tm.team_id AND tm.user_id = %s
            WHERE f.owner_id = %s OR tm.user_id IS NOT NULL
            ORDER BY f.updated_at DESC
        """

        files = db.execute_query(query, (user_id, user_id))

        # Convert datetime objects to ISO format
        for file in files:
            file["created_at"] = file["created_at"].isoformat()
            file["updated_at"] = file["updated_at"].isoformat()

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

        # Create file
        now = datetime.now(timezone.utc)
        file_id = db.execute_modify(
            """
            INSERT INTO files (name, content, owner_id, team_id, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (name, content, user_id, team_id, now, now),
        )

        # Log activity
        log_activity(user_id, "create", "file", file_id, f"Created file: {name}")

        # Return created file metadata
        file_data = {
            "id": file_id,
            "name": name,
            "content": content,
            "owner_id": user_id,
            "team_id": team_id,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
        }

        logger.info(f"File created: {name} (ID: {file_id}) by user {user_id}")

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

        # Get file data
        file_data = db.execute_one(
            """
            SELECT id, name, content, owner_id, team_id, created_at, updated_at
            FROM files
            WHERE id = %s
            """,
            (file_id,),
        )

        if not file_data:
            return format_error_response("File not found", 404)

        # Convert datetime objects to ISO format
        file_data["created_at"] = file_data["created_at"].isoformat()
        file_data["updated_at"] = file_data["updated_at"].isoformat()

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
            "SELECT name, content FROM files WHERE id = %s", (file_id,)
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

        if new_content is not None:
            updates.append("content = %s")
            params.append(new_content)

        if not updates:
            return format_error_response("No updates provided", 400)

        # Update timestamp
        now = datetime.now(timezone.utc)
        updates.append("updated_at = %s")
        params.append(now)
        params.append(file_id)

        # Create file version before update
        db.execute_modify(
            """
            INSERT INTO file_versions (file_id, content, created_at)
            VALUES (%s, %s, %s)
            """,
            (file_id, current_file["content"], now),
        )

        # Update file
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
            SELECT id, name, content, owner_id, team_id, created_at, updated_at
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
