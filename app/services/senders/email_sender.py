# app/services/senders/email_sender.py

# Standard library imports
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from typing import Dict, Any

# Third-party imports
import aiosmtplib

# Local application imports
from app.core.config import settings
from .base import NotificationSender, SendResult


class EmailSender(NotificationSender):
    """
    Email notification sender implementation using SMTP.
    Handles email composition and sending via SMTP server.
    """

    def send(self, notification) -> SendResult:
        """
        Send an email notification.

        Args:
            notification: Notification object containing template, user and content

        Returns:
            SendResult: Result of the email sending operation
        """
        try:
            message = MIMEMultipart('alternative')
            message['Subject'] = notification.template.name
            message['From'] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
            message['To'] = notification.user.email

            html_content = MIMEText(notification.content, 'html')
            message.attach(html_content)

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