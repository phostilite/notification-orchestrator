from typing import Optional, List
from pydantic import BaseModel, EmailStr, UUID4, Field
from app.schemas.base import BaseSchema
from app.schemas.preference import PreferenceResponse

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

class UserResponse(UserBase):
    id: UUID4
    is_verified: bool
    preferences: List[PreferenceResponse]

class Token(BaseModel):
    access_token: str
    token_type: str