"""
Database layer tests.
"""

import pytest
import logging
from mysql.connector import Error
from unittest.mock import patch, MagicMock

from app.db import Database
from app.config import Config


class TestDatabaseConnection:
    """Test database connection and pool management."""

    def test_init_pool_success(self):
        """Test successful database pool initialization."""
        with patch("mysql.connector.pooling.MySQLConnectionPool") as mock_pool:
            mock_pool_instance = MagicMock()
            mock_pool.return_value = mock_pool_instance

            db = Database()

            # Verify pool was created with correct config
            mock_pool.assert_called_once()
            args, kwargs = mock_pool.call_args
            assert kwargs["host"] == Config.MYSQL_HOST
            assert kwargs["port"] == Config.MYSQL_PORT
            assert kwargs["user"] == Config.MYSQL_USER
            assert kwargs["password"] == Config.MYSQL_PASSWORD
            assert kwargs["database"] == Config.MYSQL_DATABASE
            assert kwargs["pool_name"] == "markboard_pool"
            assert kwargs["pool_size"] == 10
            assert kwargs["pool_reset_session"] is True
            assert kwargs["autocommit"] is True
            assert kwargs["charset"] == "utf8mb4"
            assert kwargs["collation"] == "utf8mb4_unicode_ci"

            assert db.pool == mock_pool_instance

    def test_init_pool_failure(self):
        """Test database pool initialization failure."""
        with patch("mysql.connector.pooling.MySQLConnectionPool") as mock_pool:
            mock_pool.side_effect = Error("Connection failed")

            with pytest.raises(Error):
                Database()

    def test_get_connection_success(self):
        """Test successful connection retrieval from pool."""
        with patch("mysql.connector.pooling.MySQLConnectionPool") as mock_pool:
            mock_connection = MagicMock()
            mock_connection.is_connected.return_value = True
            mock_pool_instance = MagicMock()
            mock_pool_instance.get_connection.return_value = mock_connection
            mock_pool.return_value = mock_pool_instance

            db = Database()

            with db.get_connection() as conn:
                assert conn == mock_connection
                # Connection is properly retrieved
                mock_pool_instance.get_connection.assert_called_once()

            # Verify connection was closed
            mock_connection.close.assert_called_once()

    def test_get_connection_with_error(self):
        """Test connection handling when database error occurs."""
        with patch("mysql.connector.pooling.MySQLConnectionPool") as mock_pool:
            mock_connection = MagicMock()
            mock_connection.is_connected.return_value = True
            mock_pool_instance = MagicMock()
            mock_pool_instance.get_connection.return_value = mock_connection
            mock_pool.return_value = mock_pool_instance

            db = Database()

            with pytest.raises(Error):
                with db.get_connection() as conn:
                    raise Error("Database operation failed")

            # Verify rollback and close were called
            mock_connection.rollback.assert_called_once()
            mock_connection.close.assert_called_once()

    def test_get_connection_cleanup_on_disconnect(self):
        """Test connection cleanup when connection is not active."""
        with patch("mysql.connector.pooling.MySQLConnectionPool") as mock_pool:
            mock_connection = MagicMock()
            mock_connection.is_connected.return_value = False
            mock_pool_instance = MagicMock()
            mock_pool_instance.get_connection.return_value = mock_connection
            mock_pool.return_value = mock_pool_instance

            db = Database()

            with db.get_connection() as conn:
                assert conn == mock_connection

            # Close should not be called if connection is not connected
            mock_connection.close.assert_not_called()


