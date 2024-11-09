# app/api/v1/endpoints/notifications.py

# Standard library imports
from datetime import datetime
from typing import List, Optional
from uuid import UUID

# Third-party imports
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
import pytz
from sqlalchemy.orm import Session

# Local application imports
from app.core.auth import get_current_user, require_admin
from app.core.exceptions import InvalidScheduleError
from app.core.logging_config import logger
from app.db.session import get_db
from app.models.delivery_status import DeliveryStatus
from app.models.notification import Notification
from app.models.template import NotificationTemplate
from app.models.user import User
from app.models.user_preference import UserPreference
from app.schemas.common import APIResponse
from app.schemas.notification import (
    DeliveryStatusResponse,
    NotificationCreate,
    NotificationDetails,
    NotificationResponse,
    NotificationUpdate,
)

# Router initialization
router = APIRouter()

@router.post("/", response_model=APIResponse[NotificationResponse], status_code=status.HTTP_201_CREATED)
async def create_notification(
    *,
    db: Session = Depends(get_db),
    notification: NotificationCreate,
    current_user: User = Depends(require_admin)
):
    """Create a new notification. Only admins can create notifications."""
    log = logger.bind(
        user_id=str(current_user.id),
        template_id=str(notification.template_id)
    )
    log.info("creating_notification")

    try:
        # Validate template
        template = db.query(NotificationTemplate).filter(
            NotificationTemplate.id == notification.template_id
        ).first()
        if not template:
            log.error("template_not_found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )

        # Validate target user
        target_user = db.query(User).filter(User.id == notification.user_id).first()
        if not target_user:
            log.error("target_user_not_found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target user not found"
            )

        # Check user's notification preferences
        user_preferences = db.query(UserPreference).filter(
            UserPreference.user_id == notification.user_id,
            UserPreference.channel == notification.channel
        ).first()

        if user_preferences and not user_preferences.enabled:
            log.warning("notification_channel_disabled_for_user",
                channel=notification.channel
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User has disabled {notification.channel} notifications"
            )

        # Get user's timezone, fallback to UTC
        user_timezone = target_user.default_timezone or "UTC"
        try:
            user_tz = pytz.timezone(user_timezone)
        except pytz.exceptions.UnknownTimeZoneError as e:
            log.error("invalid_timezone", timezone=user_timezone)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid timezone: {user_timezone}"
            )

        # Validate and convert scheduled_for time
        try:
            if notification.scheduled_for:
                if notification.scheduled_for.tzinfo is not None:
                    scheduled_for_utc = notification.scheduled_for.astimezone(pytz.UTC)
                else:
                    local_dt = user_tz.localize(notification.scheduled_for)
                    scheduled_for_utc = local_dt.astimezone(pytz.UTC)

                # Check if scheduled time is in the past
                if scheduled_for_utc < datetime.now(pytz.UTC):
                    log.warning("past_schedule_attempted", 
                        scheduled_for=scheduled_for_utc.isoformat()
                    )
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Cannot schedule notifications in the past. Please provide a future date and time."
                    )
            else:
                scheduled_for_utc = datetime.now(pytz.UTC)

        except ValueError as e:
            log.error("invalid_datetime", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid datetime format: {str(e)}"
            )

        # Render template content
        try:
            rendered_content = template.render(notification.variables)
        except Exception as e:
            log.error("template_render_error", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Template rendering error: {str(e)}"
            )

        # Create notification
        db_notification = Notification(
            user_id=notification.user_id,
            template_id=notification.template_id,
            channel=notification.channel,
            variables=notification.variables,
            priority=notification.priority,
            scheduled_for=scheduled_for_utc,
            timezone=user_timezone,
            content=rendered_content,
            status="pending"
        )
        
        try:
            db.add(db_notification)
            db.commit()
            db.refresh(db_notification)
        except Exception as e:
            log.error("database_error", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save notification"
            )

        log.info("notification_created_successfully",
            notification_id=str(db_notification.id),
            scheduled_for=str(scheduled_for_utc)
        )

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
        log.error("error_creating_notification", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating notification: {str(e)}"
        )
    
