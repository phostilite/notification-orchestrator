# app/services/senders/sms_sender.py

# Standard library imports
from typing import Dict, Any

# Third-party imports
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

# Local application imports
from app.core.config import settings
from .base import NotificationSender, SendResult


class SMSSender(NotificationSender):
    """
    SMS notification sender implementation using Twilio.
    Handles sending SMS messages via Twilio API.
    """

    def __init__(self):
        """Initialize Twilio client with credentials from settings."""
        self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    def send(self, notification) -> SendResult:
        """
        Send an SMS notification.

        Args:
            notification: Notification object containing user phone and content

        Returns:
            SendResult: Result of the SMS sending operation with Twilio response details
        """
        try:
            message = self.client.messages.create(
                body=notification.content,
                from_=settings.TWILIO_FROM_NUMBER,
                to=notification.user.phone
            )

            return SendResult(
                success=True,
                response={
                    "message_sid": message.sid,
                    "status": message.status
                }
            )
        except TwilioRestException as e:
            return SendResult(
                success=False,
                error_code=str(e.code),
                error_message=str(e.msg),
                response={"twilio_error": str(e)}
            )
        except Exception as e:
            return SendResult(
                success=False,
                error_code="INTERNAL_ERROR",
                error_message=str(e)
            )