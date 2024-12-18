# app/models/user_preference.py

# Third-party imports
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Time, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

# Local application imports
from .base import Base

class UserPreference(Base):
    """User preferences for different notification channels"""
    user_id = Column(UUID(as_uuid=True), ForeignKey('user.id'), nullable=False)
    channel = Column(String(20), nullable=False)  # email, sms, push
    enabled = Column(Boolean, default=True)
    quiet_hours_start = Column(Time)
    quiet_hours_end = Column(Time)
    frequency_limit = Column(Integer)  # max notifications per hour
    priority_threshold = Column(Integer, default=1)  # minimum priority level
    
    # Relationships
    user = relationship("User", back_populates="preferences")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'channel', name='uix_user_channel'),
    )
