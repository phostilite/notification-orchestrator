# tests/test_email_sender.py

# Standard library imports
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch

# Third-party imports
import pytest
import pytz

# Local application imports
from app.core.config import settings
from app.services.senders.base import SendResult
from app.services.senders.email_sender import EmailSender

def test_successful_email_send(email_sender, mock_notification_for_service):
    """Test successful email sending"""
    with patch('smtplib.SMTP') as mock_smtp:
        # Setup mock SMTP instance
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        result = email_sender.send(mock_notification_for_service)

        # Verify SMTP server setup
        mock_smtp.assert_called_once_with(settings.SMTP_HOST, settings.SMTP_PORT)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with(settings.SMTP_USER, settings.SMTP_PASSWORD)
        
        # Verify email was sent
        assert mock_server.send_message.called
        assert result.success is True
        assert result.response == {"message": "Email sent successfully"}

def test_email_content_and_headers(email_sender, test_notification, test_template):
    """Test email content and headers are set correctly"""
    with patch('smtplib.SMTP') as mock_smtp:
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        email_sender.send(test_notification)

        sent_message = mock_server.send_message.call_args[0][0]
        
        assert sent_message['Subject'] == test_template.name
        assert sent_message['To'] == test_notification.user.email
        assert settings.EMAILS_FROM_EMAIL in sent_message['From']
        assert settings.EMAILS_FROM_NAME in sent_message['From']

def test_smtp_error_handling(email_sender, mock_notification_for_service):
    """Test SMTP error handling"""
    with patch('smtplib.SMTP') as mock_smtp:
        mock_smtp.return_value.__enter__.side_effect = Exception("SMTP Connection Error")

        result = email_sender.send(mock_notification_for_service)

        assert result.success is False
        assert result.error_code == "SMTP_ERROR"
        assert "SMTP Connection Error" in result.error_message

def test_login_error_handling(email_sender, mock_notification_for_service):
    """Test SMTP login error handling"""
    with patch('smtplib.SMTP') as mock_smtp:
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        mock_server.login.side_effect = Exception("Authentication failed")

        result = email_sender.send(mock_notification_for_service)

        assert result.success is False
        assert result.error_code == "SMTP_ERROR"
        assert "Authentication failed" in result.error_message

def test_send_message_error_handling(email_sender, mock_notification_for_service):
    """Test send message error handling"""
    with patch('smtplib.SMTP') as mock_smtp:
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        mock_server.send_message.side_effect = Exception("Failed to send")

        result = email_sender.send(mock_notification_for_service)

        assert result.success is False
        assert result.error_code == "SMTP_ERROR"
        assert "Failed to send" in result.error_message