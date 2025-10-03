"""
Tests for teams API endpoints.
"""

import json
from unittest.mock import patch


def test_list_teams_success(client, mock_db, auth_headers):
    """Test successful team listing."""
    mock_db.reset_mock()
    mock_db.execute_query.return_value = [
        {
            "id": 1,
            "name": "Engineering",
            "description": "Engineering team",
            "owner_id": 1,
            "created_at": "2025-10-03T10:00:00",
            "updated_at": "2025-10-03T10:00:00",
            "file_count": 0,
            "member_count": 1,
            "role": "admin",
        }
    ]
    # Mock JWT verification
    with patch("app.services.auth_service.AuthService.verify_jwt") as mock_verify:
        mock_verify.return_value = {"user_id": 1, "email": "test@example.com"}
    team_data = {"name": "New Team", "description": ""}
    with (
        patch("app.services.auth_service.AuthService.verify_jwt") as mock_verify,
        patch("app.services.team_service.TeamService.create_team") as mock_create_team,
        patch(
            "app.services.team_service.TeamService.get_team_details"
        ) as mock_get_team_details,
    ):
        mock_verify.return_value = {"user_id": 1, "email": "test@example.com"}
        mock_create_team.return_value = (True, "Team created", 1)
        # Patch get_team_details to return a valid team dict
        mock_get_team_details.return_value = {
            "id": 1,
            "name": "New Team",
            "description": "",
            "owner_id": 1,
            "created_at": "2025-10-03T10:00:00",
            "updated_at": "2025-10-03T10:00:00",
            "file_count": 0,
            "member_count": 1,
            "role": "admin",
        }
        response = client.post(
            "/teams",
            data=json.dumps(team_data),
            content_type="application/json",
            headers=auth_headers,
        )
        # Assert response
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["name"] == "New Team"
        assert data["id"] == 1
    # Mock JWT verification
    with patch("app.services.auth_service.AuthService.verify_jwt") as mock_verify:
        mock_verify.return_value = {"user_id": 1, "email": "test@example.com"}
        # Patch the DB response for team details to include 'role'
        mock_db.execute_one.return_value = {
            "id": 1,
            "name": "Engineering",
            "description": "Engineering team",
            "owner_id": 1,
            "created_at": "2025-10-03T10:00:00",
            "updated_at": "2025-10-03T10:00:00",
            "file_count": 0,
            "member_count": 1,
            "role": "admin",
        }
        response = client.get("/teams/1", headers=auth_headers)
        # Assert response
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["name"] == "Engineering"
        assert data["id"] == 1
        # Verify database was called correctly
        assert mock_db.execute_one.call_count == 2
        calls = mock_db.execute_one.call_args_list
        # The last call should be the team details query
        assert "SELECT t.id, t.name, t.description, t.owner_id" in calls[-1][0][0]


def test_get_nonexistent_team(client, mock_db, auth_headers):
    """Test getting a team that doesn't exist."""
    mock_db.reset_mock()
    # Mock database response for no team found
    mock_db.execute_one.return_value = None
    # Mock JWT verification
    with patch("app.services.auth_service.AuthService.verify_jwt") as mock_verify:
        mock_verify.return_value = {"user_id": 1, "email": "test@example.com"}
        response = client.get("/teams/999", headers=auth_headers)
        # Assert response
        assert response.status_code == 404
        data = json.loads(response.data)
        assert "error" in data
        assert "not found" in data["error"].lower()


def test_create_team_success(client, mock_db, auth_headers):
    """Test successful team creation."""
    mock_db.reset_mock()
    # Mock database response for team creation
    team_data = {"name": "New Team", "description": "A new team for testing."}
    with (
        patch("app.services.auth_service.AuthService.verify_jwt") as mock_verify,
        patch(
            "app.services.team_service.TeamService.get_team_details"
        ) as mock_get_team_details,
    ):
        mock_verify.return_value = {"user_id": 1, "email": "test@example.com"}
        # Mock admin check to return admin user
        mock_db.execute_one.side_effect = [
            {"is_admin": True},  # Admin check
            {  # Team creation (include all expected fields)
                "id": 1,
                "name": "New Team",
                "description": "",
                "owner_id": 1,
                "created_at": "2025-10-03T10:00:00",
                "updated_at": "2025-10-03T10:00:00",
                "file_count": 0,
                "member_count": 1,
                "role": "admin",
            },
        ]
        # Patch get_team_details to return a valid team dict
        mock_get_team_details.return_value = {
            "id": 1,
            "name": "New Team",
            "description": "",
            "owner_id": 1,
            "created_at": "2025-10-03T10:00:00",
            "updated_at": "2025-10-03T10:00:00",
            "file_count": 0,
            "member_count": 1,
            "role": "admin",
        }
        response = client.post(
            "/teams",
            data=json.dumps(team_data),
            content_type="application/json",
            headers=auth_headers,
        )
        # Assert response
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["name"] == "New Team"
        assert data["id"] == 1
        # Verify database was called correctly
        assert mock_db.execute_one.call_count >= 2


def test_create_team_missing_fields(client, mock_db, auth_headers):
    """Test team creation with missing required fields."""
    mock_db.reset_mock()
    with patch("app.services.auth_service.AuthService.verify_jwt") as mock_verify:
        mock_verify.return_value = {"user_id": 1, "email": "test@example.com"}
        mock_db.execute_one.return_value = {"is_admin": True}  # Admin check
        # Missing name field
        response = client.post(
            "/teams",
            data=json.dumps({}),
            content_type="application/json",
            headers=auth_headers,
        )
        # Assert response
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
        assert "name" in data["error"].lower()


