"""
Test for app routing.
"""

import json


def test_root_endpoint(client):
    """Test that the root endpoint works."""
    response = client.get("/")

    assert response.status_code == 200
    data = json.loads(response.data)
    assert "message" in data
    assert data["message"] == "Markboard API"


def test_routes_registered(app):
    """Test that routes are registered."""
    # Get the map of registered routes
    rules = [rule.rule for rule in app.url_map.iter_rules()]

    # Print all rules for debugging
    print("\nRegistered routes:", rules)

    # Check that basic app routes exist
    assert "/" in rules
