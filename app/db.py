"""
Database connection and query utilities.
"""

import mysql.connector
from mysql.connector import pooling, Error
from contextlib import contextmanager
from typing import Optional, List, Dict, Any
import logging
from app.config import Config

logger = logging.getLogger(__name__)


class Database:
    """Database connection pool manager."""

    def __init__(self):
        self.pool = None
        self.init_pool()

    def init_pool(self):
        """Initialize connection pool."""
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
            }

            self.pool = pooling.MySQLConnectionPool(**config)
            logger.info("Database connection pool initialized successfully")

        except Error as e:
            logger.error(f"Failed to create connection pool: {e}")
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
            logger.error(f"Database error: {e}")
            raise
        finally:
            if connection and connection.is_connected():
                connection.close()

    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results."""
        logger.debug(f"Executing query: {query} with params: {params}")
        with self.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, params)
            results = cursor.fetchall()
            logger.debug(f"Query returned {len(results)} rows")
            cursor.close()
            return results

    def execute_one(self, query: str, params: tuple = None) -> Optional[Dict[str, Any]]:
        """Execute a SELECT query and return single result."""
        logger.debug(f"Executing single query: {query} with params: {params}")
        with self.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, params)
            result = cursor.fetchone()
            logger.debug(f"Query returned: {'1 row' if result else 'no rows'}")
            cursor.close()
            return result

    def execute_modify(self, query: str, params: tuple = None) -> int:
        """Execute INSERT, UPDATE, or DELETE query and return affected rows."""
        logger.debug(f"Executing modify query: {query} with params: {params}")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            affected_rows = cursor.rowcount
            last_id = cursor.lastrowid
            cursor.close()
            is_insert = query.strip().upper().startswith("INSERT")
            result = last_id if is_insert else affected_rows
            logger.debug(f"Query affected {affected_rows} rows, returned {result}")
            return result

    def execute_transaction(self, queries: List[tuple]) -> bool:
        """Execute multiple queries in a transaction."""
        logger.debug(f"Executing transaction with {len(queries)} queries")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                conn.start_transaction()
                for i, (query, params) in enumerate(queries):
                    logger.debug(f"Transaction query {i+1}: {query} with {params}")
                    cursor.execute(query, params)
                conn.commit()
                logger.debug("Transaction committed successfully")
                cursor.close()
                return True
            except Error as e:
                conn.rollback()
                logger.error(f"Transaction failed and rolled back: {e}")
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
            logger.error(f"Database connection test failed: {e}")
            return False


# Global database instance
db = Database()
