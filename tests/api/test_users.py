# tests/api/test_users.py

# Third-party imports
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

# Local application imports
from app.core.auth import create_access_token
from app.main import app
from app.models.user import User
from app.schemas.user import UserCreate
from app.services.user_service import UserService

# Initialize test client
client = TestClient(app)

@pytest.fixture
def valid_user_data():
    """Fixture for valid user registration data"""
    return {
        "email": "test@example.com",
        "password": "Test123!",
        "phone": "+1234567890",
        "full_name": "Test User"
    }

@pytest.fixture
def auth_headers(test_user):
    access_token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {access_token}"}

def test_register_user_success(client, test_db, valid_user_data):
    """Test successful user registration"""
    response = client.post("/api/v1/users/register", json=valid_user_data)
    
    # Print response for debugging
    print(f"Response: {response.json()}")
    
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "success"
    assert data["message"] == "User registered successfully"
    
    # Verify user was created in DB
    user = test_db.query(User).filter(User.email == valid_user_data["email"]).first()
    assert user is not None
    assert user.email == valid_user_data["email"]


def test_register_user_duplicate_email(client, test_db, valid_user_data):
    """Test registration with duplicate email"""
    # First registration
    response1 = client.post("/api/v1/users/register", json=valid_user_data)
    assert response1.status_code == 201
    
    # Attempt duplicate registration
    response2 = client.post("/api/v1/users/register", json=valid_user_data)
    assert response2.status_code == 400  # Changed from 200 to 400 for duplicate
    data = response2.json()
    assert data["status"] == "error"
    assert "already registered" in data["message"].lower()

def test_register_user_invalid_email(test_db):
    """Test registration with invalid email format"""
    invalid_user_data = {
        "email": "invalid-email",
        "password": "Test123!",
        "phone": "+1234567890",
        "full_name": "Test User"
    }
    
    response = client.post("/api/v1/users/register", json=invalid_user_data)
    
    assert response.status_code == 422  # FastAPI validation error

def test_register_user_missing_required_fields(test_db):
    """Test registration with missing required fields"""
    incomplete_data = {
        "email": "test@example.com"
        # Missing password and other required fields
    }
    
    response = client.post("/api/v1/users/register", json=incomplete_data)
    
    assert response.status_code == 422


