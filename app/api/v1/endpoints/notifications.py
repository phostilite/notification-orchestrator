# Modified app/api/v1/endpoints/notifications.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.notification import NotificationCreate, NotificationResponse
from app.models.user import User
from app.models.notification import Notification
from app.models.template import NotificationTemplate
from app.core.auth import get_current_user, require_admin
from app.core.logging import logger
from datetime import datetime
import pytz
from app.schemas.common import APIResponse

router = APIRouter()

@router.post("/", response_model=APIResponse[NotificationResponse], status_code=status.HTTP_201_CREATED)
async def create_notification(
    *,
    db: Session = Depends(get_db),
    notification: NotificationCreate,
    current_user: User = Depends(require_admin)
):
    """Create a new notification. Only admins can create notifications."""
    try:
        template = db.query(NotificationTemplate).filter(
            NotificationTemplate.id == notification.template_id
        ).first()
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )

        target_user = db.query(User).filter(User.id == notification.user_id).first()
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target user not found"
            )

        # Get user's timezone, fallback to UTC
        user_timezone = target_user.default_timezone or "UTC"
        user_tz = pytz.timezone(user_timezone)

        # Convert scheduled_for to UTC for storage
        if notification.scheduled_for:
            # If datetime has timezone info, convert to UTC
            if notification.scheduled_for.tzinfo is not None:
                scheduled_for_utc = notification.scheduled_for.astimezone(pytz.UTC)
            else:
                # If naive datetime, assume it's in user's timezone and convert to UTC
                local_dt = user_tz.localize(notification.scheduled_for)
                scheduled_for_utc = local_dt.astimezone(pytz.UTC)
        else:
            # Use current time in UTC
            scheduled_for_utc = datetime.now(pytz.UTC)

        # Create notification
        db_notification = Notification(
            user_id=notification.user_id,
            template_id=notification.template_id,
            channel=notification.channel,
            variables=notification.variables,
            priority=notification.priority,
            scheduled_for=scheduled_for_utc,
            timezone=user_timezone,
            content=template.render(notification.variables),
            status="pending"
        )
        
        db.add(db_notification)
        db.commit()
        db.refresh(db_notification)

        # Convert scheduled_for back to user's timezone for response
        response_notification = db_notification.__dict__.copy()
        response_notification['scheduled_for'] = db_notification.scheduled_for.astimezone(user_tz)

        return APIResponse(
            status="success",
            data=response_notification,
            message="Notification created and scheduled successfully"
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error creating notification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating notification"
        )