from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.models.user_preference import UserPreference
from app.core.auth import get_password_hash, verify_password
from app.core.logging_config import logger

class UserService:
    @staticmethod
    async def validate_unique_fields(
        db: Session, 
        email: Optional[str] = None, 
        phone: Optional[str] = None
    ) -> None:
        """Validate email and phone uniqueness"""
        if email:
            existing_email = db.query(User).filter(User.email == email).first()
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
        
        if phone:
            existing_phone = db.query(User).filter(User.phone == phone).first()
            if existing_phone:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Phone number already registered"
                )
            
    @staticmethod
    async def create_user(db: Session, user_create: UserCreate) -> User:
        # Check if user exists
        if db.query(User).filter(User.email == user_create.email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user
        user = User(
            email=user_create.email,
            phone=user_create.phone,
            full_name=user_create.full_name,
            hashed_password=get_password_hash(user_create.password),
            is_admin=user_create.is_admin
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    async def get_user(db: Session, user_id: str) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    async def authenticate_user(
        db: Session, 
        email: str, 
        password: str
    ) -> Optional[User]:
        """Authenticate user with email and password"""
        try:
            user = db.query(User).filter(User.email == email).first()
            if not user:
                return None
            
            if not verify_password(password, user.hashed_password):
                return None
                
            return user
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return None

    @staticmethod
    async def update_user(db: Session, user_id: str, user_update: UserUpdate) -> Optional[User]:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        # Handle basic user fields
        update_data = user_update.model_dump(exclude={'preferences'}, exclude_unset=True)
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

        # Only allow admin updates from admin users
        if "is_admin" in update_data and not user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot modify admin status"
            )

        for key, value in update_data.items():
            setattr(user, key, value)

        # Handle preferences if provided
        if user_update.preferences:
            for pref_update in user_update.preferences:
                db_preference = db.query(UserPreference).filter(
                    UserPreference.user_id == user_id,
                    UserPreference.channel == pref_update.channel
                ).first()

                if not db_preference:
                    # Create new preference if doesn't exist
                    db_preference = UserPreference(
                        user_id=user_id,
                        channel=pref_update.channel
                    )
                    db.add(db_preference)

                # Update preference fields
                pref_data = pref_update.model_dump(exclude={'channel'}, exclude_unset=True)
                for key, value in pref_data.items():
                    setattr(db_preference, key, value)

        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    async def delete_user(db: Session, user_id: str) -> bool:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        db.delete(user)
        db.commit()
        return True