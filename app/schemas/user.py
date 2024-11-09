# app/schemas/user.py

# Standard library imports
from datetime import datetime
from typing import List, Optional

# Third-party imports
import pytz
from pydantic import BaseModel, ConfigDict, EmailStr, Field, UUID4, validator

# Local application imports
from app.schemas.base import BaseSchema
from app.schemas.preference import PreferenceResponse, PreferenceUpdate

class UserBase(BaseSchema):
    email: EmailStr
    phone: Optional[str] = None  
    full_name: Optional[str] = None
    is_admin: Optional[bool] = False  
    default_timezone: str = Field(default="UTC", description="User's default timezone (e.g. 'America/New_York')")

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_admin: Optional[bool] = None  
    default_timezone: Optional[str] = None
    preferences: Optional[List[PreferenceUpdate]] = None

    @validator('default_timezone')
    def validate_timezone(cls, v):
        if v is not None:
            try:
                if v not in pytz.all_timezones:
                    raise ValueError("Invalid timezone")
                return v
            except Exception:
                raise ValueError("Invalid timezone. Please provide a valid timezone like 'Asia/Kolkata' or 'America/New_York'")
        return v

class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    is_verified: bool
    preferences: List[PreferenceResponse]
    created_at: datetime
    updated_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class UserWithToken(BaseModel):
    user: UserResponse
    token: Token