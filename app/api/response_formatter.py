"""
Response formatting utilities.
"""

from typing import Any, Dict, Optional


def format_error_response(
    message: str, status_code: int = 400
) -> tuple[Dict[str, str], int]:
    """Format error response consistently."""
    return {"error": message}, status_code


def format_success_response(
    data: Any = None, message: Optional[str] = None, status_code: int = 200
) -> tuple[Dict[str, Any], int]:
    """Format success response consistently."""
    response = {}
    if data is not None:
        if isinstance(data, dict):
            response.update(data)
        else:
            response["data"] = data
    if message:
        response["message"] = message

    return response, status_code


__all__ = ["format_error_response", "format_success_response"]
