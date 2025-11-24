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
            "/api/teams",
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
        response = client.get("/api/teams/1", headers=auth_headers)
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
        response = client.get("/api/teams/999", headers=auth_headers)
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
        # Mock DB: first call (check for existing team) returns None
        mock_db.execute_one.side_effect = [
            None,  # No existing team with this name
        ]
        mock_db.execute_modify.return_value = 1
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
            "/api/teams",
            data=json.dumps(team_data),
            content_type="application/json",
            headers=auth_headers,
        )
        # Assert response
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["name"] == "New Team"
        assert data["id"] == 1
    # Verify database was called correctly (team name check only)
    assert mock_db.execute_one.call_count == 1


def test_create_team_missing_fields(client, mock_db, auth_headers):
    """Test team creation with missing required fields."""
    mock_db.reset_mock()
    with patch("app.services.auth_service.AuthService.verify_jwt") as mock_verify:
        mock_verify.return_value = {"user_id": 1, "email": "test@example.com"}
        # Empty body
        response = client.post(
            "/api/teams",
            data=json.dumps({}),
            content_type="application/json",
            headers=auth_headers,
        )
        # Assert response for empty body
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
        assert "request body" in data["error"].lower()


def test_create_team_missing_name_field(client, mock_db, auth_headers):
    """Test team creation with missing 'name' field in non-empty body."""
    mock_db.reset_mock()
    with patch("app.services.auth_service.AuthService.verify_jwt") as mock_verify:
        mock_verify.return_value = {"user_id": 1, "email": "test@example.com"}
        # Body with description but no name
        response = client.post(
            "/api/teams",
            data=json.dumps({"description": "foo"}),
            content_type="application/json",
            headers=auth_headers,
        )
        # Assert response for missing name
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
        assert "name" in data["error"].lower()


def test_join_team_success(client, mock_db, auth_headers):
    """Test successfully joining a team."""
    mock_db.reset_mock()
    # Mock JWT verification

    with patch("app.services.auth_service.AuthService.verify_jwt") as mock_verify:
        mock_verify.return_value = {"user_id": 1, "email": "test@example.com"}

        # First call: team exists, second call: user not a member
        mock_db.execute_one.side_effect = [
            {
                "id": 1,
                "name": "Test Team",
                "created_at": "2025-10-03T10:00:00",
                "updated_at": "2025-10-03T10:00:00",
            },
            None,  # Not already a member
        ]

        response = client.post("/api/teams/1/join", headers=auth_headers)

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
        # Mock database responses in correct order:
        # 1. Team lookup (must include owner_id)
        # 2. File count for team
        mock_db.execute_one.side_effect = [
            {"name": "Test Team", "owner_id": 1},  # Team lookup
            {"count": 0},  # No files for team
        ]

        response = client.delete("/api/teams/1", headers=auth_headers)

        # Assert response
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "success" in data["message"].lower()

        # Verify calls
        assert mock_db.execute_one.call_count >= 2
        mock_db.execute_modify.assert_called()


