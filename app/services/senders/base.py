# app/services/senders/base.py

# Standard library imports
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional

@dataclass
class SendResult:
    """
    Represents the result of a notification sending attempt.

    Attributes:
        success (bool): Whether the send operation was successful
        response (Optional[Dict[str, Any]]): Optional response data from the sending service
        error_code (Optional[str]): Error code if send operation failed
        error_message (Optional[str]): Human readable error message if send operation failed
    """
    success: bool
    response: Optional[Dict[str, Any]] = None
    error_code: Optional[str] = None 
    error_message: Optional[str] = None

class NotificationSender(ABC):
    """
    Abstract base class for notification senders.
    All concrete notification senders must implement this interface.
    """
    @abstractmethod
    def send(self, notification) -> SendResult:
        """
        Send a notification and return the result.

        Args:
            notification: The notification to send

        Returns:
            SendResult: The result of the send operation
        """
        pass