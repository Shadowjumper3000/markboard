"""
Database connection and query utilities.
"""

from contextlib import contextmanager
from typing import Optional, List, Dict, Any
import logging
import time
from mysql.connector.pooling import MySQLConnectionPool
from mysql.connector import Error
from app.config import Config

logger = logging.getLogger(__name__)


class Database:
    """Database connection pool manager."""

    def __init__(self):
        self.pool = None
        self.init_pool()

    def init_pool(self, max_retries=5, retry_delay=2):
        """Initialize connection pool with retry logic."""
        for attempt in range(1, max_retries + 1):
            try:
                config = {
                    "host": Config.MYSQL_HOST,
                    "port": Config.MYSQL_PORT,
                    "user": Config.MYSQL_USER,
                    "password": Config.MYSQL_PASSWORD,
                    "database": Config.MYSQL_DATABASE,
                    "pool_name": "markboard_pool",
                    "pool_size": 10,
                    "pool_reset_session": True,
                    "autocommit": True,
                    "charset": "utf8mb4",
                    "collation": "utf8mb4_unicode_ci",
                    "auth_plugin": "mysql_native_password",
                    "sql_mode": "TRADITIONAL",
                    "use_unicode": True,
                    "get_warnings": True,
                }

                self.pool = MySQLConnectionPool(**config)
                logger.info("Database connection pool initialized successfully")
                return

            except Error as e:
                logger.warning(
                    f"Failed to create connection pool (attempt {attempt}/{max_retries}): {e}"
                )
                if attempt < max_retries:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    continue
                else:
                    logger.error("Failed to initialize database pool after all retries")
                    raise

    @contextmanager
    def get_connection(self):
        """Get a connection from the pool."""
        connection = None
        try:
            connection = self.pool.get_connection()
            yield connection
        except Error as e:
            if connection:
                connection.rollback()
            logger.error("Database error: %s", e)
            raise
        finally:
            if connection and connection.is_connected():
                connection.close()

    def execute_query(
        self, query: str, params: Optional[tuple] = None
    ) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results."""
        logger.debug("Executing query: %s with params: %s", query, params)
        with self.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, params)
            results = cursor.fetchall()
            logger.debug("Query returned %s rows", len(results))
            cursor.close()
            return results

    def execute_one(
        self, query: str, params: Optional[tuple] = None
    ) -> Optional[Dict[str, Any]]:
        """Execute a SELECT query and return single result."""
        logger.debug("Executing single query: %s with params: %s", query, params)
        with self.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, params)
            result = cursor.fetchone()
            logger.debug("Query returned: %s", result)
            cursor.close()
            return result

    def execute_modify(self, query: str, params: Optional[tuple] = None) -> int:
        """Execute INSERT, UPDATE, or DELETE query and return affected rows or lastrowid for INSERT."""
        logger.debug("Executing modify query: %s with params: %s", query, params)
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            logger.debug(
                "Query affected %s rows, returned %s", cursor.rowcount, cursor.lastrowid
            )
            # Return lastrowid for INSERT, else rowcount
            if query.strip().lower().startswith("insert"):
                result = cursor.lastrowid
            else:
                result = cursor.rowcount
            cursor.close()
            return result

    def execute_transaction(self, queries: List[tuple]) -> bool:
        """Execute multiple queries in a transaction."""
        logger.debug("Executing transaction with %s queries", len(queries))
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                conn.start_transaction()
                for i, (query, params) in enumerate(queries):
                    logger.debug(
                        "Transaction query %i: %s with %s", i + 1, query, params
                    )
                    cursor.execute(query, params)
                conn.commit()
                logger.debug("Transaction committed successfully")
                cursor.close()
                return True
            except Error as e:
                conn.rollback()
                logger.error("Transaction failed and rolled back: %s", e)
                cursor.close()
                raise

    def test_connection(self) -> bool:
        """Test database connection."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                cursor.close()
                return True
        except Error as e:
            logger.error("Database connection test failed: %s", e)
            return False


# Lazy-initialized global database instance
_db_instance = None


def get_db():
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance
