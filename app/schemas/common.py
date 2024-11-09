#app/schemas/common.py

# Standard library imports
from datetime import datetime, time
from typing import Generic, List, Optional, TypeVar, Union
from uuid import UUID

# Third-party imports
from pydantic import BaseModel

# Type variable for generic response
T = TypeVar('T')

class APIResponse(BaseModel, Generic[T]):
    """
    Standard API response wrapper model that provides a consistent response format.

    Attributes:
        status (str): Response status (e.g. 'success', 'error')
        data (Optional[T]): Generic response data payload
        message (str): Human readable response message
    """
    status: str
    data: Optional[T] = None
    message: str