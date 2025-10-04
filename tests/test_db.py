"""
Unit tests for the real Database class in app.db, using mock MySQL connections/cursors.
"""

from unittest.mock import patch, MagicMock
from app.db import Database


@patch("app.db.MySQLConnectionPool")
def test_execute_query_returns_results(mock_pool):
    # Setup mock connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_pool.return_value.get_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [{"id": 1, "name": "Alice"}]

    db = Database()
    result = db.execute_query("SELECT * FROM users")
    assert result == [{"id": 1, "name": "Alice"}]
    mock_cursor.execute.assert_called_once_with("SELECT * FROM users", None)
    mock_cursor.close.assert_called_once()


@patch("app.db.MySQLConnectionPool")
def test_execute_one_returns_single_result(mock_pool):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_pool.return_value.get_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = {"id": 2, "name": "Bob"}

    db = Database()
    result = db.execute_one("SELECT * FROM users WHERE id=%s", (2,))
    assert result == {"id": 2, "name": "Bob"}
    mock_cursor.execute.assert_called_once_with("SELECT * FROM users WHERE id=%s", (2,))
    mock_cursor.close.assert_called_once()


@patch("app.db.MySQLConnectionPool")
def test_execute_modify_returns_affected_rows(mock_pool):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_pool.return_value.get_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.rowcount = 3
    mock_cursor.lastrowid = 42

    db = Database()
    # Test UPDATE (not insert)
    result = db.execute_modify("UPDATE users SET name=%s WHERE id=%s", ("Charlie", 3))
    assert result == 3
    mock_cursor.execute.assert_called_once_with(
        "UPDATE users SET name=%s WHERE id=%s", ("Charlie", 3)
    )
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()


@patch("app.db.MySQLConnectionPool")
def test_execute_modify_returns_lastrowid_for_insert(mock_pool):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_pool.return_value.get_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.rowcount = 1
    mock_cursor.lastrowid = 99

    db = Database()
    # Test INSERT
    result = db.execute_modify("INSERT INTO users (name) VALUES (%s)", ("Dana",))
    assert result == 99
    mock_cursor.execute.assert_called_once_with(
        "INSERT INTO users (name) VALUES (%s)", ("Dana",)
    )
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()


@patch("app.db.MySQLConnectionPool")
def test_test_connection_success(mock_pool):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_pool.return_value.get_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = (1,)

    db = Database()
    assert db.test_connection() is True
    mock_cursor.execute.assert_called_once_with("SELECT 1")
    mock_cursor.close.assert_called_once()


@patch("app.db.MySQLConnectionPool")
def test_execute_transaction_success(mock_pool):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_pool.return_value.get_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    db = Database()
    queries = [
        ("UPDATE users SET name=%s WHERE id=%s", ("Eve", 4)),
        ("DELETE FROM users WHERE id=%s", (5,)),
    ]
    result = db.execute_transaction(queries)
    assert result is True
    assert mock_cursor.execute.call_count == 2
    mock_conn.start_transaction.assert_called_once()
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
