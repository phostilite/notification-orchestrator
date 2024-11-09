# app/services/senders/factory.py

# Local application imports
from app.services.senders.base import NotificationSender
from app.services.senders.email_sender import EmailSender
from app.services.senders.push_sender import PushSender
from app.services.senders.sms_sender import SMSSender


class NotificationSenderFactory:
    """
    Factory class for creating notification sender instances based on channel type.
    Implements the Factory Pattern for notification sender creation.
    """

    @staticmethod
    def get_sender(channel: str) -> NotificationSender:
        """
        Create and return a notification sender instance for the specified channel.

        Args:
            channel (str): The notification channel type ('email', 'sms', or 'push')

        Returns:
            NotificationSender: An instance of the appropriate sender class

        Raises:
            ValueError: If the specified channel is not supported
        """
        senders = {
            'email': EmailSender(),
            'sms': SMSSender(),
            'push': PushSender()
        }
        
        sender = senders.get(channel.lower())
        if not sender:
            raise ValueError(f"Unsupported channel: {channel}")
            
        return sender