# app/api/v1/endpoints/notifications.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.notification_service import NotificationService
from app.schemas.notification import (
    NotificationCreate,
    NotificationResponse,
    NotificationList
)
from app.core.auth import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/notifications", response_model=NotificationResponse)
async def create_notification(
    *,
    db: Session = Depends(get_db),
    notification: NotificationCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new notification.
    """
    try:
        result = await NotificationService.create_notification(
            db=db,
            user_id=notification.user_id,
            template_id=notification.template_id,
            channel=notification.channel,
            variables=notification.variables,
            scheduled_for=notification.scheduled_for,
            priority=notification.priority
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/notifications", response_model=NotificationList)
async def list_notifications(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[str] = None
):
    """
    List notifications for the current user.
    """
    try:
        notifications = await NotificationService.get_user_notifications(
            db=db,
            user_id=str(current_user.id),
            skip=skip,
            limit=limit,
            status=status
        )
        return NotificationList(
            items=notifications,
            total=len(notifications),
            skip=skip,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/notifications/{notification_id}")
async def cancel_notification(
    notification_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cancel a pending notification.
    """
    try:
        success = await NotificationService.cancel_notification(
            db=db,
            notification_id=notification_id
        )
        if not success:
            raise HTTPException(
                status_code=404,
                detail="Notification not found or already processed"
            )
        return {"message": "Notification cancelled successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")