class TestDatabaseQueries:
    """Test database query methods."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database instance."""
        with patch("mysql.connector.pooling.MySQLConnectionPool") as mock_pool:
            mock_connection = MagicMock()
            mock_connection.is_connected.return_value = True
            mock_pool_instance = MagicMock()
            mock_pool_instance.get_connection.return_value = mock_connection
            mock_pool.return_value = mock_pool_instance

            db = Database()
            db._test_connection = mock_connection

            yield db, mock_connection

    def test_execute_query_success(self, mock_db, caplog):
        """Test successful SELECT query execution."""
        db, mock_connection = mock_db
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            {"id": 1, "name": "test1"},
            {"id": 2, "name": "test2"},
        ]
        mock_connection.cursor.return_value = mock_cursor

        with patch.object(db, "get_connection") as mock_get_conn:
            mock_get_conn.return_value.__enter__.return_value = mock_connection

            with caplog.at_level(logging.DEBUG):
                result = db.execute_query("SELECT * FROM test", ("param1", "param2"))

        # Verify query execution
        mock_connection.cursor.assert_called_once_with(dictionary=True)
        mock_cursor.execute.assert_called_once_with(
            "SELECT * FROM test", ("param1", "param2")
        )
        mock_cursor.fetchall.assert_called_once()
        mock_cursor.close.assert_called_once()

        # Verify result
        expected_result = [{"id": 1, "name": "test1"}, {"id": 2, "name": "test2"}]
        assert result == expected_result

        # Verify logging
        expected_log = (
            "Executing query: SELECT * FROM test with params: " "('param1', 'param2')"
        )
        assert expected_log in caplog.text
        assert "Query returned 2 rows" in caplog.text

    def test_execute_one_success(self, mock_db, caplog):
        """Test successful single row query execution."""
        db, mock_connection = mock_db
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {"id": 1, "name": "test"}
        mock_connection.cursor.return_value = mock_cursor

        with patch.object(db, "get_connection") as mock_get_conn:
            mock_get_conn.return_value.__enter__.return_value = mock_connection

            with caplog.at_level(logging.DEBUG):
                result = db.execute_one("SELECT * FROM test WHERE id = %s", (1,))

        # Verify query execution
        mock_connection.cursor.assert_called_once_with(dictionary=True)
        mock_cursor.execute.assert_called_once_with(
            "SELECT * FROM test WHERE id = %s", (1,)
        )
        mock_cursor.fetchone.assert_called_once()
        mock_cursor.close.assert_called_once()

        # Verify result
        assert result == {"id": 1, "name": "test"}

        # Verify logging
        assert "Executing single query" in caplog.text
        assert "Query returned: 1 row" in caplog.text

    def test_execute_one_no_result(self, mock_db, caplog):
        """Test single row query with no result."""
        db, mock_connection = mock_db
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_connection.cursor.return_value = mock_cursor

        with patch.object(db, "get_connection") as mock_get_conn:
            mock_get_conn.return_value.__enter__.return_value = mock_connection

            with caplog.at_level(logging.DEBUG):
                result = db.execute_one("SELECT * FROM test WHERE id = %s", (999,))

        # Verify result is None
        assert result is None

        # Verify logging
        assert "Query returned: no rows" in caplog.text

    def test_execute_modify_insert(self, mock_db, caplog):
        """Test INSERT query execution."""
        db, mock_connection = mock_db
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 1
        mock_cursor.lastrowid = 123
        mock_connection.cursor.return_value = mock_cursor

        with patch.object(db, "get_connection") as mock_get_conn:
            mock_get_conn.return_value.__enter__.return_value = mock_connection

            with caplog.at_level(logging.DEBUG):
                result = db.execute_modify(
                    "INSERT INTO test (name) VALUES (%s)", ("test_name",)
                )

        # Verify query execution
        mock_connection.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once_with(
            "INSERT INTO test (name) VALUES (%s)", ("test_name",)
        )
        mock_connection.commit.assert_called_once()
        mock_cursor.close.assert_called_once()

        # Verify result (should return lastrowid for INSERT)
        assert result == 123

        # Verify logging
        assert "Executing modify query" in caplog.text
        assert "Query affected 1 rows, returned 123" in caplog.text

    def test_execute_modify_update(self, mock_db, caplog):
        """Test UPDATE query execution."""
        db, mock_connection = mock_db
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 2
        mock_cursor.lastrowid = 0
        mock_connection.cursor.return_value = mock_cursor

        with patch.object(db, "get_connection") as mock_get_conn:
            mock_get_conn.return_value.__enter__.return_value = mock_connection

            with caplog.at_level(logging.DEBUG):
                result = db.execute_modify(
                    "UPDATE test SET name = %s WHERE active = %s", ("new_name", True)
                )

        # Verify result (should return rowcount for UPDATE)
        assert result == 2

        # Verify logging
        assert "Query affected 2 rows, returned 2" in caplog.text

    def test_execute_modify_delete(self, mock_db, caplog):
        """Test DELETE query execution."""
        db, mock_connection = mock_db
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 1
        mock_cursor.lastrowid = 0
        mock_connection.cursor.return_value = mock_cursor

        with patch.object(db, "get_connection") as mock_get_conn:
            mock_get_conn.return_value.__enter__.return_value = mock_connection

            with caplog.at_level(logging.DEBUG):
                result = db.execute_modify("DELETE FROM test WHERE id = %s", (1,))

        # Verify result (should return rowcount for DELETE)
        assert result == 1

    def test_execute_transaction_success(self, mock_db, caplog):
        """Test successful transaction execution."""
        db, mock_connection = mock_db
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor

        queries = [
            ("INSERT INTO test (name) VALUES (%s)", ("test1",)),
            ("UPDATE test SET active = %s WHERE name = %s", (True, "test1")),
            ("DELETE FROM test WHERE id = %s", (999,)),
        ]

        with patch.object(db, "get_connection") as mock_get_conn:
            mock_get_conn.return_value.__enter__.return_value = mock_connection

            with caplog.at_level(logging.DEBUG):
                result = db.execute_transaction(queries)

        # Verify transaction handling
        mock_connection.start_transaction.assert_called_once()
        mock_connection.commit.assert_called_once()
        mock_cursor.close.assert_called_once()

        # Verify all queries were executed
        assert mock_cursor.execute.call_count == 3
        expected_calls = [
            (("INSERT INTO test (name) VALUES (%s)", ("test1",)),),
            (("UPDATE test SET active = %s WHERE name = %s", (True, "test1")),),
            (("DELETE FROM test WHERE id = %s", (999,)),),
        ]
        actual_calls = mock_cursor.execute.call_args_list
        assert actual_calls == expected_calls

        # Verify result
        assert result is True

        # Verify logging
        assert "Executing transaction with 3 queries" in caplog.text
        assert "Transaction query 1:" in caplog.text
        assert "Transaction query 2:" in caplog.text
        assert "Transaction query 3:" in caplog.text
        assert "Transaction committed successfully" in caplog.text

    def test_execute_transaction_rollback(self, mock_db, caplog):
        """Test transaction rollback on error."""
        db, mock_connection = mock_db
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = [None, Error("Query failed"), None]
        mock_connection.cursor.return_value = mock_cursor

        queries = [
            ("INSERT INTO test (name) VALUES (%s)", ("test1",)),
            ("INVALID QUERY", ()),
            ("DELETE FROM test WHERE id = %s", (999,)),
        ]

        with patch.object(db, "get_connection") as mock_get_conn:
            mock_get_conn.return_value.__enter__.return_value = mock_connection

            with pytest.raises(Error):
                with caplog.at_level(logging.DEBUG):
                    db.execute_transaction(queries)

        # Verify rollback was called
        mock_connection.rollback.assert_called_once()
        mock_cursor.close.assert_called_once()

        # Verify logging
        assert "Transaction failed and rolled back" in caplog.text

    def test_test_connection_success(self, mock_db):
        """Test successful connection test."""
        db, mock_connection = mock_db
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (1,)
        mock_connection.cursor.return_value = mock_cursor

        with patch.object(db, "get_connection") as mock_get_conn:
            mock_get_conn.return_value.__enter__.return_value = mock_connection

            result = db.test_connection()

        # Verify test query
        mock_cursor.execute.assert_called_once_with("SELECT 1")
        mock_cursor.fetchone.assert_called_once()
        mock_cursor.close.assert_called_once()

        assert result is True

    def test_test_connection_failure(self, mock_db, caplog):
        """Test connection test failure."""
        db, mock_connection = mock_db
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = Error("Connection test failed")
        mock_connection.cursor.return_value = mock_cursor

        with patch.object(db, "get_connection") as mock_get_conn:
            mock_get_conn.return_value.__enter__.return_value = mock_connection

            with caplog.at_level(logging.ERROR):
                result = db.test_connection()

        assert result is False
        assert "Database connection test failed" in caplog.text


