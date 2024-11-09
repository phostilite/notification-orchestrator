# app/tasks/notifications.py
from typing import Dict, Any
from celery import Task
from datetime import datetime
import pytz
from app.core.celery import celery_app
from app.db.session import SessionLocal
from app.models.notification import Notification
from app.services.senders.factory import NotificationSenderFactory
from app.core.logging import logger

class NotificationTask(Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        with SessionLocal() as db:
            notification_id = args[0]
            notification = db.query(Notification).filter(Notification.id == notification_id).first()
            if notification:
                notification.status = "failed"
                notification.error_message = str(exc)
                notification.retry_count += 1
                db.commit()
        super().on_failure(exc, task_id, args, kwargs, einfo)

@celery_app.task(base=NotificationTask, name="send_notification")
def send_notification(notification_id: str):
    with SessionLocal() as db:
        notification = db.query(Notification).filter(Notification.id == notification_id).first()
        if not notification:
            logger.error(f"Notification {notification_id} not found")
            return

        try:
            sender = NotificationSenderFactory.get_sender(notification.channel)
            result = sender.send(notification)

            if result.success:
                notification.status = "sent"
                notification.sent_at = datetime.now(pytz.UTC)
            else:
                notification.status = "failed"
                notification.error_message = result.error_message
                notification.retry_count += 1

            db.commit()
            return result.success
        except Exception as e:
            logger.error(f"Error sending notification {notification_id}: {str(e)}")
            notification.status = "failed"
            notification.error_message = str(e)
            notification.retry_count += 1
            db.commit()
            raise

@celery_app.task(name="schedule_pending_notifications")
def schedule_pending_notifications():
    """
    Periodic task to check and schedule pending notifications
    """
    with SessionLocal() as db:
        now = datetime.now(pytz.UTC)
        pending_notifications = db.query(Notification).filter(
            Notification.status == "pending",
            Notification.scheduled_for <= now,
            Notification.retry_count < Notification.max_retries
        ).all()

        for notification in pending_notifications:
            send_notification.delay(str(notification.id))