"""
Database tests - focused on core functionality and logging.
"""

import pytest
import logging
from mysql.connector import Error
from unittest.mock import patch, MagicMock

from app.db import Database


class TestDatabaseCore:
    """Test core database functionality."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database instance for testing."""
        with patch("mysql.connector.pooling.MySQLConnectionPool") as mock_pool:
            mock_connection = MagicMock()
            mock_connection.is_connected.return_value = True
            mock_pool_instance = MagicMock()
            mock_pool_instance.get_connection.return_value = mock_connection
            mock_pool.return_value = mock_pool_instance

            db = Database()
            yield db, mock_connection

    def test_connection_pool_creation(self):
        """Test database connection pool is created with correct settings."""
        with patch("mysql.connector.pooling.MySQLConnectionPool") as mock_pool:
            mock_pool.return_value = MagicMock()

            Database()

            # Verify pool was created
            mock_pool.assert_called_once()
            kwargs = mock_pool.call_args[1]
            assert kwargs["pool_name"] == "markboard_pool"
            assert kwargs["pool_size"] == 10
            assert kwargs["charset"] == "utf8mb4"
            assert kwargs["collation"] == "utf8mb4_unicode_ci"

    def test_execute_query_logging(self, mock_db, caplog):
        """Test that database queries are properly logged."""
        db, mock_connection = mock_db
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [{"id": 1}]
        mock_connection.cursor.return_value = mock_cursor

        with patch.object(db, "get_connection") as mock_get_conn:
            mock_get_conn.return_value.__enter__.return_value = mock_connection

            with caplog.at_level(logging.DEBUG):
                result = db.execute_query("SELECT * FROM users", (123,))

        # Verify query was executed
        mock_cursor.execute.assert_called_once_with("SELECT * FROM users", (123,))
        assert result == [{"id": 1}]

        # Verify logging
        assert "Executing query: SELECT * FROM users" in caplog.text
        assert "Query returned 1 rows" in caplog.text

    def test_execute_one_logging(self, mock_db, caplog):
        """Test single query execution and logging."""
        db, mock_connection = mock_db
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {"id": 1, "name": "test"}
        mock_connection.cursor.return_value = mock_cursor

        with patch.object(db, "get_connection") as mock_get_conn:
            mock_get_conn.return_value.__enter__.return_value = mock_connection

            with caplog.at_level(logging.DEBUG):
                result = db.execute_one("SELECT * FROM users WHERE id = %s", (1,))

        # Verify result
        assert result == {"id": 1, "name": "test"}

        # Verify logging
        assert "Executing single query" in caplog.text
        assert "Query returned: 1 row" in caplog.text

    def test_execute_one_no_result(self, mock_db, caplog):
        """Test single query with no result."""
        db, mock_connection = mock_db
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_connection.cursor.return_value = mock_cursor

        with patch.object(db, "get_connection") as mock_get_conn:
            mock_get_conn.return_value.__enter__.return_value = mock_connection

            with caplog.at_level(logging.DEBUG):
                result = db.execute_one("SELECT * FROM users WHERE id = %s", (999,))

        assert result is None
        assert "Query returned: no rows" in caplog.text

    def test_execute_modify_insert(self, mock_db, caplog):
        """Test INSERT query execution and logging."""
        db, mock_connection = mock_db
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 1
        mock_cursor.lastrowid = 42
        mock_connection.cursor.return_value = mock_cursor

        with patch.object(db, "get_connection") as mock_get_conn:
            mock_get_conn.return_value.__enter__.return_value = mock_connection

            with caplog.at_level(logging.DEBUG):
                result = db.execute_modify(
                    "INSERT INTO users (name) VALUES (%s)", ("John Doe",)
                )

        # Verify INSERT returns lastrowid
        assert result == 42

        # Verify commit was called
        mock_connection.commit.assert_called_once()

        # Verify logging
        assert "Executing modify query" in caplog.text
        assert "Query affected 1 rows, returned 42" in caplog.text

    def test_execute_modify_update(self, mock_db, caplog):
        """Test UPDATE query execution."""
        db, mock_connection = mock_db
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 3
        mock_cursor.lastrowid = 0
        mock_connection.cursor.return_value = mock_cursor

        with patch.object(db, "get_connection") as mock_get_conn:
            mock_get_conn.return_value.__enter__.return_value = mock_connection

            with caplog.at_level(logging.DEBUG):
                result = db.execute_modify("UPDATE users SET active = %s", (True,))

        # Verify UPDATE returns rowcount
        assert result == 3

        # Verify logging
        assert "Query affected 3 rows, returned 3" in caplog.text

    def test_transaction_success(self, mock_db, caplog):
        """Test successful transaction execution and logging."""
        db, mock_connection = mock_db
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor

        queries = [
            ("INSERT INTO users (name) VALUES (%s)", ("Alice",)),
            ("UPDATE users SET active = %s WHERE name = %s", (True, "Alice")),
        ]

        with patch.object(db, "get_connection") as mock_get_conn:
            mock_get_conn.return_value.__enter__.return_value = mock_connection

            with caplog.at_level(logging.DEBUG):
                result = db.execute_transaction(queries)

        # Verify transaction handling
        mock_connection.start_transaction.assert_called_once()
        mock_connection.commit.assert_called_once()
        assert result is True

        # Verify all queries were executed
        assert mock_cursor.execute.call_count == 2

        # Verify logging
        assert "Executing transaction with 2 queries" in caplog.text
        assert "Transaction query 1:" in caplog.text
        assert "Transaction query 2:" in caplog.text
        assert "Transaction committed successfully" in caplog.text

    def test_transaction_rollback(self, mock_db, caplog):
        """Test transaction rollback on error."""
        db, mock_connection = mock_db
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = [None, Error("Query failed")]
        mock_connection.cursor.return_value = mock_cursor

        queries = [
            ("INSERT INTO users (name) VALUES (%s)", ("Bob",)),
            ("INVALID QUERY", ()),
        ]

        with patch.object(db, "get_connection") as mock_get_conn:
            mock_get_conn.return_value.__enter__.return_value = mock_connection

            with pytest.raises(Error):
                with caplog.at_level(logging.DEBUG):
                    db.execute_transaction(queries)

        # Verify rollback was called
        mock_connection.rollback.assert_called_once()

        # Verify logging
        assert "Transaction failed and rolled back" in caplog.text

    def test_connection_test_success(self, mock_db):
        """Test successful database connection test."""
        db, mock_connection = mock_db
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (1,)
        mock_connection.cursor.return_value = mock_cursor

        with patch.object(db, "get_connection") as mock_get_conn:
            mock_get_conn.return_value.__enter__.return_value = mock_connection

            result = db.test_connection()

        # Verify test query
        mock_cursor.execute.assert_called_once_with("SELECT 1")
        assert result is True

    def test_connection_test_failure(self, mock_db, caplog):
        """Test connection test failure and logging."""
        db, mock_connection = mock_db
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = Error("Connection failed")
        mock_connection.cursor.return_value = mock_cursor

        with patch.object(db, "get_connection") as mock_get_conn:
            mock_get_conn.return_value.__enter__.return_value = mock_connection

            with caplog.at_level(logging.ERROR):
                result = db.test_connection()

        assert result is False
        assert "Database connection test failed" in caplog.text

    def test_error_handling_in_queries(self, mock_db, caplog):
        """Test that database errors are properly handled and logged."""
        db, mock_connection = mock_db
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = Error("Table doesn't exist")
        mock_connection.cursor.return_value = mock_cursor

        with patch.object(db, "get_connection") as mock_get_conn:
            mock_get_conn.return_value.__enter__.return_value = mock_connection

            with pytest.raises(Error):
                db.execute_query("SELECT * FROM nonexistent_table")

        # Verify connection rollback was called due to error
        mock_connection.rollback.assert_called_once()

    def test_connection_cleanup(self, mock_db):
        """Test that connections are properly cleaned up."""
        db, mock_connection = mock_db
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_connection.cursor.return_value = mock_cursor

        with patch.object(db, "get_connection") as mock_get_conn:
            mock_get_conn.return_value.__enter__.return_value = mock_connection

            # Execute a query
            db.execute_query("SELECT 1")

        # Verify cursor was closed
        mock_cursor.close.assert_called_once()

    def test_parameter_handling(self, mock_db):
        """Test proper handling of query parameters."""
        db, mock_connection = mock_db
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_connection.cursor.return_value = mock_cursor

        test_cases = [
            ("SELECT * FROM users", None),
            ("SELECT * FROM users WHERE id = %s", (1,)),
            ("SELECT * FROM users WHERE name = %s AND age = %s", ("John", 25)),
        ]

        with patch.object(db, "get_connection") as mock_get_conn:
            mock_get_conn.return_value.__enter__.return_value = mock_connection

            for query, params in test_cases:
                db.execute_query(query, params)

                # Verify parameters were passed correctly
                last_call = mock_cursor.execute.call_args
                assert last_call[0][0] == query
                assert last_call[0][1] == params


