from typing import Dict, Any
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
from .base import NotificationSender, SendResult

class EmailSender(NotificationSender):
    async def send(self, notification) -> SendResult:
        try:
            # Create message container
            message = MIMEMultipart('alternative')
            message['Subject'] = notification.template.name
            message['From'] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
            message['To'] = notification.user.email

            # Create HTML content
            html_content = MIMEText(notification.content, 'html')
            message.attach(html_content)

            # Connect and send email
            await aiosmtplib.send(
                message,
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                username=settings.SMTP_USER,
                password=settings.SMTP_PASSWORD,
                use_tls=settings.SMTP_TLS
            )

            return SendResult(
                success=True,
                response={"message": "Email sent successfully"}
            )

        except Exception as e:
            return SendResult(
                success=False,
                error_code="SMTP_ERROR",
                error_message=str(e)
            )