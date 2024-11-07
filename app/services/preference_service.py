from sqlalchemy.orm import Session
from app.models.user_preference import UserPreference
from app.schemas.preference import PreferenceCreate, PreferenceUpdate

class PreferenceService:
    @staticmethod
    async def get_user_preferences(db: Session, user_id: str):
        return db.query(UserPreference).filter(UserPreference.user_id == user_id).all()

    @staticmethod
    async def update_preference(db: Session, user_id: str, channel: str, preference: PreferenceUpdate):
        db_preference = db.query(UserPreference).filter(
            UserPreference.user_id == user_id,
            UserPreference.channel == channel
        ).first()
        
        if not db_preference:
            raise ValueError("Preference not found")

        for key, value in preference.model_dump(exclude_unset=True).items():
            setattr(db_preference, key, value)

        db.commit()
        db.refresh(db_preference)
        return db_preference
    
    