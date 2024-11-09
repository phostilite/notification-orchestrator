# tests/conftest.py

# Standard library imports
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from uuid import uuid4

# Third-party imports
import pytest
import pytest_asyncio
import pytz
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Local application imports
from app.core.auth import create_access_token
from app.core.config import settings
from app.db.session import get_db
from app.main import app
from app.models.base import Base
from app.models.delivery_status import DeliveryStatus
from app.models.notification import Notification
from app.models.template import NotificationTemplate
from app.schemas.user import UserCreate
from app.services.senders.email_sender import EmailSender
from app.services.user_service import UserService

# Test database URL  
TEST_DATABASE_URL = "postgresql://notification_service_user:hunter2butbetter@localhost:5432/notification_service_test"

# Create test engine
test_engine = create_engine(TEST_DATABASE_URL)

# Create test session factory
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="session")
def engine():
    """Create test database engine"""
    return test_engine  # Return the test_engine instance

@pytest.fixture(scope="function")
def test_db():
    """Create fresh test database tables for each test"""
    Base.metadata.create_all(bind=test_engine)
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)

@pytest.fixture(scope="function")
def client(test_db):
    """Create test client with database dependency override"""
    def override_get_db():
        try:
            yield test_db
        finally:
            test_db.close()
            
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)

@pytest_asyncio.fixture
async def test_user(test_db: Session):
    """Async fixture for creating test user"""
    user_data = UserCreate(
        email="test@example.com",
        password="testpass123",
        phone="+1234567890",
        full_name="Test User"
    )
    user = await UserService.create_user(db=test_db, user_create=user_data)
    return user

@pytest_asyncio.fixture
async def test_admin_user(test_db: Session):
    """Async fixture for creating test admin user"""
    user_data = UserCreate(
        email="admin@example.com",  # Changed email to avoid conflicts
        password="testpass123",
        phone="+1234567890",
        full_name="Test Admin",
        is_admin=True
    )
    user = await UserService.create_user(db=test_db, user_create=user_data)
    test_db.commit()  # Commit the transaction
    test_db.refresh(user)  # Refresh the user
    return user

@pytest.fixture
def auth_headers(test_user):
    """Fixture to create authentication headers for regular users"""
    access_token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture
def admin_auth_headers(test_db, test_admin_user):
    """Fixture to create authentication headers for admin users"""
    test_db.add(test_admin_user)
    test_db.commit()  # Add commit here
    test_db.refresh(test_admin_user)
    access_token = create_access_token(data={
        "sub": str(test_admin_user.id),
        "is_admin": True
    })
    return {"Authorization": f"Bearer {access_token}"}



@pytest.fixture
def test_template(test_db, test_admin_user):
    """Create a test notification template"""
    template = NotificationTemplate(
        name="test_template",
        description="Test template",
        channel="email",
        content="Hello {{name}}",
        variables={"name": {"type": "string"}},
        version=1
    )
    
    test_db.add(template)
    test_db.commit()
    test_db.refresh(template)
    return template

@pytest.fixture
def test_notification(test_db, test_admin_user, test_template):
    """Create a test notification"""
    notification = Notification(
        user_id=test_admin_user.id,
        template_id=test_template.id,
        channel="email",
        content="Test content",
        variables={"name": "Test User"},
        status="pending",
        scheduled_for=datetime.now(pytz.UTC) + timedelta(hours=1)
    )
    test_db.add(notification)
    test_db.commit()
    return notification

@pytest.fixture
def mock_notification():
    """Create a mock notification data"""
    return {
        "id": str(uuid4()),
        "user_id": str(uuid4()),
        "template_id": str(uuid4()),
        "channel": "email",
        "variables": {"name": "Test User"},
        "priority": 1,
        "status": "pending",
        "scheduled_for": (datetime.now(pytz.UTC) + timedelta(hours=1)).isoformat()
    }

@pytest.fixture
def mock_notification_for_service():
    """Create a mock notification object with required attributes"""
    notification = Mock()
    # Configure the template mock with a name property
    template_mock = Mock()
    template_mock.name = "Test Template"  # Set as property instead of Mock
    notification.template = template_mock
    
    # Configure user mock
    user_mock = Mock()
    user_mock.email = "test@example.com"
    notification.user = user_mock
    
    notification.content = "<p>Test email content</p>"
    return notification

@pytest.fixture
def test_notification_sent(test_db, test_admin_user, test_template):
    """Create a test notification that has been sent"""
    notification = Notification(
        user_id=test_admin_user.id,
        template_id=test_template.id,
        channel="email",
        content="Test content",
        variables={"name": "Test User"},
        status="sent",
        scheduled_for=datetime.now(pytz.UTC) - timedelta(hours=1),
        sent_at=datetime.now(pytz.UTC)
    )
    test_db.add(notification)
    test_db.commit()
    return notification

@pytest.fixture
def test_delivery_status(test_db, test_notification):
    """Create a test delivery status"""
    status = DeliveryStatus(
        notification_id=test_notification.id,
        status="delivered",
        attempt_number=1,
        delivered_at=datetime.now(pytz.UTC)
    )
    test_db.add(status)
    test_db.commit()
    return status

@pytest.fixture
def email_sender():
    """Create email sender instance"""
    return EmailSender()