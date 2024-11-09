# app/tasks/notifications.py
from celery import Task
from celery.exceptions import MaxRetriesExceededError
from datetime import datetime
import pytz
from app.db.session import SessionLocal
from app.schemas.notification import NotificationStatus
from app.models import Notification, DeliveryStatus
from app.services.senders.factory import NotificationSenderFactory
from app.core.celery import celery_app
from app.core.exceptions import DeliveryError
from app.core.logging_config import logger

# app/tasks/notifications.py
class BaseNotificationTask(Task):
    abstract = True
    max_retries = 3
    autoretry_for = (DeliveryError,)
    retry_backoff = False  # Disable exponential backoff
    retry_jitter = False   # Disable jitter

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        with SessionLocal() as db:
            notification_id = args[0]
            notification = db.query(Notification).filter(Notification.id == notification_id).first()
            
            if notification:
                delivery_status = DeliveryStatus(
                    notification_id=notification_id,
                    attempt_number=notification.retry_count + 1,
                    status="failed",
                    error_message=str(exc),
                    error_code=getattr(exc, 'error_code', None),
                    provider_response=getattr(exc, 'details', {})
                )
                db.add(delivery_status)
                
                notification.retry_count += 1
                notification.error_message = str(exc)
                
                if isinstance(exc, MaxRetriesExceededError) or notification.retry_count >= self.max_retries:
                    notification.status = NotificationStatus.FAILED_PERMANENT
                else:
                    notification.status = NotificationStatus.FAILED
                    # Retry with fixed 10 second delay
                    self.retry(exc=exc, countdown=10)
                    
                db.commit()
                
        logger.error("notification_task_failed",
            notification_id=notification_id,
            error=str(exc),
            traceback=str(einfo)
        )

@celery_app.task(base=BaseNotificationTask, name="send_notification")
def send_notification(notification_id: str):
    """Send a single notification"""
    log = logger.bind(task="send_notification", notification_id=notification_id)
    
    with SessionLocal() as db:
        try:
            notification = (db.query(Notification)
                          .filter(Notification.id == notification_id)
                          .with_for_update(skip_locked=True)
                          .first())

            if not notification or notification.status in [
                NotificationStatus.SENT,
                NotificationStatus.FAILED_PERMANENT
            ]:
                return False

            notification.status = NotificationStatus.PROCESSING
            db.commit()

            delivery_status = DeliveryStatus(
                notification_id=notification_id,
                attempt_number=notification.retry_count + 1,
                status="processing"
            )
            db.add(delivery_status)
            db.commit()

            try:
                sender = NotificationSenderFactory.get_sender(notification.channel)
                result = sender.send(notification)

                if result.success:
                    notification.status = NotificationStatus.SENT
                    notification.sent_at = datetime.now(pytz.UTC)
                    delivery_status.status = "delivered"
                    delivery_status.delivered_at = notification.sent_at
                    delivery_status.provider_response = result.response
                    log.info("notification_delivered_successfully")
                else:
                    raise DeliveryError(
                        message=result.error_message,
                        details={
                            "error_code": result.error_code,
                            "channel": notification.channel,
                            "provider_response": result.response
                        }
                    )

            except Exception as e:
                notification.retry_count += 1
                delivery_status.status = "failed"
                delivery_status.error_message = str(e)
                
                if isinstance(e, MaxRetriesExceededError) or notification.retry_count >= notification.max_retries:
                    notification.status = NotificationStatus.FAILED_PERMANENT
                else:
                    notification.status = NotificationStatus.FAILED
                    
                raise

            finally:
                db.commit()

        except Exception as e:
            db.rollback()
            log.error("notification_delivery_failed",
                error=str(e),
                retry_count=notification.retry_count if notification else 0,
                channel=notification.channel if notification else None
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
            pending_notifications = (
                db.query(Notification)
                .filter(
                    Notification.status == NotificationStatus.PENDING,
                    Notification.scheduled_for <= now,
                    Notification.retry_count < Notification.max_retries
                )
                .with_for_update(skip_locked=True)
                .limit(100)  # Process in batches
                .all()
            )

            scheduled_count = 0
            for notification in pending_notifications:
                try:
                    send_notification.apply_async(
                        args=[str(notification.id)],
                        priority=notification.priority
                    )
                    scheduled_count += 1
                except Exception as e:
                    log.error("notification_scheduling_failed",
                        notification_id=notification.id,
                        error=str(e)
                    )

            log.info("notifications_scheduled",
                count=scheduled_count,
                total_pending=len(pending_notifications)
            )

        except Exception as e:
            db.rollback()
            log.error("notification_scheduling_failed",
                error=str(e)
            )
            raise