def test_create_team_not_admin(client, mock_db, auth_headers):
    """Test team creation without admin privileges."""
    mock_db.reset_mock()
    team_data = {"name": "New Team"}
    with patch("app.services.auth_service.AuthService.verify_jwt") as mock_verify:
        mock_verify.return_value = {"user_id": 1, "email": "test@example.com"}
        mock_db.execute_one.return_value = {"is_admin": False}  # Non-admin user
        response = client.post(
            "/teams",
            data=json.dumps(team_data),
            content_type="application/json",
            headers=auth_headers,
        )
        # Assert response
        assert response.status_code == 403
        data = json.loads(response.data)
        assert "error" in data
        assert "permission" in data["error"].lower() or "admin" in data["error"].lower()


def test_join_team_success(client, mock_db, auth_headers):
    """Test successfully joining a team."""
    mock_db.reset_mock()
    # Mock JWT verification

    with patch("app.services.auth_service.AuthService.verify_jwt") as mock_verify:
        mock_verify.return_value = {"user_id": 1, "email": "test@example.com"}

        # Mock database response for successful join
        mock_db.execute_one.return_value = {
            "id": 1,
            "name": "Test Team",
            "created_at": "2025-10-03T10:00:00",
            "updated_at": "2025-10-03T10:00:00",
        }

        response = client.post("/teams/1/join", headers=auth_headers)

        # Assert response
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "message" in data
        assert "success" in data["message"].lower()

        # Verify database was called correctly
        mock_db.execute_one.assert_called()


def test_delete_team_success(client, mock_db, auth_headers):
    """Test successful team deletion."""
    mock_db.reset_mock()
    # Mock JWT verification and admin check

    with patch("app.services.auth_service.AuthService.verify_jwt") as mock_verify:
        mock_verify.return_value = {"user_id": 1, "email": "test@example.com"}
        # Mock database responses
        mock_db.execute_one.side_effect = [
            {"is_admin": True},  # Admin check
            {  # Team lookup
                "id": 1,
                "name": "Test Team",
                "created_at": "2025-10-03T10:00:00",
                "updated_at": "2025-10-03T10:00:00",
            },
        ]

        response = client.delete("/teams/1", headers=auth_headers)

        # Assert response
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "success" in data["message"].lower()

        # Verify calls
        assert mock_db.execute_one.call_count >= 2
        mock_db.execute_modify.assert_called_once()


def test_kick_user_from_team_success(client, mock_db, auth_headers):
    """Test successfully kicking a user from a team."""
    mock_db.reset_mock()
    # Mock JWT verification

    with patch("app.services.auth_service.AuthService.verify_jwt") as mock_verify:
        mock_verify.return_value = {"user_id": 1, "email": "test@example.com"}

        # Mock database responses
        mock_db.execute_one.return_value = {
            "id": 1,
            "name": "Test Team",
            "created_at": "2025-10-03T10:00:00",
            "updated_at": "2025-10-03T10:00:00",
        }

        kick_data = {"user_id": 2}

        response = client.post(
            "/teams/1/kick",
            data=json.dumps(kick_data),
            content_type="application/json",
            headers=auth_headers,
        )

        # Assert response
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "message" in data
        assert "success" in data["message"].lower()

        # Verify database calls
        mock_db.execute_one.assert_called()


def test_leave_team_success(client, mock_db, auth_headers):
    """Test successfully leaving a team."""
    mock_db.reset_mock()
    # Mock JWT verification

    with patch("app.services.auth_service.AuthService.verify_jwt") as mock_verify:
        mock_verify.return_value = {"user_id": 1, "email": "test@example.com"}

        # Mock database responses
        mock_db.execute_one.return_value = {
            "id": 1,
            "name": "Test Team",
            "created_at": "2025-10-03T10:00:00",
            "updated_at": "2025-10-03T10:00:00",
        }

        response = client.post("/teams/1/leave", headers=auth_headers)

        # Assert response
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "message" in data
        assert "success" in data["message"].lower()

        # Verify database calls
        mock_db.execute_one.assert_called()


def test_list_team_members_success(client, mock_db, auth_headers):
    """Test listing team members."""
    mock_db.reset_mock()
    # Mock JWT verification

    with patch("app.services.auth_service.AuthService.verify_jwt") as mock_verify:
        mock_verify.return_value = {"user_id": 1, "email": "test@example.com"}

        # Mock database response for team members
        mock_db.execute_query.return_value = [
            {
                "user_id": 1,
                "email": "test@example.com",
                "created_at": "2025-10-03T10:00:00",
            },
            {
                "user_id": 2,
                "email": "member@example.com",
                "created_at": "2025-10-03T12:00:00",
            },
        ]

        response = client.get("/teams/1/users", headers=auth_headers)

        # Assert response
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "users" in data
        assert isinstance(data["users"], list)
        assert len(data["users"]) == 2
        assert data["users"][0]["email"] == "test@example.com"
        assert data["users"][1]["email"] == "member@example.com"

        # Verify database calls
        mock_db.execute_query.assert_called_once()
