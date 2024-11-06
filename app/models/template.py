# app/models/template.py
from sqlalchemy import Column, String, Integer, Text, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from .base import Base

class NotificationTemplate(Base):
    """Template model for notification content"""
    name = Column(String(100), nullable=False)
    version = Column(Integer, nullable=False, default=1)
    content = Column(Text, nullable=False)
    variables = Column(JSON)  # JSON schema for required variables
    channel = Column(String(20), nullable=False)  # email, sms, push
    description = Column(String(255))
    
    # Relationships
    notifications = relationship("Notification", back_populates="template")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('name', 'version', name='uix_template_version'),
    )