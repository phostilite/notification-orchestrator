#app/schemas/common.py
from typing import Generic, TypeVar, Optional, Union, List
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime, time

T = TypeVar('T')

class APIResponse(BaseModel, Generic[T]):
    """Standard API response wrapper"""
    status: str
    data: Optional[T]
    message: str