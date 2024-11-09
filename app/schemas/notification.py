# app/schemas/notification.py

# Standard library imports
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from uuid import UUID

# Third-party imports
from pydantic import BaseModel, Field

class NotificationBase(BaseModel):
    channel: str = Field(..., description="Notification channel (email, sms, push)")
    variables: Dict[str, Any] = Field(default_factory=dict)
    priority: int = Field(default=1, ge=1, le=5)
    scheduled_for: Optional[datetime] = None

class NotificationCreate(NotificationBase):
    user_id: UUID
    template_id: UUID

class NotificationUpdate(BaseModel):
    template_id: Optional[UUID] = None
    channel: Optional[str] = None
    variables: Optional[Dict[str, Any]] = None
    priority: Optional[int] = Field(None, ge=1, le=5)
    scheduled_for: Optional[datetime] = None

class NotificationResponse(NotificationBase):
    id: UUID
    user_id: UUID
    template_id: UUID
    status: str
    content: str
    scheduled_for: datetime
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class NotificationDetails(NotificationResponse):
    notification_metadata: Optional[Dict[str, Any]] = None
    timezone: Optional[str] = None

class NotificationChannel(str, Enum):
    """Supported notification channels"""
    EMAIL = "email"
    SMS = "sms" 
    PUSH = "push"
    
    @classmethod
    def list(cls):
        """Get list of all channel values"""
        return list(map(lambda c: c.value, cls))

    def __str__(self):
        return self.value
    
class NotificationStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing" 
    SENT = "sent"
    FAILED = "failed"
    FAILED_PERMANENT = "failed_permanent"

class DeliveryStatusResponse(BaseModel):
    notification_id: UUID
    attempt_number: int
    status: str
    provider_response: Optional[Dict[str, Any]]
    error_code: Optional[str]
    error_message: Optional[str]
    delivered_at: Optional[datetime]
    created_at: datetime

    class Config:
        orm_mode = True