class TestDatabaseLogging:
    """Test database logging functionality."""

    def test_debug_logging_enabled(self, caplog):
        """Test that debug logging works when enabled."""
        with patch("mysql.connector.pooling.MySQLConnectionPool"):
            with caplog.at_level(logging.DEBUG):
                Database()

        # Should have initialization log
        assert "Database connection pool initialized successfully" in caplog.text

    def test_info_logging_level(self, caplog):
        """Test logging at INFO level."""
        with patch("mysql.connector.pooling.MySQLConnectionPool"):
            with caplog.at_level(logging.INFO):
                Database()

        # Should have initialization log at INFO level too
        assert "Database connection pool initialized successfully" in caplog.text

    def test_error_logging(self, caplog):
        """Test error logging on connection failure."""
        with patch("mysql.connector.pooling.MySQLConnectionPool") as mock_pool:
            mock_pool.side_effect = Error("Database connection failed")

            with pytest.raises(Error):
                with caplog.at_level(logging.ERROR):
                    Database()

        assert "Failed to create connection pool" in caplog.text


class TestDatabaseIntegration:
    """Integration-style tests for database operations."""

    def test_file_operations_logging(self, caplog):
        """Test that file operations generate appropriate logs."""
        with patch("mysql.connector.pooling.MySQLConnectionPool") as mock_pool:
            mock_connection = MagicMock()
            mock_connection.is_connected.return_value = True
            mock_cursor = MagicMock()
            mock_cursor.fetchall.return_value = []
            mock_cursor.lastrowid = 1
            mock_cursor.rowcount = 1
            mock_connection.cursor.return_value = mock_cursor
            mock_pool_instance = MagicMock()
            mock_pool_instance.get_connection.return_value = mock_connection
            mock_pool.return_value = mock_pool_instance

            db = Database()

            with patch.object(db, "get_connection") as mock_get_conn:
                mock_get_conn.return_value.__enter__.return_value = mock_connection

                with caplog.at_level(logging.DEBUG):
                    # Simulate typical file operations
                    db.execute_query("SELECT * FROM files WHERE owner_id = %s", (1,))
                    db.execute_modify(
                        "INSERT INTO files (name, content) VALUES (%s, %s)",
                        ("test.md", "# Test"),
                    )
                    db.execute_one("SELECT * FROM files WHERE id = %s", (1,))

        # Verify all operations were logged
        log_text = caplog.text
        assert "Executing query: SELECT * FROM files" in log_text
        assert "Executing modify query: INSERT INTO files" in log_text
        assert "Executing single query: SELECT * FROM files" in log_text

    def test_user_operations_logging(self, caplog):
        """Test that user operations generate appropriate logs."""
        with patch("mysql.connector.pooling.MySQLConnectionPool") as mock_pool:
            mock_connection = MagicMock()
            mock_connection.is_connected.return_value = True
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = {"id": 1, "email": "test@example.com"}
            mock_cursor.lastrowid = 1
            mock_cursor.rowcount = 1
            mock_connection.cursor.return_value = mock_cursor
            mock_pool_instance = MagicMock()
            mock_pool_instance.get_connection.return_value = mock_connection
            mock_pool.return_value = mock_pool_instance

            db = Database()

            with patch.object(db, "get_connection") as mock_get_conn:
                mock_get_conn.return_value.__enter__.return_value = mock_connection

                with caplog.at_level(logging.DEBUG):
                    # Simulate user authentication flow
                    db.execute_one(
                        "SELECT * FROM users WHERE email = %s", ("test@example.com",)
                    )
                    db.execute_modify(
                        "INSERT INTO activity_logs (user_id, action) VALUES (%s, %s)",
                        (1, "login"),
                    )

        # Verify operations were logged with appropriate detail
        log_text = caplog.text
        assert "Executing single query" in log_text
        assert "SELECT * FROM users WHERE email" in log_text
        assert "INSERT INTO activity_logs" in log_text