def test_kick_user_from_team_success(client, mock_db, auth_headers):
    """Test successfully kicking a user from a team."""
    mock_db.reset_mock()
    # Mock JWT verification

    with patch("app.services.auth_service.AuthService.verify_jwt") as mock_verify:
        mock_verify.return_value = {"user_id": 1, "email": "test@example.com"}

        # Mock DB calls in correct order:
        # 1. Kicker is admin
        # 2. Target is member
        # 3. Team info
        # 4. Target user email
        mock_db.execute_one.side_effect = [
            {"role": "admin"},
            {"role": "member"},
            {"name": "Test Team", "owner_id": 1},
            {"email": "target@example.com"},
        ]

        kick_data = {"user_id": 2}

        response = client.post(
            "/api/teams/1/kick",
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

        # Mock DB calls in correct order:
        # 1. User is a member
        # 2. Team info (owner is not the user)
        mock_db.execute_one.side_effect = [
            {"role": "member"},
            {"name": "Test Team", "owner_id": 99},
        ]

        response = client.post("/api/teams/1/leave", headers=auth_headers)

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

        response = client.get("/api/teams/1/users", headers=auth_headers)

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


def test_join_nonexistent_team(client, mock_db, auth_headers):
    """Test joining a team that does not exist."""
    mock_db.reset_mock()
    with patch("app.services.auth_service.AuthService.verify_jwt") as mock_verify:
        mock_verify.return_value = {"user_id": 1, "email": "test@example.com"}
        # Team does not exist
        mock_db.execute_one.side_effect = [None]
        response = client.post("/api/teams/999/join", headers=auth_headers)
        assert response.status_code == 404
        data = json.loads(response.data)
        assert "error" in data
        assert "not found" in data["error"].lower() or "exist" in data["error"].lower()


def test_join_team_already_member(client, mock_db, auth_headers):
    """Test joining a team the user is already a member of."""
    mock_db.reset_mock()
    with patch("app.services.auth_service.AuthService.verify_jwt") as mock_verify:
        mock_verify.return_value = {"user_id": 1, "email": "test@example.com"}
        # Team exists, user is already a member
        mock_db.execute_one.side_effect = [
            {"id": 1, "name": "Test Team"},
            {"user_id": 1},
        ]
        response = client.post("/api/teams/1/join", headers=auth_headers)
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
        assert "already" in data["error"].lower()


def test_leave_team_not_member(client, mock_db, auth_headers):
    """Test leaving a team the user is not a member of."""
    mock_db.reset_mock()
    with patch("app.services.auth_service.AuthService.verify_jwt") as mock_verify:
        mock_verify.return_value = {"user_id": 1, "email": "test@example.com"}
        # User is not a member
        mock_db.execute_one.side_effect = [None]
        response = client.post("/api/teams/1/leave", headers=auth_headers)
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
        assert (
            "not a member" in data["error"].lower()
            or "not part" in data["error"].lower()
        )


def test_kick_user_not_member(client, mock_db, auth_headers):
    """Test kicking a user who is not a member of the team."""
    mock_db.reset_mock()
    with patch("app.services.auth_service.AuthService.verify_jwt") as mock_verify:
        mock_verify.return_value = {"user_id": 1, "email": "test@example.com"}
        # Kicker is admin, target is not a member
        mock_db.execute_one.side_effect = [
            {"role": "admin"},
            None,
        ]
        kick_data = {"user_id": 2}
        response = client.post(
            "/api/teams/1/kick",
            data=json.dumps(kick_data),
            content_type="application/json",
            headers=auth_headers,
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
        assert (
            "not a member" in data["error"].lower()
            or "not part" in data["error"].lower()
        )


def test_kick_user_not_admin(client, mock_db, auth_headers):
    """Test kicking a user as a non-admin."""
    mock_db.reset_mock()
    with patch("app.services.auth_service.AuthService.verify_jwt") as mock_verify:
        mock_verify.return_value = {"user_id": 1, "email": "test@example.com"}
        # Kicker is not admin
        mock_db.execute_one.side_effect = [
            {"role": "member"},
        ]
        kick_data = {"user_id": 2}
        response = client.post(
            "/api/teams/1/kick",
            data=json.dumps(kick_data),
            content_type="application/json",
            headers=auth_headers,
        )
        assert response.status_code == 403 or response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
        assert "permission" in data["error"].lower() or "admin" in data["error"].lower()


def test_disband_team_not_owner(client, mock_db, auth_headers):
    """Test disbanding a team as a non-owner."""
    mock_db.reset_mock()
    with patch("app.services.auth_service.AuthService.verify_jwt") as mock_verify:
        mock_verify.return_value = {"user_id": 2, "email": "test@example.com"}
        # Team exists, but user is not owner
        mock_db.execute_one.side_effect = [
            {"name": "Test Team", "owner_id": 1},
        ]
        response = client.delete("/api/teams/1", headers=auth_headers)
        assert response.status_code == 400 or response.status_code == 403
        data = json.loads(response.data)
        assert "error" in data
        assert "owner" in data["error"].lower() or "permission" in data["error"].lower()


def test_create_team_name_too_long(client, mock_db, auth_headers):
    """Test creating a team with a name that exceeds the allowed length."""
    mock_db.reset_mock()
    long_name = "A" * 101
    with patch("app.services.auth_service.AuthService.verify_jwt") as mock_verify:
        mock_verify.return_value = {"user_id": 1, "email": "test@example.com"}
        team_data = {"name": long_name, "description": "desc"}
        response = client.post(
            "/api/teams",
            data=json.dumps(team_data),
            content_type="application/json",
            headers=auth_headers,
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
        assert "100 characters" in data["error"].lower()


def test_create_team_description_too_long(client, mock_db, auth_headers):
    """Test creating a team with a description that exceeds the allowed length."""
    mock_db.reset_mock()
    long_desc = "D" * 501
    with patch("app.services.auth_service.AuthService.verify_jwt") as mock_verify:
        mock_verify.return_value = {"user_id": 1, "email": "test@example.com"}
        team_data = {"name": "Valid Name", "description": long_desc}
        response = client.post(
            "/api/teams",
            data=json.dumps(team_data),
            content_type="application/json",
            headers=auth_headers,
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
        assert "500 characters" in data["error"].lower()


def test_list_teams_empty(client, mock_db, auth_headers):
    """Test getting list of teams when user is not a member of any team."""
    mock_db.reset_mock()
    with patch("app.services.auth_service.AuthService.verify_jwt") as mock_verify:
        mock_verify.return_value = {"user_id": 1, "email": "test@example.com"}
        mock_db.execute_query.return_value = []
        response = client.get("/api/teams", headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "teams" in data
        assert isinstance(data["teams"], list)
        assert len(data["teams"]) == 0


def test_get_available_teams_empty(client, mock_db, auth_headers):
    """Test getting available teams when there are none."""
    mock_db.reset_mock()
    with patch("app.services.auth_service.AuthService.verify_jwt") as mock_verify:
        mock_verify.return_value = {"user_id": 1, "email": "test@example.com"}
        mock_db.execute_query.return_value = []
        response = client.get("/api/teams/available", headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "teams" in data
        assert isinstance(data["teams"], list)
        assert len(data["teams"]) == 0


# Additional edge case and negative tests for teams API
def test_kick_user_missing_user_id(client, mock_db, auth_headers):
    """Test kicking a user with missing user_id in request body."""
    mock_db.reset_mock()
    with patch("app.services.auth_service.AuthService.verify_jwt") as mock_verify:
        mock_verify.return_value = {"user_id": 1, "email": "test@example.com"}
        response = client.post(
            "/api/teams/1/kick",
            data=json.dumps({}),
            content_type="application/json",
            headers=auth_headers,
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
    assert "user_id is required" in data["error"].lower()


def test_kick_user_non_integer_user_id(client, mock_db, auth_headers):
    """Test kicking a user with non-integer user_id."""
    mock_db.reset_mock()
    with patch("app.services.auth_service.AuthService.verify_jwt") as mock_verify:
        mock_verify.return_value = {"user_id": 1, "email": "test@example.com"}
        response = client.post(
            "/api/teams/1/kick",
            data=json.dumps({"user_id": "abc"}),
            content_type="application/json",
            headers=auth_headers,
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
    assert "user_id must be an integer" in data["error"].lower()


def test_get_team_count_success(client, mock_db, auth_headers):
    """Test getting the number of teams for a user."""
    mock_db.reset_mock()
    with patch("app.services.auth_service.AuthService.verify_jwt") as mock_verify:
        mock_verify.return_value = {"user_id": 1, "email": "test@example.com"}
        mock_db.execute_one.return_value = {"count": 3}
        # Patch TeamService.get_user_team_count to return 3
        with patch(
            "app.services.team_service.TeamService.get_user_team_count"
        ) as mock_count:
            mock_count.return_value = 3
            response = client.get("/api/teams/count", headers=auth_headers)
            assert response.status_code == 200
            data = json.loads(response.data)
            assert "count" in data
            assert data["count"] == 3


def test_get_team_count_internal_error(client, mock_db, auth_headers):
    """Test get_team_count with simulated internal error."""
    mock_db.reset_mock()
    with patch("app.services.auth_service.AuthService.verify_jwt") as mock_verify:
        mock_verify.return_value = {"user_id": 1, "email": "test@example.com"}
        with patch(
            "app.services.team_service.TeamService.get_user_team_count",
            side_effect=Exception("fail"),
        ):
            response = client.get("/api/teams/count", headers=auth_headers)
            assert response.status_code == 500
            data = json.loads(response.data)
            assert "error" in data
            assert "internal server error" in data["error"].lower()


def test_list_team_users_not_authorized(client, mock_db, auth_headers):
    """Test list_team_users when service returns not authorized (success=False)."""
    mock_db.reset_mock()
    with patch("app.services.auth_service.AuthService.verify_jwt") as mock_verify:
        mock_verify.return_value = {"user_id": 1, "email": "test@example.com"}
        with patch("app.services.team_service.TeamService.get_team_users") as mock_get:
            mock_get.return_value = (False, "forbidden", [])
            response = client.get("/api/teams/1/users", headers=auth_headers)
            assert response.status_code == 403
            data = json.loads(response.data)
            assert "error" in data
            assert "forbidden" in data["error"].lower()


def test_disband_team_not_found(client, mock_db, auth_headers):
    """Test disband_team for a team that does not exist (simulate 'not found' in message)."""
    mock_db.reset_mock()
    with patch("app.services.auth_service.AuthService.verify_jwt") as mock_verify:
        mock_verify.return_value = {"user_id": 1, "email": "test@example.com"}
        with patch(
            "app.services.team_service.TeamService.disband_team"
        ) as mock_disband:
            mock_disband.return_value = (False, "Team not found")
            response = client.delete("/api/teams/999", headers=auth_headers)
            assert response.status_code == 404
            data = json.loads(response.data)
            assert "error" in data
            assert "not found" in data["error"].lower()


def test_create_team_missing_description(client, mock_db, auth_headers):
    """Test creating a team with description field missing (should default to empty string)."""
    mock_db.reset_mock()
    with (
        patch("app.services.auth_service.AuthService.verify_jwt") as mock_verify,
        patch("app.services.team_service.TeamService.create_team") as mock_create_team,
        patch(
            "app.services.team_service.TeamService.get_team_details"
        ) as mock_get_team_details,
    ):
        mock_verify.return_value = {"user_id": 1, "email": "test@example.com"}
        mock_create_team.return_value = (True, "Team created", 1)
        mock_get_team_details.return_value = {
            "id": 1,
            "name": "No Desc Team",
            "description": "",
            "owner_id": 1,
            "created_at": "2025-10-03T10:00:00",
            "updated_at": "2025-10-03T10:00:00",
            "file_count": 0,
            "member_count": 1,
            "role": "admin",
        }
        team_data = {"name": "No Desc Team"}
        response = client.post(
            "/api/teams",
            data=json.dumps(team_data),
            content_type="application/json",
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["name"] == "No Desc Team"
        assert data["description"] == ""
