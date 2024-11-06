# app/models/notification.py
from sqlalchemy import Column, String, ForeignKey, JSON, Integer, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from .base import Base

class Notification(Base):
    """
    Represents a notification to be sent to a user.

    Attributes:
        user_id (UUID): Foreign key referencing the user receiving the notification.
        template_id (UUID): Foreign key referencing the notification template.
        channel (str): The channel through which the notification will be sent (e.g., email, SMS, push).
        content (str): The content of the notification.
        variables (JSON): Dynamic variables to be used in the notification template.
        priority (int): The priority level of the notification.
        scheduled_for (datetime): The timestamp when the notification is scheduled to be sent.
        sent_at (datetime): The timestamp when the notification was sent.
        status (str): The current status of the notification (e.g., pending, sent, failed).
        retry_count (int): The number of retry attempts made for the notification.
        max_retries (int): The maximum number of retry attempts allowed.
        error_message (str): The error message if the notification failed.
        notification_metadata (JSON): Additional metadata related to the notification.
    """
    user_id = Column(UUID(as_uuid=True), ForeignKey('user.id'), nullable=False)
    template_id = Column(UUID(as_uuid=True), ForeignKey('notificationtemplate.id'), nullable=False)
    channel = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    variables = Column(JSON)
    priority = Column(Integer, default=1)
    scheduled_for = Column(DateTime)
    sent_at = Column(DateTime)
    status = Column(String(20), default='pending')  # pending, sent, failed, cancelled
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    error_message = Column(Text)
    notification_metadata = Column(JSON)
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    template = relationship("NotificationTemplate", back_populates="notifications")
    delivery_statuses = relationship("DeliveryStatus", back_populates="notification", cascade="all, delete-orphan")
