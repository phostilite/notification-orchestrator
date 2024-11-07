# app/services/notification_service.py
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging
from sqlalchemy.orm import Session
from app.models.notification import Notification
from app.models.user import User
from app.models.template import NotificationTemplate
from app.models.delivery_status import DeliveryStatus
from app.schemas.notification import NotificationCreate, NotificationUpdate
from app.services.senders.factory import NotificationSenderFactory
from app.core.celery_app import celery_app

logger = logging.getLogger(__name__)

class NotificationService:
    @staticmethod
    async def create_notification(
        db: Session,
        user_id: str,
        template_id: str,
        channel: str,
        variables: Dict[str, Any],
        scheduled_for: Optional[datetime] = None,
        priority: int = 1
    ) -> Notification:
        # Get template and validate variables
        template = db.query(NotificationTemplate).filter(
            NotificationTemplate.id == template_id
        ).first()
        if not template:
            raise ValueError("Template not found")

        # Validate user preferences
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")

        # Generate content from template
        content = template.content
        for key, value in variables.items():
            content = content.replace(f"{{{key}}}", str(value))

        # Create notification
        notification = Notification(
            user_id=user_id,
            template_id=template_id,
            channel=channel,
            content=content,
            variables=variables,
            priority=priority,
            scheduled_for=scheduled_for,
            status='pending'
        )
        
        db.add(notification)
        db.commit()
        db.refresh(notification)

        # If not scheduled, send immediately
        if not scheduled_for:
            celery_app.send_task(
                "app.tasks.send_notification",
                args=[str(notification.id)]
            )

        return notification

    @staticmethod
    async def send_notification(db: Session, notification_id: str) -> bool:
        notification = db.query(Notification).filter(
            Notification.id == notification_id
        ).first()
        
        if not notification:
            raise ValueError("Notification not found")

        try:
            # Get appropriate sender service based on channel
            sender = NotificationSenderFactory.get_sender(notification.channel)
            
            # Attempt to send
            result = await sender.send(notification)
            
            # Record delivery status
            delivery_status = DeliveryStatus(
                notification_id=notification.id,
                attempt_number=notification.retry_count + 1,
                status='success' if result.success else 'failed',
                provider_response=result.response,
                error_code=result.error_code,
                error_message=result.error_message,
                delivered_at=datetime.utcnow() if result.success else None
            )
            
            db.add(delivery_status)
            
            # Update notification status
            if result.success:
                notification.status = 'sent'
                notification.sent_at = datetime.utcnow()
            else:
                if notification.retry_count >= notification.max_retries:
                    notification.status = 'failed'
                else:
                    notification.retry_count += 1
                    # Schedule retry with exponential backoff
                    retry_delay = 2 ** notification.retry_count * 60  # minutes
                    celery_app.send_task(
                        "app.tasks.send_notification",
                        args=[str(notification.id)],
                        countdown=retry_delay
                    )
            
            db.commit()
            return result.success
            
        except Exception as e:
            logger.error(f"Error sending notification {notification_id}: {str(e)}")
            notification.status = 'failed'
            notification.error_message = str(e)
            db.commit()
            return False

    @staticmethod
    async def get_user_notifications(
        db: Session,
        user_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Notification]:
        return db.query(Notification).filter(
            Notification.user_id == user_id
        ).order_by(
            Notification.created_at.desc()
        ).offset(skip).limit(limit).all()

    @staticmethod
    async def cancel_notification(db: Session, notification_id: str) -> bool:
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.status == 'pending'
        ).first()
        
        if not notification:
            return False

        notification.status = 'cancelled'
        db.commit()
        return True