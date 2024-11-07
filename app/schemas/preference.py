# app/schemas/preference.py
from typing import Optional
from datetime import datetime, time
from pydantic import BaseModel, UUID4, Field
from .base import BaseSchema
from .notification import NotificationChannel

class PreferenceBase(BaseSchema):
    channel: NotificationChannel = Field(..., description="Notification channel (email, sms, push)")
    enabled: bool = True
    quiet_hours_start: Optional[time] = None
    quiet_hours_end: Optional[time] = None
    frequency_limit: Optional[int] = Field(None, ge=0)
    priority_threshold: int = Field(default=1, ge=1, le=5)

class PreferenceCreate(BaseSchema):
    channel: NotificationChannel = Field(..., description="Notification channel (email, sms, push)")
    enabled: bool = True
    quiet_hours_start: Optional[time] = None
    quiet_hours_end: Optional[time] = None
    frequency_limit: Optional[int] = Field(None, ge=0)
    priority_threshold: int = Field(default=1, ge=1, le=5)

class PreferenceUpdate(BaseModel):
    channel: Optional[str] = None
    enabled: Optional[bool] = None
    quiet_hours_start: Optional[time] = None
    quiet_hours_end: Optional[time] = None
    frequency_limit: Optional[int] = Field(None, ge=0)
    priority_threshold: Optional[int] = Field(None, ge=1, le=5)

class PreferenceResponse(PreferenceBase):
    id: UUID4
    user_id: UUID4
    created_at: datetime
    updated_at: datetime