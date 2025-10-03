"""
Abstract storage interface for file operations.
Follows the Dependency Inversion Principle by defining contracts.
"""

from abc import ABC, abstractmethod
from typing import Optional, Tuple


class StorageInterface(ABC):
    """Abstract interface for file storage operations."""

    @abstractmethod
    def generate_file_path(self, file_id: int, filename: str) -> str:
        """Generate a structured file path based on file ID."""
        pass

    @abstractmethod
    def save_file(self, file_path: str, content: str) -> Tuple[int, str]:
        """
        Save content to file and return size and checksum.
        Returns: Tuple of (file_size, checksum)
        """
        pass

    @abstractmethod
    def read_file(self, file_path: str) -> str:
        """Read content from file."""
        pass

    @abstractmethod
    def delete_file(self, file_path: str) -> bool:
        """Delete file from storage."""
        pass

    @abstractmethod
    def move_file(self, src_path: str, dst_path: str) -> bool:
        """Move file from source to destination."""
        pass

    @abstractmethod
    def copy_file(self, src_path: str, dst_path: str) -> bool:
        """Copy file from source to destination."""
        pass

    @abstractmethod
    def get_file_info(self, file_path: str) -> Optional[dict]:
        """Get file information including size, modified time, etc."""
        pass

    @abstractmethod
    def file_exists(self, file_path: str) -> bool:
        """Check if file exists in storage."""
        pass

    @abstractmethod
    def verify_file_integrity(self, file_path: str, expected_checksum: str) -> bool:
        """Verify file integrity using checksum."""
        pass

    @abstractmethod
    def cleanup_orphaned_files(self, referenced_files: set) -> int:
        """Clean up orphaned files that are not referenced."""
        pass
