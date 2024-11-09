# app/models/delivery_status.py

# Third-party imports
from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

# Local application imports
from .base import Base

class DeliveryStatus(Base):
    """Tracks individual delivery attempts and their outcomes"""
    notification_id = Column(UUID(as_uuid=True), ForeignKey('notification.id'), nullable=False)
    attempt_number = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False)  # success, failed
    provider_response = Column(JSON)
    error_code = Column(String(50))
    error_message = Column(Text)
    delivered_at = Column(DateTime)
    
    # Relationships
    notification = relationship("Notification", back_populates="delivery_statuses")