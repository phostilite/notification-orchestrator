from celery import Task
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.core.celery_app import celery_app
from app.services.notification_service import NotificationService
import logging
import asyncio

logger = logging.getLogger(__name__)

class DBTask(Task):
    _db = None

    @property
    def db(self) -> Session:
        if self._db is None:
            self._db = SessionLocal()
        return self._db

    def after_return(self, *args, **kwargs):
        if self._db is not None:
            self._db.close()
            self._db = None

@celery_app.task(base=DBTask, bind=True, max_retries=3)
def send_notification(self, notification_id: str):
    """
    Task to send a notification asynchronously.
    """
    async def _send_notification():
        try:
            success = await NotificationService.send_notification(
                db=self.db,
                notification_id=notification_id
            )
            
            if not success and self.request.retries < self.max_retries:
                raise self.retry(
                    exc=Exception("Failed to send notification"),
                    countdown=2 ** self.request.retries * 60  # exponential backoff
                )
                
            return success
            
        except Exception as e:
            logger.error(f"Error processing notification {notification_id}: {str(e)}")
            raise

    return asyncio.run(_send_notification())

@celery_app.task(base=DBTask)
def process_scheduled_notifications():
    """
    Periodic task to check and send scheduled notifications.
    """
    db_task = DBTask()
    try:
        notifications = NotificationService.get_due_notifications(db_task.db)
        
        for notification in notifications:
            send_notification.delay(str(notification.id))
            
    except Exception as e:
        logger.error(f"Error processing scheduled notifications: {str(e)}")
        raise
    finally:
        db_task.after_return()

# Configure periodic tasks
celery_app.conf.beat_schedule = {
    'process-scheduled-notifications': {
        'task': 'app.tasks.notifications.process_scheduled_notifications',
        'schedule': 60.0,  # every minute
    },
}