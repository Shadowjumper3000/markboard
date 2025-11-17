"""
Tests for admin_service.py
"""

from app.services.admin_service import AdminService


def test_get_all_users(mock_db):
    """Test retrieving all users."""
    mock_db.reset_mock()
    mock_db.execute_query.return_value = [{"id": 1, "email": "admin@example.com"}]
    users = AdminService.get_all_users()
    assert isinstance(users, list)
    assert users[0]["email"] == "admin@example.com"


def test_get_system_stats(mock_db):
    """Test retrieving system statistics."""
    mock_db.reset_mock()
    mock_db.execute_one.side_effect = [
        {"count": 10},  # total users
        {"count": 5},  # active users
        {"count": 50},  # total files
        {"count": 3},  # total teams
        {"count": 7},  # recent activity
    ]
    stats = AdminService.get_system_stats()
    assert "totalUsers" in stats
    assert "totalTeams" in stats
