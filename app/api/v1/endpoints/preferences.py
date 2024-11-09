# app/api/v1/endpoints/preferences.py

# Standard library imports
from typing import List

# Third-party imports
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

# Local application imports
from app.core.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.common import APIResponse
from app.schemas.preference import (
    PreferenceCreate, 
    PreferenceResponse,
    PreferenceUpdate
)
from app.services.preference_service import PreferenceService

# Router initialization
router = APIRouter()

@router.post("/", response_model=APIResponse[PreferenceResponse], status_code=status.HTTP_201_CREATED)
async def create_preference(
    *,
    db: Session = Depends(get_db),
    preference: PreferenceCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new notification preference for the authenticated user."""
    try:
        # Check if preference already exists
        existing = await PreferenceService.get_preference(
            db=db,
            user_id=str(current_user.id),
            channel=preference.channel.value
        )
        
        if existing:
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content={
                    "status": "error",
                    "data": None,
                    "message": f"Preference already exists for channel {preference.channel}"
                }
            )

        new_preference = await PreferenceService.create_preference(
            db=db,
            user_id=str(current_user.id),
            preference_data=preference
        )
        
        return APIResponse(
            status="success",
            data=new_preference,
            message="Preference created successfully"
        )
        
    except ValueError as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "status": "error",
                "data": None,
                "message": str(e)
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "error",
                "data": None,
                "message": "Internal server error"
            }
        )

@router.get("/", response_model=APIResponse[List[PreferenceResponse]])
async def get_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all notification preferences for the current user."""
    try:
        preferences = await PreferenceService.get_user_preferences(
            db=db,
            user_id=str(current_user.id)
        )
        
        return APIResponse(
            status="success",
            data=preferences,
            message="Preferences retrieved successfully"
        )
        
    except Exception as e:
        return APIResponse(
            status="error",
            data=None,
            message="Internal server error"
        )

@router.get("/{channel}", response_model=APIResponse[PreferenceResponse])
async def get_preference(
    *,
    db: Session = Depends(get_db),
    channel: str,
    current_user: User = Depends(get_current_user)
):
    """Get notification preferences for a specific channel."""
    try:
        preference = await PreferenceService.get_preference(
            db=db,
            user_id=str(current_user.id),
            channel=channel
        )
        
        if not preference:
            return APIResponse(
                status="error",
                data=None,
                message=f"No preference found for channel {channel}"
            )
            
        return APIResponse(
            status="success",
            data=preference,
            message=f"Preference for channel {channel} retrieved successfully"
        )
        
    except Exception as e:
        return APIResponse(
            status="error",
            data=None,
            message="Internal server error"
        )

@router.put("/{channel}", response_model=APIResponse[PreferenceResponse])
async def update_preference(
    *,
    db: Session = Depends(get_db),
    channel: str,
    preference: PreferenceUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update notification preferences for a specific channel."""
    try:
        updated_preference = await PreferenceService.update_preference(
            db=db,
            user_id=str(current_user.id),
            channel=channel,
            preference=preference
        )
        
        if not updated_preference:
            return APIResponse(
                status="error",
                data=None,
                message=f"No preference found for channel {channel}"
            )
            
        return APIResponse(
            status="success",
            data=updated_preference,
            message=f"Preference for channel {channel} updated successfully"
        )
        
    except ValueError as e:
        return APIResponse(
            status="error",
            data=None,
            message=str(e)
        )
    except Exception as e:
        return APIResponse(
            status="error",
            data=None,
            message="Internal server error"
        )

@router.delete("/{channel}", response_model=APIResponse[dict])
async def delete_preference(
    *,
    db: Session = Depends(get_db),
    channel: str,
    current_user: User = Depends(get_current_user)
):
    """Delete notification preferences for a specific channel."""
    try:
        deleted = await PreferenceService.delete_preference(
            db=db,
            user_id=str(current_user.id),
            channel=channel
        )
        
        if not deleted:
            return APIResponse(
                status="error",
                data=None,
                message=f"No preference found for channel {channel}"
            )
            
        return APIResponse(
            status="success",
            data={"channel": channel},
            message=f"Preference for channel {channel} deleted successfully"
        )
        
    except Exception as e:
        return APIResponse(
            status="error",
            data=None,
            message="Internal server error"
        )