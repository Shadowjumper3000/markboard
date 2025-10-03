"""
Security utilities for file handling and sanitization.
"""

import re


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent directory traversal."""
    # Remove path separators and keep only safe characters
    sanitized = re.sub(r"[^\w\s.-]", "", filename)
    # Remove leading/trailing dots and spaces
    sanitized = sanitized.strip(". ")
    # Limit length
    return sanitized[:255] if sanitized else "untitled"


__all__ = ["sanitize_filename"]
