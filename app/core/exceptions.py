# app/core/exceptions.py
class NotificationError(Exception):
    """Base exception for notification related errors"""
    pass

class TemplateNotFoundError(NotificationError):
    """Raised when a notification template is not found"""
    pass

class UserNotFoundError(NotificationError):
    """Raised when a user is not found"""
    pass

class InvalidChannelError(NotificationError):
    """Raised when an invalid notification channel is specified"""
    pass