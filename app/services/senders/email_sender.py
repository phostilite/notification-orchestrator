from typing import Dict, Any
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
from .base import NotificationSender, SendResult

# app/services/senders/email_sender.py
class EmailSender(NotificationSender):
    def send(self, notification) -> SendResult:  # Remove async
        try:
            message = MIMEMultipart('alternative')
            message['Subject'] = notification.template.name
            message['From'] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
            message['To'] = notification.user.email

            html_content = MIMEText(notification.content, 'html')
            message.attach(html_content)

            # Use synchronous SMTP instead of aiosmtplib
            import smtplib
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(message)

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

