from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.user_preference import UserPreference
from app.schemas.preference import PreferenceCreate, PreferenceUpdate
from app.schemas.notification import NotificationChannel

class PreferenceService:
    @staticmethod
    async def create_preference(db: Session, user_id: str, preference_data: PreferenceCreate) -> UserPreference:
        """Create a new preference."""
        db_preference = UserPreference(
            user_id=user_id,
            channel=preference_data.channel.value,
            enabled=preference_data.enabled,
            quiet_hours_start=preference_data.quiet_hours_start,
            quiet_hours_end=preference_data.quiet_hours_end,
            frequency_limit=preference_data.frequency_limit,
            priority_threshold=preference_data.priority_threshold
        )
        db.add(db_preference)
        db.commit()
        db.refresh(db_preference)
        return db_preference

    @staticmethod
    async def create_default_preferences(db: Session, user_id: str) -> List[UserPreference]:
        """Create default preferences for all notification channels."""
        preferences = []
        for channel in NotificationChannel:
            pref = PreferenceCreate(
                channel=channel,
                enabled=True,
                priority_threshold=1
            )
            db_pref = await PreferenceService.create_preference(db, user_id, pref)
            preferences.append(db_pref)
        return preferences

    @staticmethod
    async def get_user_preferences(db: Session, user_id: str) -> List[UserPreference]:
        """Get all preferences for a user."""
        return db.query(UserPreference).filter(UserPreference.user_id == user_id).all()

    @staticmethod
    async def get_preference(db: Session, user_id: str, channel: str) -> Optional[UserPreference]:
        """Get a specific preference by channel."""
        return db.query(UserPreference).filter(
            UserPreference.user_id == user_id,
            UserPreference.channel == channel
        ).first()

    @staticmethod
    async def update_preference(db: Session, user_id: str, channel: str, preference: PreferenceUpdate) -> Optional[UserPreference]:
        """Update a specific preference."""
        db_preference = await PreferenceService.get_preference(db, user_id, channel)
        if not db_preference:
            return None

        for key, value in preference.model_dump(exclude_unset=True).items():
            setattr(db_preference, key, value)
            
        db.commit()
        db.refresh(db_preference)
        return db_preference

    @staticmethod
    async def delete_preference(db: Session, user_id: str, channel: str) -> bool:
        """Delete a specific preference."""
        db_preference = await PreferenceService.get_preference(db, user_id, channel)
        if not db_preference:
            return False

        db.delete(db_preference)
        db.commit()
        return True