# app/api/v1/endpoints/preferences.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.preference_service import PreferenceService
from app.schemas.preference import (
    PreferenceCreate,
    PreferenceUpdate,
    PreferenceResponse
)
from app.core.auth import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/preferences", response_model=List[PreferenceResponse])
async def get_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get user's notification preferences.
    """
    try:
        preferences = await PreferenceService.get_user_preferences(
            db=db,
            user_id=str(current_user.id)
        )
        return preferences
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/preferences/{channel}", response_model=PreferenceResponse)
async def update_preferences(
    *,
    db: Session = Depends(get_db),
    channel: str,
    preference: PreferenceUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update user's notification preferences for a specific channel.
    """
    try:
        updated_preference = await PreferenceService.update_preference(
            db=db,
            user_id=str(current_user.id),
            channel=channel,
            preference=preference
        )
        return updated_preference
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")