@router.get("/{notification_id}", response_model=APIResponse[NotificationDetails])
async def get_notification(
    notification_id: UUID = Path(..., title="The ID of the notification to get"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get details of a specific notification."""
    try:
        notification = db.query(Notification).filter(Notification.id == notification_id).first()
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        # Check if user has access to this notification
        if not current_user.is_admin and notification.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this notification"
            )
        
        # Convert UTC times to user's timezone for response
        user_tz = pytz.timezone(notification.timezone or 'UTC')
        notification_dict = notification.__dict__.copy()
        
        if notification.scheduled_for:
            notification_dict['scheduled_for'] = notification.scheduled_for.astimezone(user_tz)
        if notification.sent_at:
            notification_dict['sent_at'] = notification.sent_at.astimezone(user_tz)
            
        return APIResponse(
            status="success",
            data=notification_dict,
            message="Notification details retrieved successfully"
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error retrieving notification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving notification"
        )
    

@router.put("/{notification_id}", response_model=APIResponse[NotificationResponse])
async def update_notification(
    notification_id: UUID = Path(..., title="The ID of the notification to update"),
    notification_update: NotificationUpdate = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update a notification if it hasn't been sent yet. Only admins can update notifications."""
    try:
        db_notification = db.query(Notification).filter(Notification.id == notification_id).first()
        
        if not db_notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
            
        if db_notification.status == "sent":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot update a notification that has already been sent"
            )

        # Update notification fields
        update_data = notification_update.dict(exclude_unset=True)
        
        if 'template_id' in update_data:
            template = db.query(NotificationTemplate).filter(
                NotificationTemplate.id == update_data['template_id']
            ).first()
            if not template:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Template not found"
                )
            # Re-render content with new template and variables
            variables = update_data.get('variables', db_notification.variables)
            update_data['content'] = template.render(variables)

        if 'scheduled_for' in update_data:
            # Convert to UTC for storage
            user_tz = pytz.timezone(db_notification.timezone or 'UTC')
            scheduled_for = update_data['scheduled_for']
            if scheduled_for.tzinfo is not None:
                update_data['scheduled_for'] = scheduled_for.astimezone(pytz.UTC)
            else:
                local_dt = user_tz.localize(scheduled_for)
                update_data['scheduled_for'] = local_dt.astimezone(pytz.UTC)

        for key, value in update_data.items():
            setattr(db_notification, key, value)

        db.commit()
        db.refresh(db_notification)

        # Convert times to user's timezone for response
        response_notification = db_notification.__dict__.copy()
        user_tz = pytz.timezone(db_notification.timezone or 'UTC')
        if db_notification.scheduled_for:
            response_notification['scheduled_for'] = db_notification.scheduled_for.astimezone(user_tz)
        if db_notification.sent_at:
            response_notification['sent_at'] = db_notification.sent_at.astimezone(user_tz)

        return APIResponse(
            status="success",
            data=response_notification,
            message="Notification updated successfully"
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error updating notification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating notification"
        )
    

@router.delete("/{notification_id}", response_model=APIResponse)
async def delete_notification(
    notification_id: UUID = Path(..., title="The ID of the notification to delete"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete a notification if it hasn't been sent yet. Only admins can delete notifications."""
    try:
        notification = db.query(Notification).filter(Notification.id == notification_id).first()
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
            
        if notification.status == "sent":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete a notification that has already been sent"
            )
            
        db.delete(notification)
        db.commit()
        
        return APIResponse(
            status="success",
            data=None,
            message="Notification deleted successfully"
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error deleting notification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting notification"
        )
    

@router.get("/", response_model=APIResponse[List[NotificationResponse]])
async def list_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None, description="Filter by notification status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List notifications with pagination and optional status filter."""
    try:
        query = db.query(Notification)
        
        # If not admin, only show user's notifications
        if not current_user.is_admin:
            query = query.filter(Notification.user_id == current_user.id)
            
        # Apply status filter if provided
        if status:
            query = query.filter(Notification.status == status)
            
        # Apply pagination
        query = query.offset(skip).limit(limit)
        notifications = query.all()
        
        # Convert times to user timezones
        response_notifications = []
        for notification in notifications:
            notification_dict = notification.__dict__.copy()
            user_tz = pytz.timezone(notification.timezone or 'UTC')
            
            if notification.scheduled_for:
                notification_dict['scheduled_for'] = notification.scheduled_for.astimezone(user_tz)
            if notification.sent_at:
                notification_dict['sent_at'] = notification.sent_at.astimezone(user_tz)
                
            response_notifications.append(notification_dict)
            
        return APIResponse(
            status="success",
            data=response_notifications,
            message=f"Retrieved {len(notifications)} notifications"
        )
        
    except Exception as e:
        logger.error(f"Error listing notifications: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error listing notifications"
        )
    


@router.get("/{notification_id}/delivery-status", response_model=APIResponse[List[DeliveryStatusResponse]])
async def get_notification_delivery_status(
    notification_id: UUID = Path(..., title="The ID of the notification to get delivery status for"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get delivery status history for a specific notification."""
    try:
        # First get the notification to check permissions
        notification = db.query(Notification).filter(Notification.id == notification_id).first()
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        # Check if user has access to this notification
        if not current_user.is_admin and notification.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this notification"
            )
        
        # Get all delivery statuses for the notification
        delivery_statuses = (
            db.query(DeliveryStatus)
            .filter(DeliveryStatus.notification_id == notification_id)
            .order_by(DeliveryStatus.attempt_number)
            .all()
        )
        
        # Convert to response model
        delivery_status_responses = []
        user_tz = pytz.timezone(notification.timezone or 'UTC')
        
        for status in delivery_statuses:
            status_dict = status.__dict__.copy()
            
            # Convert timestamps to user timezone
            if status.delivered_at:
                status_dict['delivered_at'] = status.delivered_at.astimezone(user_tz)
            if status.created_at:
                status_dict['created_at'] = status.created_at.astimezone(user_tz)
                
            delivery_status_responses.append(status_dict)

        return APIResponse(
            status="success",
            data=delivery_status_responses,
            message=f"Retrieved {len(delivery_statuses)} delivery status records"
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error retrieving delivery status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving delivery status"
        )