class TestDatabaseIntegration:
    """Integration tests for database operations."""

    def test_logging_levels(self, caplog):
        """Test that database operations log at appropriate levels."""
        with patch("mysql.connector.pooling.MySQLConnectionPool") as mock_pool:
            mock_connection = MagicMock()
            mock_connection.is_connected.return_value = True
            mock_cursor = MagicMock()
            mock_cursor.fetchall.return_value = []
            mock_connection.cursor.return_value = mock_cursor
            mock_pool_instance = MagicMock()
            mock_pool_instance.get_connection.return_value = mock_connection
            mock_pool.return_value = mock_pool_instance

            db = Database()

            with patch.object(db, "get_connection") as mock_get_conn:
                mock_get_conn.return_value.__enter__.return_value = mock_connection

                # Test different log levels
                with caplog.at_level(logging.DEBUG):
                    db.execute_query("SELECT * FROM test")

                with caplog.at_level(logging.INFO):
                    db.execute_query("SELECT * FROM test")

                with caplog.at_level(logging.ERROR):
                    db.execute_query("SELECT * FROM test")

        # DEBUG level should show detailed query logs
        debug_logs = [
            record for record in caplog.records if record.levelno == logging.DEBUG
        ]
        assert len(debug_logs) > 0

        # Query details should be in debug logs
        debug_messages = [record.message for record in debug_logs]
        assert any("Executing query:" in msg for msg in debug_messages)

    def test_connection_pool_exhaustion(self):
        """Test behavior when connection pool is exhausted."""
        with patch("mysql.connector.pooling.MySQLConnectionPool") as mock_pool:
            mock_pool_instance = MagicMock()
            mock_pool_instance.get_connection.side_effect = Error("Pool exhausted")
            mock_pool.return_value = mock_pool_instance

            db = Database()

            with pytest.raises(Error):
                with db.get_connection():
                    pass

    def test_concurrent_connections(self):
        """Test handling of concurrent database connections."""
        with patch("mysql.connector.pooling.MySQLConnectionPool") as mock_pool:
            mock_connections = [MagicMock() for _ in range(3)]
            for conn in mock_connections:
                conn.is_connected.return_value = True

            mock_pool_instance = MagicMock()
            mock_pool_instance.get_connection.side_effect = mock_connections
            mock_pool.return_value = mock_pool_instance

            db = Database()

            # Simulate multiple concurrent operations
            contexts = []
            for i in range(3):
                ctx = db.get_connection()
                contexts.append(ctx)
                conn = ctx.__enter__()
                assert conn == mock_connections[i]

            # Clean up contexts
            for ctx in contexts:
                ctx.__exit__(None, None, None)

            # Verify all connections were closed
            for conn in mock_connections:
                conn.close.assert_called_once()


