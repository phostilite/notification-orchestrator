# app/models/base.py

# Standard library imports
from datetime import datetime, timezone
from typing import Any
import uuid

# Third-party imports
from sqlalchemy import Boolean, Column, DateTime, UUID
from sqlalchemy.ext.declarative import declared_attr, declarative_base

class CustomBase:
    """
    Base class for all database models providing common functionality.
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