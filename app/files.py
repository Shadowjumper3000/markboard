"""
File management endpoints - refactored to use services.
"""

import logging
from flask import Blueprint, request, g
from app.services.auth_service import AuthService
from app.response_format import format_error_response, format_success_response
from app.services.file_service import FileService

logger = logging.getLogger(__name__)

files_bp = Blueprint("files", __name__, url_prefix="/files")


@files_bp.route("", methods=["GET"])
@AuthService.require_auth
def list_files():
    """Get list of files accessible to the authenticated user."""
    try:
        user_id = g.current_user_id
        files = FileService.get_user_files(user_id)
        return format_success_response({"files": files})
    except Exception as e:
        logger.error("List files error: %s", e)
        return format_error_response("Internal server error", 500)


@files_bp.route("", methods=["POST"])
@AuthService.require_auth
def create_file():
    """Create a new file."""
    try:
        user_id = g.current_user_id
        data = request.get_json()

        if not data:
            return format_error_response("Request body is required", 400)

        name = data.get("name", "").strip()
        content = data.get("content", "")
        team_id = data.get("team_id")

        if not name:
            return format_error_response("File name is required", 400)

        # Validate team_id if provided
        if team_id is not None:
            try:
                team_id = int(team_id)
            except (ValueError, TypeError):
                return format_error_response("team_id must be an integer", 400)

        success, message, file_record = FileService.create_file(
            name, content, user_id, team_id
        )

        if not success:
            # Use 409 Conflict if file already exists, else 400
            if message and "already exists" in message.lower():
                return format_error_response(message, 409)
            return format_error_response(message, 400)

        return format_success_response(file_record, message, 201)

    except Exception as e:
        logger.error("Create file error: %s", e)
        return format_error_response("Internal server error", 500)


@files_bp.route("/<int:file_id>", methods=["GET"])
@AuthService.require_auth
def get_file(file_id):
    """Get file details and content."""
    try:
        user_id = g.current_user_id
        success, message, file_record = FileService.get_file_details(file_id, user_id)

        if not success:
            status_code = 404 if "not found" in message.lower() else 403
            return format_error_response(message, status_code)

        return format_success_response(file_record)
    except Exception as e:
        logger.error("Get file error: %s", e)
        return format_error_response("Internal server error", 500)


@files_bp.route("/<int:file_id>", methods=["PATCH"])
@AuthService.require_auth
def update_file(file_id):
    """Update file name and/or content."""
    try:
        user_id = g.current_user_id
        data = request.get_json()

        if not data:
            return format_error_response("Request body is required", 400)

        name = data.get("name")
        content = data.get("content")

        if name is not None and not name.strip():
            return format_error_response("File name cannot be empty", 400)

        success, message, file_record = FileService.update_file(
            file_id, user_id, name, content
        )

        if not success:
            status_code = (
                404
                if "not found" in message.lower()
                else 403 if "access denied" in message.lower() else 400
            )
            return format_error_response(message, status_code)

        return format_success_response(file_record, message)

    except Exception as e:
        logger.error("Update file error: %s", e)
        return format_error_response("Internal server error", 500)


@files_bp.route("/<int:file_id>", methods=["DELETE"])
@AuthService.require_auth
def delete_file(file_id):
    """Delete a file."""
    try:
        user_id = g.current_user_id
        success, message = FileService.delete_file(file_id, user_id)

        if not success:
            status_code = (
                404
                if "not found" in message.lower()
                else 403 if "access denied" in message.lower() else 400
            )
            return format_error_response(message, status_code)

        return format_success_response({"message": message})

    except Exception as e:
        logger.error("Delete file error: %s", e)
        return format_error_response("Internal server error", 500)


@files_bp.route("/<int:file_id>/content", methods=["GET"])
@AuthService.require_auth
def get_file_content(file_id):
    """Get file content only (for download functionality)."""
    try:
        user_id = g.current_user_id
        success, message, content = FileService.get_file_content(file_id, user_id)

        if not success:
            status_code = 404 if "not found" in message.lower() else 403
            return format_error_response(message, status_code)

        # Get file name for response
        _, _, name = FileService.get_file_name(file_id, user_id)

        return format_success_response({"content": content, "name": name})
    except Exception as e:
        logger.error("Get file content error: %s", e)
        return format_error_response("Internal server error", 500)
