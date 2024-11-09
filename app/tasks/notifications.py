# app/tasks/notifications.py
from celery import Task
from celery.exceptions import MaxRetriesExceededError
from datetime import datetime, timedelta
import pytz
from app.core.celery import celery_app
from app.db.session import SessionLocal
from app.models.notification import Notification
from app.models.delivery_status import DeliveryStatus
from app.services.senders.factory import NotificationSenderFactory
from app.core.logging_config import logger
from app.core.exceptions import NotificationError, DeliveryError

class BaseNotificationTask(Task):
    autoretry_for = (Exception,)
    max_retries = 3
    retry_backoff = True
    retry_backoff_max = 600  # Maximum delay between retries (10 minutes)
    retry_jitter = True     # Add randomness to retry delays

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        with SessionLocal() as db:
            notification_id = args[0]
            notification = db.query(Notification).filter(Notification.id == notification_id).first()
            
            if notification:
                # Create delivery status record
                delivery_status = DeliveryStatus(
                    notification_id=notification_id,
                    status="failed",
                    error_message=str(exc),
                    attempt_number=notification.retry_count + 1,
                    metadata={
                        "task_id": task_id,
                        "error_type": type(exc).__name__,
                        "traceback": str(einfo)
                    }
                )
                db.add(delivery_status)

                # Update notification status
                notification.status = "failed"
                notification.error_message = str(exc)
                notification.retry_count += 1
                
                if isinstance(exc, MaxRetriesExceededError):
                    notification.status = "failed_permanent"
                    logger.error("notification_max_retries_exceeded", 
                        notification_id=notification_id,
                        error=str(exc),
                        retry_count=notification.retry_count
                    )
                
                db.commit()
                
        logger.error("notification_task_failed",
            notification_id=notification_id,
            task_id=task_id,
            error=str(exc),
            traceback=str(einfo)
        )
        
        super().on_failure(exc, task_id, args, kwargs, einfo)

@celery_app.task(base=BaseNotificationTask, name="send_notification")
def send_notification(notification_id: str):
    log = logger.bind(notification_id=notification_id)
    log.info("starting_notification_delivery")
    
    with SessionLocal() as db:
        notification = db.query(Notification).filter(Notification.id == notification_id).first()
        if not notification:
            log.error("notification_not_found")
            return

        try:
            # Create delivery status record for attempt
            delivery_status = DeliveryStatus(
                notification_id=notification_id,
                status="processing",
                attempt_number=notification.retry_count + 1
            )
            db.add(delivery_status)
            db.commit()

            sender = NotificationSenderFactory.get_sender(notification.channel)
            result = sender.send(notification)

            if result.success:
                notification.status = "sent"
                notification.sent_at = datetime.now(pytz.UTC)
                delivery_status.status = "delivered"
                delivery_status.sent_at = notification.sent_at
                log.info("notification_delivered_successfully")
            else:
                raise DeliveryError(
                    message=result.error_message,
                    details={
                        "error_code": result.error_code,
                        "channel": notification.channel
                    }
                )

            db.commit()
            return result.success

        except Exception as e:
            db.rollback()
            notification.retry_count += 1
            delivery_status.status = "failed"
            delivery_status.error_message = str(e)
            db.commit()

            log.error("notification_delivery_failed",
                error=str(e),
                retry_count=notification.retry_count,
                channel=notification.channel
            )
            raise

@celery_app.task(name="schedule_pending_notifications")
def schedule_pending_notifications():
    """Periodic task to check and schedule pending notifications"""
    log = logger.bind(task="schedule_pending_notifications")
    log.info("checking_pending_notifications")
    
    with SessionLocal() as db:
        now = datetime.now(pytz.UTC)
        
        try:
            # Get pending notifications that are due and haven't exceeded retry limit
            pending_notifications = db.query(Notification).filter(
                Notification.status == "pending",
                Notification.scheduled_for <= now,
                Notification.retry_count < Notification.max_retries
            ).all()

            scheduled_count = 0
            for notification in pending_notifications:
                try:
                    send_notification.apply_async(
                        args=[str(notification.id)],
                        priority=notification.priority
                    )
                    scheduled_count += 1
                except Exception as e:
                    log.error("error_scheduling_notification",
                        notification_id=str(notification.id),
                        error=str(e)
                    )

            log.info("notifications_scheduled",
                total_pending=len(pending_notifications),
                scheduled_count=scheduled_count
            )

        except Exception as e:
            log.error("error_processing_pending_notifications", error=str(e))
            raise