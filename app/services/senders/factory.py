# app/services/senders/factory.py
from app.services.senders.base import NotificationSender
from app.services.senders.email_sender import EmailSender
from app.services.senders.sms_sender import SMSSender
from app.services.senders.push_sender import PushSender

class NotificationSenderFactory:
    @staticmethod
    def get_sender(channel: str) -> NotificationSender:
        senders = {
            'email': EmailSender(),
            'sms': SMSSender(),
            'push': PushSender()
        }
        
        sender = senders.get(channel.lower())
        if not sender:
            raise ValueError(f"Unsupported channel: {channel}")
            
        return sender