"""
Abstract storage interface for file operations.
Follows the Dependency Inversion Principle by defining contracts.
"""

from abc import ABC, abstractmethod
from typing import Optional, Tuple, Protocol, List, Dict, Any


class StorageInterface(ABC):
    """Abstract interface for file storage operations."""

    @abstractmethod
    def generate_file_path(self, file_id: int, filename: str) -> str:
        """Generate a structured file path based on file ID."""

    @abstractmethod
    def save_file(self, file_path: str, content: str) -> Tuple[int, str]:
        """
        Save content to file and return size and checksum.
        Returns: Tuple of (file_size, checksum)
        """

    @abstractmethod
    def read_file(self, file_path: str) -> str:
        """Read content from file."""

    @abstractmethod
    def delete_file(self, file_path: str) -> bool:
        """Delete file from storage."""

    @abstractmethod
    def move_file(self, src_path: str, dst_path: str) -> bool:
        """Move file from source to destination."""

    @abstractmethod
    def copy_file(self, src_path: str, dst_path: str) -> bool:
        """Copy file from source to destination."""

    @abstractmethod
    def get_file_info(self, file_path: str) -> Optional[dict]:
        """Get file information including size, modified time, etc."""

    @abstractmethod
    def file_exists(self, file_path: str) -> bool:
        """Check if file exists in storage."""

    @abstractmethod
    def verify_file_integrity(self, file_path: str, expected_checksum: str) -> bool:
        """Verify file integrity using checksum."""

    @abstractmethod
    def cleanup_orphaned_files(self, referenced_files: set) -> int:
        """Clean up orphaned files that are not referenced."""


class DatabaseInterface(Protocol):
    """Abstract interface for database operations."""

    def execute_query(
        self, query: str, params: Optional[tuple] = None
    ) -> List[Dict[str, Any]]:
        """Execute a query and return the result set."""

    def execute_one(
        self, query: str, params: Optional[tuple] = None
    ) -> Optional[Dict[str, Any]]:
        """Execute a query and return a single result row."""

    def execute_modify(self, query: str, params: Optional[tuple] = None) -> int:
        """Execute a modification query (INSERT, UPDATE, DELETE) and return the number of affected rows."""

    def execute_transaction(self, queries: List[tuple]) -> bool:
        """Execute a series of queries as a single transaction."""

    def test_connection(self) -> bool:
        """Test the database connection."""
