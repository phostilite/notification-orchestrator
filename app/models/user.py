# app/models/user.py
from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship
from .base import Base

class User(Base):
    """User model for authentication and notification preferences"""
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20), unique=True, index=True)
    full_name = Column(String(100))
    hashed_password = Column(String(255), nullable=False)
    is_verified = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    
    # Relationships
    preferences = relationship("UserPreference", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
