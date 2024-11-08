# app/schemas/notification.py
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, UUID4, Field
from .base import BaseSchema
from enum import Enum

class NotificationBase(BaseSchema):
    channel: str = Field(..., description="Notification channel (email, sms, push)")
    template_id: UUID4
    variables: Dict[str, Any] = Field(default_factory=dict)
    priority: int = Field(default=1, ge=1, le=5)
    scheduled_for: Optional[datetime] = None

class NotificationCreate(NotificationBase):
    user_id: UUID4

class NotificationUpdate(BaseModel):
    status: Optional[str] = None

class NotificationResponse(NotificationBase):
    id: UUID4
    user_id: UUID4
    status: str
    content: str
    created_at: datetime
    sent_at: Optional[datetime]
    error_message: Optional[str]

class NotificationList(BaseModel):
    items: List[NotificationResponse]
    total: int
    skip: int
    limit: int

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