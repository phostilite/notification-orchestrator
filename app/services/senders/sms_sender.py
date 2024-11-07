from typing import Dict, Any
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from app.core.config import settings
from .base import NotificationSender, SendResult

class SMSSender(NotificationSender):
    def __init__(self):
        self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    async def send(self, notification) -> SendResult:
        try:
            message = await self.client.messages.create(
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