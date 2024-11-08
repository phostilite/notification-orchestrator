# app/models/base.py
from datetime import datetime, timezone
from typing import Any
from sqlalchemy.ext.declarative import declared_attr, declarative_base
from sqlalchemy import Column, DateTime, Boolean, UUID
import uuid

class CustomBase:
    """Base class for all database models providing common functionality.
    
    This class serves as a foundation for SQLAlchemy models with the following features:
    - Automatic table naming based on class name (lowercase)
    - UUID primary key generation
    - Created and updated timestamp tracking
    - Soft deletion support via is_active flag
    
    Attributes:
        id (UUID): Primary key, auto-generated UUID
        created_at (DateTime): UTC timestamp of record creation
        updated_at (DateTime): UTC timestamp of last update
        is_active (Boolean): Soft deletion flag, defaults to True
    """
    
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), 
                       onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    is_active = Column(Boolean, default=True)

Base = declarative_base(cls=CustomBase)