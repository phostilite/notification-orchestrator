from typing import Optional, List
from pydantic import BaseModel, EmailStr, UUID4, Field
from datetime import datetime
from app.schemas.base import BaseSchema
from app.schemas.preference import PreferenceResponse, PreferenceUpdate

class UserBase(BaseSchema):
    email: EmailStr
    phone: Optional[str] = None  
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    preferences: Optional[List[PreferenceUpdate]] = None  

class UserResponse(UserBase):
    id: UUID4
    is_verified: bool
    preferences: List[PreferenceResponse]
    created_at: datetime
    updated_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str