"""
Tests for team_service.py
"""

from app.services.team_service import TeamService


def test_create_team_success(mock_db):
    """Test creating a team successfully."""
    mock_db.reset_mock()
    # 1. No duplicate team name
    # 2. Insert team returns id
    mock_db.execute_one.side_effect = [None, {"id": 1}]
    mock_db.execute_modify.return_value = 1
    success, msg, team_id = TeamService.create_team("Team A", "desc", 1)
    assert success
    assert team_id == 1
    assert msg == "Team created successfully"


def test_get_team_details_success(mock_db):
    """Test retrieving team details successfully."""
    mock_db.reset_mock()
    # 1. User is a member
    # 2. Team details
    mock_db.execute_one.side_effect = [
        {"role": "admin"},
        {"id": 1, "name": "Team A", "owner_id": 1},
    ]
    team = TeamService.get_team_details(1, 1)
    assert team["id"] == 1
    assert team["role"] == "admin"


def test_create_team_duplicate_name(mock_db):
    """Test creating a team with a duplicate name fails."""
    mock_db.reset_mock()
    mock_db.execute_one.side_effect = [{"id": 1}]
    success, msg, team_id = TeamService.create_team("Team A", "desc", 1)
    assert not success
    assert msg == "Team name already exists"
    assert team_id is None


def test_create_team_db_error(mock_db):
    """Test DB error during team creation returns failure."""
    mock_db.reset_mock()
    mock_db.execute_one.side_effect = [None, Exception("DB error")]
    success, msg, team_id = TeamService.create_team("Team B", "desc", 2)
    assert not success
    assert msg == "Failed to create team"
    assert team_id is None


def test_join_team_success(mock_db):
    """Test joining a team successfully."""
    mock_db.reset_mock()
    # 1. Team exists
    # 2. Not already a member
    mock_db.execute_one.side_effect = [
        {"name": "Team A"},
        None,
    ]
    mock_db.execute_modify.return_value = 1
    success, msg = TeamService.join_team(1, 2)
    assert success
    assert msg == "Successfully joined team"


def test_leave_team_success(mock_db):
    """Test leaving a team successfully."""
    mock_db.reset_mock()
    # 1. User is member
    # 2. Team exists, not owner
    mock_db.execute_one.side_effect = [
        {"role": "member"},
        {"name": "Team A", "owner_id": 1},
    ]
    mock_db.execute_modify.return_value = 1
    success, msg = TeamService.leave_team(1, 2)
    assert success
    assert msg == "Successfully left team"


def test_disband_team_success(mock_db):
    """Test disbanding a team as owner succeeds."""
    mock_db.reset_mock()
    # 1. Team exists and user is owner
    # 2. No files
    mock_db.execute_one.side_effect = [
        {"name": "Team A", "owner_id": 2},
        {"count": 0},
    ]
    mock_db.execute_modify.return_value = 1
    success, msg = TeamService.disband_team(1, 2)
    assert success
    assert "disbanded successfully" in msg


def test_kick_user_from_team_success(mock_db):
    """Test kicking a user from team as admin/owner succeeds."""
    mock_db.reset_mock()
    # 1. Kicker is admin
    # 2. Target is member
    # 3. Team info
    # 4. Target user info
    mock_db.execute_one.side_effect = [
        {"role": "admin"},
        {"role": "member"},
        {"name": "Team A", "owner_id": 2},
        {"email": "target@example.com"},
    ]
    mock_db.execute_modify.return_value = 1
    success, msg = TeamService.kick_user_from_team(1, 3, 2)
    assert success
    assert "successfully removed" in msg
