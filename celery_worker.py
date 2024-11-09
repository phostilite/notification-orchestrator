# celery_worker.py (create in root directory)
import os
from app.core.celery import celery_app
from app.tasks.notifications import send_notification, schedule_pending_notifications

# Add periodic task to check pending notifications
celery_app.conf.beat_schedule = {
    'check-pending-notifications': {
        'task': 'schedule_pending_notifications',
        'schedule': 60.0,  # Run every minute
    },
}