def test_login_success(client, test_db, valid_user_data):
    """Test successful user login"""
    # First register a user
    client.post("/api/v1/users/register", json=valid_user_data)
    
    # Attempt login
    login_data = {
        "username": valid_user_data["email"],
        "password": valid_user_data["password"]
    }
    response = client.post("/api/v1/users/login", data=login_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["message"] == "Login successful"
    assert "access_token" in data["data"]
    assert data["data"]["token_type"] == "bearer"

def test_login_missing_credentials(client, test_db):
    """Test login with missing credentials"""
    login_data = {
        "username": "",
        "password": ""
    }
    response = client.post("/api/v1/users/login", data=login_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "error"
    assert data["message"] == "Email and password are required"

def test_login_invalid_credentials(client, test_db):
    """Test login with invalid credentials"""
    login_data = {
        "username": "nonexistent@example.com",
        "password": "wrongpassword"
    }
    response = client.post("/api/v1/users/login", data=login_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "error"
    assert data["message"] == "Invalid email or password"

def test_login_correct_email_wrong_password(client, test_db, valid_user_data):
    """Test login with correct email but wrong password"""
    # First register a user
    client.post("/api/v1/users/register", json=valid_user_data)
    
    # Attempt login with wrong password
    login_data = {
        "username": valid_user_data["email"],
        "password": "wrongpassword123"
    }
    response = client.post("/api/v1/users/login", data=login_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "error"
    assert data["message"] == "Invalid email or password"

def test_get_user_profile_no_auth():
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Not authenticated"

def test_get_user_profile_invalid_token():
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/api/v1/users/me", headers=headers)
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data
    assert "Invalid authentication token format" in data["detail"]

def test_get_user_profile_expired_token(client: TestClient):
    # Create an expired token
    from datetime import timedelta
    access_token = create_access_token(
        data={"sub": "123"}, 
        expires_delta=timedelta(minutes=-1)
    )
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = client.get("/api/v1/users/me", headers=headers)
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data
    assert "Token has expired" in data["detail"]

def test_update_profile_success(client, test_db):
    """Test successful profile update"""
    # First create a user
    user_data = {
        "email": "test@example.com",
        "password": "Test123!",
        "phone": "+1234567890",
        "full_name": "Test User"
    }
    # Register the user
    register_response = client.post("/api/v1/users/register", json=user_data)
    assert register_response.status_code == 201

    # Login to get token
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    login_response = client.post("/api/v1/users/login", data=login_data)
    assert login_response.status_code == 200
    token = login_response.json()["data"]["access_token"]
    
    # Update profile
    update_data = {
        "default_timezone": "Asia/Kolkata"
    }
    
    response = client.put(
        "/api/v1/users/me",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["message"] == "User profile updated successfully"
    assert data["data"]["default_timezone"] == "Asia/Kolkata"

def test_update_profile_no_auth(client):
    """Test profile update without authentication"""
    update_data = {
        "default_timezone": "Asia/Kolkata"
    }
    
    response = client.put("/api/v1/users/me", json=update_data)
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Not authenticated"

def test_update_profile_duplicate_email(client, test_db):
    """Test profile update with duplicate email"""
    # Create first user
    user1_data = {
        "email": "user1@example.com",
        "password": "Test123!",
        "phone": "+1234567890",
        "full_name": "User One"
    }
    client.post("/api/v1/users/register", json=user1_data)
    
    # Create second user
    user2_data = {
        "email": "user2@example.com",
        "password": "Test123!",
        "phone": "+1987654321",
        "full_name": "User Two"
    }
    client.post("/api/v1/users/register", json=user2_data)
    
    # Login as second user
    login_response = client.post("/api/v1/users/login", 
                               data={"username": user2_data["email"], 
                                    "password": user2_data["password"]})
    token = login_response.json()["data"]["access_token"]
    
    # Try to update email to first user's email
    update_data = {
        "email": user1_data["email"]
    }
    
    response = client.put(
        "/api/v1/users/me",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "error"
    assert "email already registered" in data["message"].lower()

def test_update_profile_invalid_timezone(client, test_db):
    """Test profile update with invalid timezone"""
    # Create and login user
    user_data = {
        "email": "test@example.com",
        "password": "Test123!",
        "phone": "+1234567890",
        "full_name": "Test User"
    }
    client.post("/api/v1/users/register", json=user_data)
    
    login_response = client.post("/api/v1/users/login", 
                               data={"username": user_data["email"], 
                                    "password": user_data["password"]})
    token = login_response.json()["data"]["access_token"]
    
    # Test case 1: Completely invalid timezone
    update_data = {
        "default_timezone": "Invalid/Timezone"
    }
    response = client.put(
        "/api/v1/users/me",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 422
    assert "Invalid timezone" in str(response.json()["detail"])

    # Test case 2: Similar but incorrect timezone
    update_data = {
        "default_timezone": "Asia/NewDelhi"  # Correct would be Asia/Kolkata
    }
    response = client.put(
        "/api/v1/users/me",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 422
    assert "Invalid timezone" in str(response.json()["detail"])


def test_update_profile_multiple_fields(client, test_db):
    """Test updating multiple profile fields at once"""
    # Create and login user
    user_data = {
        "email": "test@example.com",
        "password": "Test123!",
        "phone": "+1234567890",
        "full_name": "Test User"
    }
    client.post("/api/v1/users/register", json=user_data)
    
    login_response = client.post("/api/v1/users/login", 
                               data={"username": user_data["email"], 
                                    "password": user_data["password"]})
    token = login_response.json()["data"]["access_token"]
    
    update_data = {
        "full_name": "Updated Name",
        "default_timezone": "America/New_York"
    }
    
    response = client.put(
        "/api/v1/users/me",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["message"] == "User profile updated successfully"
    assert data["data"]["full_name"] == "Updated Name"
    assert data["data"]["default_timezone"] == "America/New_York"

def test_update_profile_invalid_token(client):
    """Test profile update with invalid token"""
    headers = {"Authorization": "Bearer invalid_token"}
    
    update_data = {
        "default_timezone": "Asia/Kolkata"
    }
    
    response = client.put("/api/v1/users/me", 
                         json=update_data,
                         headers=headers)
    
    assert response.status_code == 401
    data = response.json()
    assert "Invalid authentication token format" in data["detail"]


def test_delete_account_success(client, test_db):
    """Test successful account deletion"""
    # Create user
    user_data = {
        "email": "delete_test@example.com",
        "password": "Test123!",
        "phone": "+1234567890",
        "full_name": "Delete Test User"
    }
    register_response = client.post("/api/v1/users/register", json=user_data)
    assert register_response.status_code == 201

    # Login to get token
    login_response = client.post("/api/v1/users/login", 
                               data={"username": user_data["email"], 
                                    "password": user_data["password"]})
    token = login_response.json()["data"]["access_token"]
    
    # Delete account
    response = client.delete(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["message"] == "User account deleted successfully"
    assert data["data"]["email"] == user_data["email"]

    # Verify user no longer exists
    login_response = client.post("/api/v1/users/login", 
                               data={"username": user_data["email"], 
                                    "password": user_data["password"]})
    assert login_response.json()["status"] == "error"

def test_delete_account_no_auth(client):
    """Test account deletion without authentication"""
    response = client.delete("/api/v1/users/me")
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Not authenticated"

def test_delete_account_invalid_token(client):
    """Test account deletion with invalid token"""
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.delete("/api/v1/users/me", headers=headers)
    
    assert response.status_code == 401
    data = response.json()
    assert "Invalid authentication token format" in data["detail"]

def test_delete_account_expired_token(client):
    """Test account deletion with expired token"""
    from datetime import timedelta
    
    # Create expired token
    access_token = create_access_token(
        data={"sub": "123"},
        expires_delta=timedelta(minutes=-1)
    )
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = client.delete("/api/v1/users/me", headers=headers)
    assert response.status_code == 401
    data = response.json()
    assert "Token has expired" in data["detail"]