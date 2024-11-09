# app/schemas/base.py

# Standard library imports
from datetime import datetime, time
from typing import Optional

# Third-party imports
from pydantic import BaseModel, UUID4

class BaseSchema(BaseModel):
    """
    Base Pydantic schema class that provides common configuration and functionality
    for all schema classes in the application.
    
    Features:
    - ORM mode enabled for SQLAlchemy model parsing
    - Population by field name allowed
    - Custom JSON encoder for time objects (HH:MM format)
    """
    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        json_encoders = {
            time: lambda v: v.strftime('%H:%M') if v else None
        }