class TestDatabaseErrorHandling:
    """Test database error handling and recovery."""

    def test_connection_recovery_after_failure(self):
        """Test that database can recover after connection failure."""
        with patch("mysql.connector.pooling.MySQLConnectionPool") as mock_pool:
            mock_connection = MagicMock()
            mock_connection.is_connected.return_value = True
            mock_cursor = MagicMock()
            mock_connection.cursor.return_value = mock_cursor

            # First call fails, second succeeds
            mock_pool_instance = MagicMock()
            mock_pool_instance.get_connection.side_effect = [
                Error("Connection failed"),
                mock_connection,
            ]
            mock_pool.return_value = mock_pool_instance

            db = Database()

            # First attempt should fail
            with pytest.raises(Error):
                with db.get_connection():
                    pass

            # Second attempt should succeed
            with db.get_connection() as conn:
                assert conn == mock_connection

    def test_query_parameter_sanitization(self, mock_db):
        """Test that query parameters are properly handled."""
        db, mock_connection = mock_db
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_connection.cursor.return_value = mock_cursor

        # Test with various parameter types
        test_params = [
            None,
            (),
            ("string_param",),
            (123, "mixed", True),
            ("with_special_chars_!@#$%",),
        ]

        with patch.object(db, "get_connection") as mock_get_conn:
            mock_get_conn.return_value.__enter__.return_value = mock_connection

            for params in test_params:
                db.execute_query("SELECT * FROM test WHERE id = %s", params)

                # Verify parameters were passed correctly to cursor
                last_call = mock_cursor.execute.call_args
                assert last_call[0][1] == params

    def test_long_query_handling(self, mock_db, caplog):
        """Test handling of long queries in logging."""
        db, mock_connection = mock_db
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_connection.cursor.return_value = mock_cursor

        # Create a very long query
        long_query = "SELECT * FROM test WHERE " + " AND ".join(
            [f"col{i} = %s" for i in range(100)]
        )
        long_params = tuple(range(100))

        with patch.object(db, "get_connection") as mock_get_conn:
            mock_get_conn.return_value.__enter__.return_value = mock_connection

            with caplog.at_level(logging.DEBUG):
                db.execute_query(long_query, long_params)

        # Verify query was logged (even if truncated)
        assert "Executing query:" in caplog.text
        assert "Query returned 0 rows" in caplog.text
