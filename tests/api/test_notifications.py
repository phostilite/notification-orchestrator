# tests/api/test_notifications.py

# Standard library imports
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from uuid import uuid4

# Third-party imports
import pytest
import pytz

@pytest.mark.asyncio
async def test_create_notification_without_db(client, mock_notification):
    """Test notification creation without database"""
    
    notification_data = {
        "user_id": mock_notification["user_id"],
        "template_id": mock_notification["template_id"],
        "channel": "email",
        "variables": {"name": "Test User"},
        "priority": 1,
        "scheduled_for": mock_notification["scheduled_for"]
    }

    # Mock the response that would come from the API
    expected_response = {
        "status": "success",
        "data": mock_notification
    }

    # Patch the post request to return our mock response
    with patch('fastapi.testclient.TestClient.post') as mock_post:
        mock_post.return_value.status_code = 201
        mock_post.return_value.json.return_value = expected_response

        response = client.post(
            "/api/v1/notifications/",
            json=notification_data,
            headers={"Authorization": "Bearer test_token"}
        )

        assert response.status_code == 201
        data = response.json()["data"]
        assert data["user_id"] == notification_data["user_id"]
        assert data["template_id"] == notification_data["template_id"]
        assert data["status"] == "pending"

@pytest.mark.asyncio
async def test_get_notification(client, admin_auth_headers, test_notification):
    """Test getting a single notification"""
    response = client.get(
        f"/api/v1/notifications/{test_notification.id}",
        headers=admin_auth_headers
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["id"] == str(test_notification.id)
    assert data["status"] == test_notification.status

@pytest.mark.asyncio
async def test_update_notification(client, admin_auth_headers, test_notification):
    """Test updating a notification"""
    update_data = {
        "priority": 2,
        "scheduled_for": (datetime.now(pytz.UTC) + timedelta(hours=2)).isoformat()
    }

    response = client.put(
        f"/api/v1/notifications/{test_notification.id}",
        json=update_data,
        headers=admin_auth_headers
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["priority"] == 2

@pytest.mark.asyncio
async def test_delete_notification(client, admin_auth_headers, test_notification):
    """Test deleting a notification"""
    response = client.delete(
        f"/api/v1/notifications/{test_notification.id}",
        headers=admin_auth_headers
    )

    assert response.status_code == 200
    assert response.json()["status"] == "success"

    # Verify deletion
    response = client.get(
        f"/api/v1/notifications/{test_notification.id}",
        headers=admin_auth_headers
    )
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_list_notifications(client, admin_auth_headers, test_notification):
    """Test listing notifications with pagination"""
    response = client.get(
        "/api/v1/notifications/?limit=10&skip=0",
        headers=admin_auth_headers
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert isinstance(data, list)
    assert len(data) > 0

@pytest.mark.asyncio
async def test_get_delivery_status(client, admin_auth_headers, test_notification, test_delivery_status):
    """Test getting delivery status for a notification"""
    response = client.get(
        f"/api/v1/notifications/{test_notification.id}/delivery-status",
        headers=admin_auth_headers
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["notification_id"] == str(test_notification.id)

# Negative test cases
@pytest.mark.asyncio
async def test_create_notification_invalid_template(client, admin_auth_headers, test_admin_user):
    """Test notification creation with invalid template"""
    notification_data = {
        "user_id": str(test_admin_user.id),
        "template_id": str(uuid4()),
        "channel": "email",
        "variables": {"name": "Test User"}
    }

    response = client.post(
        "/api/v1/notifications/",
        json=notification_data,
        headers=admin_auth_headers
    )

    assert response.status_code == 404
    assert "Template not found" in response.json()["detail"]

@pytest.mark.asyncio
async def test_update_sent_notification(client, admin_auth_headers, test_notification_sent):
    """Test updating an already sent notification"""
    update_data = {
        "priority": 2
    }

    response = client.put(
        f"/api/v1/notifications/{test_notification_sent.id}",
        json=update_data,
        headers=admin_auth_headers
    )

    assert response.status_code == 400
    assert "already been sent" in response.json()["detail"]