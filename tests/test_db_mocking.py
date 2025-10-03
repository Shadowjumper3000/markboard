"""
Tests for database mocking setup.
"""

from app.db import get_db


def test_db_mocking_works(mock_db):
    """Test that database mocking is working properly."""
    mock_db.reset_mock()
    # Get the database instance
    db = get_db()

    # Verify that it's the same as our mock
    assert db is mock_db

    # Test connection method
    assert db.test_connection() is True

    # Test execute_query
    result = db.execute_query("SELECT * FROM users")
    assert isinstance(result, list)
    assert len(result) == 0  # Should be empty by default

    # Test execute_one
    result = db.execute_one("SELECT NOW() as now")
    assert isinstance(result, dict)
    assert "now" in result
    assert result["now"] == "2025-10-03T10:00:00"

    # Test execute_modify
    result = db.execute_modify(
        "UPDATE users SET last_login = %s WHERE id = %s", ("2025-10-03", 1)
    )
    assert result == 1  # Should return 1 row affected by default

    # Test customizing mock responses
    mock_db.execute_one.return_value = {"custom": "response"}
    result = db.execute_one("ANY QUERY")
    assert result == {"custom": "response"}

    # Test resetting to default behavior
    mock_db.execute_one.side_effect = None
    mock_db.execute_one.return_value = None
    result = db.execute_one("ANY QUERY")
    assert result is None
