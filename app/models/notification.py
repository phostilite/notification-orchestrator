# app/models/notification.py
from sqlalchemy import Column, String, ForeignKey, JSON, Integer, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from .base import Base

class Notification(Base):
    """
    Represents a notification to be sent to a user.
    """
    user_id = Column(UUID(as_uuid=True), ForeignKey('user.id'), nullable=False)
    template_id = Column(UUID(as_uuid=True), ForeignKey('notificationtemplate.id'), nullable=False)
    channel = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    variables = Column(JSON)
    priority = Column(Integer, default=1)
    scheduled_for = Column(DateTime(timezone=True))
    timezone = Column(String(50), nullable=True)
    sent_at = Column(DateTime(timezone=True))
    status = Column(String(20), default='pending')  
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    error_message = Column(Text)
    notification_metadata = Column(JSON)
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    template = relationship("NotificationTemplate", back_populates="notifications")
    delivery_statuses = relationship("DeliveryStatus", back_populates="notification", cascade="all, delete-orphan")
