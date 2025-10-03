"""
File storage utilities for managing files on the filesystem.
"""

import os
import hashlib
import shutil
import mimetypes
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple
import logging
from app.security import sanitize_filename
from app.storage.interface import StorageInterface

logger = logging.getLogger(__name__)


class FileStorage(StorageInterface):
    """Handles file storage operations on the filesystem."""

    def __init__(self, base_path: str = "/app/data"):
        """Initialize file storage with base path."""
        self.base_path = os.environ.get("FILE_STORAGE_DIR", "data/files")
        base_dir = self.base_path
        self.files_dir = Path(base_dir)
        self.files_dir.mkdir(parents=True, exist_ok=True)

        logger.info("File storage initialized at %s", self.base_path)

    def generate_file_path(self, file_id: int, filename: str) -> str:
        """Generate a structured file path based on file ID."""
        # Create subdirectories based on file ID to avoid too many files per directory
        subdir = str(file_id // 1000).zfill(3)  # Groups of 1000 files per directory
        file_dir = self.files_dir / subdir
        file_dir.mkdir(exist_ok=True)

        # Clean filename and add file ID to avoid conflicts
        clean_name = sanitize_filename(filename)
        return str(file_dir / f"{file_id}_{clean_name}")

    def save_file(self, file_path: str, content: str) -> Tuple[int, str]:
        """
        Save content to file and return size and checksum.

        Args:
            file_path: Full path where to save the file
            content: File content to save

        Returns:
            Tuple of (file_size, checksum)
        """
        try:
            # Ensure directory exists
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)

            # Write content to file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            # Calculate file size and checksum
            file_size = os.path.getsize(file_path)
            checksum = self._calculate_checksum(file_path)

            logger.info(
                "File saved: %s (%d bytes, checksum: %s...)",
                file_path,
                file_size,
                checksum[:8],
            )
            return file_size, checksum

        except Exception as e:
            logger.error("Failed to save file %s: %s", file_path, e)
            raise

    def read_file(self, file_path: str) -> str:
        """
        Read content from file.

        Args:
            file_path: Full path to the file

        Returns:
            File content as string
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            logger.debug("File read: %s (%d characters)", file_path, len(content))
            return content

        except Exception as e:
            logger.error("Failed to read file %s: %s", file_path, e)
            raise

    def delete_file(self, file_path: str) -> bool:
        """
        Delete file from filesystem.

        Args:
            file_path: Full path to the file

        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info("File deleted: %s", file_path)
                return True
            else:
                logger.warning("File not found for deletion: %s", file_path)
                return False

        except Exception as e:
            logger.error("Failed to delete file %s: %s", file_path, e)
            return False

    def move_file(self, src_path: str, dst_path: str) -> bool:
        """
        Move file from source to destination.

        Args:
            src_path: Source file path
            dst_path: Destination file path

        Returns:
            True if moved successfully, False otherwise
        """
        try:
            # Ensure destination directory exists
            Path(dst_path).parent.mkdir(parents=True, exist_ok=True)

            shutil.move(src_path, dst_path)
            logger.info("File moved: %s -> %s", src_path, dst_path)
            return True

        except Exception as e:
            logger.error("Failed to move file %s -> %s: %s", src_path, dst_path, e)
            return False

    def copy_file(self, src_path: str, dst_path: str) -> bool:
        """
        Copy file from source to destination.

        Args:
            src_path: Source file path
            dst_path: Destination file path

        Returns:
            True if copied successfully, False otherwise
        """
        try:
            # Ensure destination directory exists
            Path(dst_path).parent.mkdir(parents=True, exist_ok=True)

            shutil.copy2(src_path, dst_path)
            logger.info("File copied: %s -> %s", src_path, dst_path)
            return True

        except Exception as e:
            logger.error("Failed to copy file %s -> %s: %s", src_path, dst_path, e)
            return False

    def get_file_info(self, file_path: str) -> Optional[dict]:
        """
        Get file information including size, modified time, etc.

        Args:
            file_path: Full path to the file

        Returns:
            Dictionary with file info or None if file doesn't exist
        """
        try:
            if not os.path.exists(file_path):
                return None

            stat = os.stat(file_path)
            mime_type, _ = mimetypes.guess_type(file_path)

            return {
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime),
                "mime_type": mime_type or "text/plain",
                "checksum": self._calculate_checksum(file_path),
            }

        except Exception as e:
            logger.error("Failed to get file info for %s: %s", file_path, e)
            return None

    def file_exists(self, file_path: str) -> bool:
        """
        Check if file exists on filesystem.

        Args:
            file_path: Full path to the file

        Returns:
            True if file exists, False otherwise
        """
        try:
            return os.path.exists(file_path)
        except Exception as e:
            logger.error("Error checking file existence %s: %s", file_path, e)
            return False

    def verify_file_integrity(self, file_path: str, expected_checksum: str) -> bool:
        """
        Verify file integrity using checksum.

        Args:
            file_path: Full path to the file
            expected_checksum: Expected SHA-256 checksum

        Returns:
            True if file is intact, False otherwise
        """
        try:
            if not os.path.exists(file_path):
                return False

            actual_checksum = self._calculate_checksum(file_path)
            is_valid = actual_checksum == expected_checksum

            if not is_valid:
                logger.warning("File integrity check failed for %s", file_path)
                logger.warning("Expected: %s", expected_checksum)
                logger.warning("Actual: %s", actual_checksum)

            return is_valid

        except Exception as e:
            logger.error("Failed to verify file integrity for %s: %s", file_path, e)
            return False

    def cleanup_orphaned_files(self, referenced_files: set) -> int:
        """
        Clean up orphaned files that are not referenced in the database.

        Args:
            referenced_files: A set of file paths that are still referenced.

        Returns:
            Number of files cleaned up
        """
        cleaned_up_count = 0

        try:
            # Iterate through all files in the storage directory
            for root, _, files in os.walk(self.files_dir):
                for file in files:
                    file_path = os.path.join(root, file)

                    # Check if the file is not in the referenced set
                    if file_path not in referenced_files:
                        try:
                            os.remove(file_path)
                            logger.info("Deleted orphaned file: %s", file_path)
                            cleaned_up_count += 1
                        except Exception as e:
                            logger.error("Failed to delete file %s: %s", file_path, e)

        except Exception as e:
            logger.error("Error during orphaned file cleanup: %s", e)

        logger.info(
            "Orphaned file cleanup completed. Files removed: %d", cleaned_up_count
        )
        return cleaned_up_count

    def _calculate_checksum(self, file_path: str) -> str:
        """
        Calculate SHA-256 checksum of a file.

        Args:
            file_path: Full path to the file

        Returns:
            SHA-256 checksum as hex string
        """
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            # Read in chunks to handle large files
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()


# Global file storage instance
file_storage = FileStorage()
