"""
Tests for admin API endpoints.
"""

import json
from unittest.mock import patch


def test_get_stats_success(client, mock_db, auth_headers):
    """Test getting system statistics by admin."""
    mock_db.reset_mock()
    # Mock database responses for statistics
    mock_db.execute_one.side_effect = [
        {"is_admin": True},  # Admin check
        {"count": 10},  # Total users
        {"count": 5},  # Active users
        {"count": 50},  # Total files
        {"count": 3},  # Total teams
        {"count": 7},  # Recent activity
    ]

    with patch("app.services.auth_service.AuthService.verify_jwt") as mock_verify:
        mock_verify.return_value = {
            "user_id": 1,
            "email": "admin@example.com",
            "is_admin": True,
        }

        response = client.get("/admin/stats", headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        # The backend returns keys: totalUsers, activeUsers, totalFiles, totalTeams, recentActivity
        assert data["totalUsers"] == 10
        assert data["activeUsers"] == 5
        assert data["totalFiles"] == 50
        assert data["totalTeams"] == 3
        assert data["recentActivity"] == 7


def test_get_stats_unauthorized(client):
    """Test getting system statistics without authentication."""
    response = client.get("/admin/stats")
    assert response.status_code == 401
    data = json.loads(response.data)
    assert "error" in data
    assert "authorization" in data["error"].lower()


def test_list_activity_success(client, mock_db, auth_headers):
    """Test listing activity logs by admin."""
    mock_db.reset_mock()
    mock_db.execute_one.return_value = {"is_admin": True}
    mock_db.execute_query.return_value = [
        {
            "id": 1,
            "user_id": 1,
            "action": "login",
            "created_at": "2025-10-01T10:00:00",
        },
        {
            "id": 2,
            "user_id": 2,
            "action": "upload",
            "created_at": "2025-10-02T10:00:00",
        },
    ]

    with patch("app.services.auth_service.AuthService.verify_jwt") as mock_verify:
        mock_verify.return_value = {
            "user_id": 1,
            "email": "admin@example.com",
            "is_admin": True,
        }

        response = client.get("/admin/activity", headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "activities" in data
        assert isinstance(data["activities"], list)
        assert len(data["activities"]) == 2


def test_list_activity_unauthorized(client):
    """Test listing activity logs without authentication."""
    response = client.get("/admin/activity")
    assert response.status_code == 401
    data = json.loads(response.data)
    assert "error" in data
    assert "authorization" in data["error"].lower()


"""Test case for admin API endpoints."""


def test_list_users_success(client, mock_db, auth_headers):
    """Test successful user listing by admin."""
    mock_db.reset_mock()
    # Mock database response for user listing
    mock_db.execute_one.return_value = {"is_admin": True}
    mock_db.execute_query.return_value = [
        {
            "id": 1,
            "email": "admin@example.com",
            "name": "Admin User",
            "created_at": "2025-10-01T10:00:00",
            "updated_at": "2025-10-01T10:00:00",
            "is_admin": True,
        },
        {
            "id": 2,
            "email": "user@example.com",
            "name": "Regular User",
            "created_at": "2025-10-02T10:00:00",
            "updated_at": "2025-10-02T10:00:00",
            "is_admin": False,
        },
    ]

    # Patch only AuthService.verify_jwt to ensure 'is_admin' is present
    with patch("app.services.auth_service.AuthService.verify_jwt") as mock_verify:
        mock_verify.return_value = {
            "user_id": 1,
            "email": "admin@example.com",
            "is_admin": True,
        }

        response = client.get("/admin/users", headers=auth_headers)

        # Assert response
        assert response.status_code == 200
        data = json.loads(response.data)
        users = data["users"]
        assert isinstance(users, list)
        assert len(users) == 2
        assert users[0]["email"] == "admin@example.com"
        assert users[1]["email"] == "user@example.com"

        # Verify database was called correctly
        mock_db.execute_query.assert_called_once()


def test_list_users_unauthorized(client):
    """Test user listing without authentication."""
    response = client.get("/admin/users")

    assert response.status_code == 401
    data = json.loads(response.data)
    assert "error" in data
    assert "authorization" in data["error"].lower()
