# tests/api/test_templates.py

# Standard library imports
from http import HTTPStatus

def test_create_notification_template(client, admin_auth_headers):
    """Test creating a new notification template"""
    # Arrange
    template_data = {
        "name": "user_welcome_email_2_3_1",
        "description": "Welcome email template",
        "channel": "email",
        "content": "Hello *{{name}}*, Welcome to our service!",
        "variables": {
            "name": "string"
        },
        "version": 1
    }

    # Act
    response = client.post(
        "/api/v1/templates/",
        json=template_data,
        headers=admin_auth_headers
    )
    response_data = response.json()

    # Assert
    assert response.status_code == HTTPStatus.CREATED
    assert response_data["status"] == "success"
    assert response_data["message"] == "Template created successfully"
    
    # Verify the returned data matches input
    created_template = response_data["data"]
    assert created_template["name"] == template_data["name"]
    assert created_template["description"] == template_data["description"]
    assert created_template["channel"] == template_data["channel"]
    assert created_template["content"] == template_data["content"]
    assert created_template["variables"] == template_data["variables"]
    assert created_template["version"] == template_data["version"]
    
    # Verify additional fields are present
    assert "id" in created_template
    assert "created_at" in created_template
    assert "updated_at" in created_template

def test_update_template(client, test_db, admin_auth_headers):
    # Arrange
    template_data = {
        "name": "test_template",
        "description": "Test template",
        "channel": "email",
        "content": "Hello {{name}}",
        "variables": {"name": {"type": "string"}},
        "version": 1
    }
    
    # Create initial template
    response = client.post(
        "/api/v1/templates/",
        json=template_data,
        headers=admin_auth_headers
    )
    template_id = response.json()["data"]["id"]
    
    # Act
    update_data = {
        "name": "updated_template",
        "description": "Updated description",
        "content": "Hi {{name}}!",
        "version": 2
    }
    
    response = client.put(
        f"/api/v1/templates/{template_id}",
        json=update_data,
        headers=admin_auth_headers
    )
    response_data = response.json()

    # Assert
    assert response.status_code == HTTPStatus.OK
    assert response_data["status"] == "success"
    assert response_data["message"] == "Template updated successfully"
    
    updated_template = response_data["data"]
    assert updated_template["name"] == update_data["name"]
    assert updated_template["description"] == update_data["description"]
    assert updated_template["content"] == update_data["content"]
    assert updated_template["version"] == update_data["version"]
    assert updated_template["channel"] == template_data["channel"]

def test_delete_template(client, test_db, admin_auth_headers):
    # Arrange
    template_data = {
        "name": "template_to_delete",
        "description": "Template to be deleted",
        "channel": "email",
        "content": "Hello {{name}}",
        "variables": {"name": {"type": "string"}},
        "version": 1
    }
    
    # Create template to delete
    response = client.post(
        "/api/v1/templates/",
        json=template_data,
        headers=admin_auth_headers
    )
    template_id = response.json()["data"]["id"]
    
    # Act
    response = client.delete(
        f"/api/v1/templates/{template_id}",
        headers=admin_auth_headers
    )
    response_data = response.json()

    # Assert
    assert response.status_code == HTTPStatus.OK
    assert response_data["status"] == "success"
    assert response_data["message"] == "Template deleted successfully"
    assert response_data["data"]["template_id"] == template_id
    
    # Verify template is deleted
    get_response = client.get(
        f"/api/v1/templates/{template_id}",
        headers=admin_auth_headers
    )
    assert get_response.status_code == HTTPStatus.NOT_FOUND