# tests/api/test_preferences.py

# Standard library imports
from datetime import time
from http import HTTPStatus
from uuid import UUID

# Third-party imports
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

# Local application imports
from app.models.user import User
from app.models.user_preference import UserPreference

# Mark all tests as async
pytestmark = pytest.mark.asyncio

def test_create_preference(
    client: TestClient,
    auth_headers: dict
):
    """Test successful creation of a user preference"""
    
    # Test data
    preference_data = {
        "channel": "email",
        "enabled": True,
        "quiet_hours_start": "23:00:00",
        "quiet_hours_end": "23:55:00",
        "frequency_limit": 5,
        "priority_threshold": 1
    }

    # Make request to create preference
    response = client.post(
        "/api/v1/preferences/",
        json=preference_data,
        headers=auth_headers
    )

    # Assert response
    assert response.status_code == HTTPStatus.CREATED
    assert response.json()["status"] == "success"
    assert response.json()["message"] == "Preference created successfully"

    # Validate response data
    data = response.json()["data"]
    assert data["channel"] == preference_data["channel"]
    assert data["enabled"] == preference_data["enabled"]
    assert data["quiet_hours_start"] == "23:00"
    assert data["quiet_hours_end"] == "23:55"
    assert data["frequency_limit"] == preference_data["frequency_limit"]
    assert data["priority_threshold"] == preference_data["priority_threshold"]
    
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

@pytest.mark.asyncio
async def test_create_duplicate_preference(client, test_user, auth_headers):
    """Test creating a duplicate preference returns 409 Conflict."""
    # Initial preference data
    preference_data = {
        "channel": "email",
        "enabled": True,
        "quiet_hours_start": "22:00",
        "quiet_hours_end": "08:00",
        "frequency_limit": 10,
        "priority_threshold": 1
    }
    
    # Create first preference
    response1 = client.post(
        "/api/v1/preferences/",
        json=preference_data,
        headers=auth_headers
    )
    assert response1.status_code == 201
    
    # Attempt to create duplicate preference
    response2 = client.post(
        "/api/v1/preferences/",
        json=preference_data,
        headers=auth_headers
    )
    
    assert response2.status_code == 409  # Changed from HTTPStatus to actual status code
    assert response2.json()["status"] == "error"
    assert response2.json()["message"] == "Preference already exists for channel email"
    assert response2.json()["data"] is None


@pytest.mark.asyncio
async def test_get_preferences(client, test_user, auth_headers):
    """Test getting all preferences for a user"""
    # First create a preference
    preference_data = {
        "channel": "email",
        "enabled": True,
        "quiet_hours_start": "23:00",
        "quiet_hours_end": "23:55",
        "frequency_limit": 5,
        "priority_threshold": 1
    }
    
    response = client.post("/api/v1/preferences/", json=preference_data, headers=auth_headers)
    assert response.status_code == 201
    
    # Get all preferences
    response = client.get("/api/v1/preferences/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["data"]) >= 1
    assert data["data"][0]["channel"] == preference_data["channel"]

@pytest.mark.asyncio
async def test_get_single_preference(client, test_user, auth_headers):
    """Test getting a single preference by channel"""
    # First create a preference
    preference_data = {
        "channel": "sms",
        "enabled": True,
        "quiet_hours_start": "23:00",
        "quiet_hours_end": "23:55",
        "frequency_limit": 5,
        "priority_threshold": 1
    }
    
    response = client.post("/api/v1/preferences/", json=preference_data, headers=auth_headers)
    assert response.status_code == 201
    
    # Get single preference
    response = client.get(f"/api/v1/preferences/{preference_data['channel']}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["channel"] == preference_data["channel"]

@pytest.mark.asyncio
async def test_update_preference(client, test_user, auth_headers):
    """Test updating a preference"""
    # First create a preference
    preference_data = {
        "channel": "push",
        "enabled": True,
        "quiet_hours_start": "23:00",
        "quiet_hours_end": "23:55",
        "frequency_limit": 5,
        "priority_threshold": 1
    }
    
    response = client.post("/api/v1/preferences/", json=preference_data, headers=auth_headers)
    assert response.status_code == 201
    
    # Update preference
    update_data = {
        "enabled": False,
        "frequency_limit": 10
    }
    
    response = client.put(
        f"/api/v1/preferences/{preference_data['channel']}", 
        json=update_data,
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["enabled"] == update_data["enabled"]
    assert data["data"]["frequency_limit"] == update_data["frequency_limit"]

@pytest.mark.asyncio
async def test_delete_preference(client, test_user, auth_headers):
    """Test deleting a preference"""
    # First create a preference
    preference_data = {
        "channel": "email",
        "enabled": True,
        "quiet_hours_start": "23:00",
        "quiet_hours_end": "23:55",
        "frequency_limit": 5,
        "priority_threshold": 1
    }
    
    response = client.post("/api/v1/preferences/", json=preference_data, headers=auth_headers)
    assert response.status_code == 201
    
    # Delete preference
    response = client.delete(f"/api/v1/preferences/{preference_data['channel']}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    
    # Verify preference is deleted
    response = client.get(f"/api/v1/preferences/{preference_data['channel']}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "error"
    assert "No preference found" in data["message"]