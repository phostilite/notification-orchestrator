# app/schemas/template.py

# Standard library imports
from datetime import datetime
from typing import Any, Dict, Optional

# Third-party imports
from pydantic import BaseModel, Field, UUID4

# Local application imports
from .base import BaseSchema

class TemplateBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=1)
    variables: Dict[str, Any] = Field(default_factory=dict)
    channel: str
    description: Optional[str] = None

class TemplateCreate(TemplateBase):
    pass

class TemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    content: Optional[str] = Field(None, min_length=1)
    variables: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
    version: Optional[int] = None
    channel: Optional[str] = None

class TemplateResponse(TemplateBase):
    id: UUID4
    version: int
    created_at: datetime
    updated_at: datetime