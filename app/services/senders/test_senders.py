from twilio.rest import Client
import os
import asyncio
from dotenv import load_dotenv
from app.core.config import settings
from app.models.notification import Notification  # Assuming you have this model
from app.db.session import get_db  # Assuming you have database session
from email_sender import EmailSender

async def get_notification_by_id(notification_id: int) -> Notification:
    db = next(get_db())
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    return notification

async def send_test_email(notification_id: int):
    # Load environment variables
    load_dotenv()
    
    try:
        # Get notification data
        notification = await get_notification_by_id(notification_id)
        if not notification:
            print(f"Notification with ID {notification_id} not found")
            return

        # Initialize email sender
        email_sender = EmailSender()
        
        # Send email
        result = await email_sender.send(notification)
        
        if result.success:
            print("Email sent successfully!")
            print(f"Response: {result.response}")
        else:
            print(f"Failed to send email: {result.error_message}")
            print(f"Error code: {result.error_code}")
            
    except Exception as e:
        print(f"Error sending email: {e}")

def send_test_sms():
    # Previous SMS code remains unchanged
    ...

async def main():
    notification_id = "dcdd1ea5-8255-4ffe-aea1-dfe5f2d9e45d"
    await send_test_email(notification_id)

if __name__ == "__main__":
    asyncio.run(main())