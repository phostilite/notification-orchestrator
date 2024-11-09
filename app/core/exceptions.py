# app/core/exceptions.py

# Third-party imports
from typing import Any, Dict

class NotificationError(Exception):
    """Base exception for notification-related errors"""
    def __init__(self, message: str, details: Dict[str, Any] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

class TemplateRenderError(NotificationError):
    """Raised when template rendering fails"""
    pass

class DeliveryError(NotificationError):
    """Raised when notification delivery fails"""
    pass

class InvalidScheduleError(NotificationError):
    """Raised when notification scheduling is invalid"""
    pass