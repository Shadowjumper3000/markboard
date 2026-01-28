"""
Database migration system - automatically applies pending migrations on startup.
"""

import logging
import os
from pathlib import Path
from typing import List, Tuple
from app.infrastructure.database.connection import get_db

logger = logging.getLogger(__name__)


class MigrationManager:
    """Manages database migrations."""

    @staticmethod
    def _ensure_migrations_table():
        """Create migrations tracking table if it doesn't exist."""
        query = """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                migration_name VARCHAR(255) NOT NULL UNIQUE,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_migration_name (migration_name)
            )
        """
        try:
            get_db().execute_modify(query, ())
            logger.info("Migrations tracking table verified")
        except Exception as e:
            logger.error(f"Error creating migrations table: {e}")
            raise

    @staticmethod
    def _get_applied_migrations() -> List[str]:
        """Get list of already applied migrations."""
        query = "SELECT migration_name FROM schema_migrations ORDER BY migration_name"
        try:
            results = get_db().execute_query(query, ())
            return [row["migration_name"] for row in results]
        except Exception as e:
            logger.error(f"Error fetching applied migrations: {e}")
            return []

    @staticmethod
    def _mark_migration_applied(migration_name: str):
        """Mark a migration as applied."""
        query = "INSERT INTO schema_migrations (migration_name) VALUES (%s)"
        try:
            get_db().execute_modify(query, (migration_name,))
            logger.info(f"Marked migration as applied: {migration_name}")
        except Exception as e:
            logger.error(f"Error marking migration as applied: {e}")
            raise

    @staticmethod
    def _get_migration_files() -> List[Tuple[str, Path]]:
        """Get all migration files sorted by name."""
        # Get path to migrations directory
        current_file = Path(__file__)
        migrations_dir = current_file.parent / "migrations"

        if not migrations_dir.exists():
            logger.warning(f"Migrations directory not found: {migrations_dir}")
            return []

        # Get all .sql files
        migration_files = []
        for file_path in sorted(migrations_dir.glob("*.sql")):
            migration_files.append((file_path.name, file_path))

        return migration_files

    @staticmethod
    def _apply_migration(migration_name: str, migration_path: Path) -> bool:
        """Apply a single migration file."""
        try:
            logger.info(f"Applying migration: {migration_name}")

            # Read migration file
            with open(migration_path, "r") as f:
                sql_content = f.read()

            # Split by semicolon and execute each statement
            statements = [
                stmt.strip() for stmt in sql_content.split(";") if stmt.strip()
            ]

            for statement in statements:
                if statement:
                    get_db().execute_modify(statement, ())

            # Mark as applied
            MigrationManager._mark_migration_applied(migration_name)
            logger.info(f"✅ Successfully applied migration: {migration_name}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to apply migration {migration_name}: {e}")
            return False

    @staticmethod
    def run_migrations():
        """Run all pending migrations."""
        try:
            logger.info("=== Starting migration check ===")

            # Ensure migrations table exists
            MigrationManager._ensure_migrations_table()

            # Get applied migrations
            applied_migrations = MigrationManager._get_applied_migrations()
            logger.info(
                f"Found {len(applied_migrations)} previously applied migrations"
            )

            # Get all migration files
            migration_files = MigrationManager._get_migration_files()
            logger.info(f"Found {len(migration_files)} migration files")

            # Find pending migrations
            pending_migrations = [
                (name, path)
                for name, path in migration_files
                if name not in applied_migrations
            ]

            if not pending_migrations:
                logger.info("✅ No pending migrations")
                return

            logger.info(f"Found {len(pending_migrations)} pending migrations")

            # Apply each pending migration
            success_count = 0
            for migration_name, migration_path in pending_migrations:
                if MigrationManager._apply_migration(migration_name, migration_path):
                    success_count += 1
                else:
                    logger.error(f"Migration failed, stopping migration process")
                    break

            logger.info(
                f"=== Migration complete: {success_count}/{len(pending_migrations)} applied ==="
            )

        except Exception as e:
            logger.error(f"Migration system error: {e}")
            raise
