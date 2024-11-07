from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.user_service import UserService
from app.schemas.user import UserCreate, UserUpdate, UserResponse, Token
from app.core.auth import get_current_user, create_access_token
from app.models.user import User
from app.core.config import settings
from app.core.logging import logger

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate
):
    """Register a new user"""
    try:
        # Validate unique fields before creation
        await UserService.validate_unique_fields(db=db, email=user_in.email, phone=user_in.phone)
        user = await UserService.create_user(db=db, user_create=user_in)
        logger.info(f"User registered successfully: {user.email}")
        return user
    except HTTPException as e:
        logger.warning(f"Registration validation failed: {str(e)}")
        raise e
    except IntegrityError as e:
        logger.error(f"Database integrity error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or phone already exists"
        )
    except Exception as e:
        logger.exception(f"Unexpected error during registration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred"
        )

@router.post("/login", response_model=Token)
async def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """Authenticate user and return token"""
    try:
        # Check for empty credentials
        if not form_data.username or not form_data.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email and password are required",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Try to authenticate user
        user = await UserService.authenticate_user(
            db=db,
            email=form_data.username,
            password=form_data.password
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=access_token_expires
        )
        logger.info(f"User logged in successfully: {user.email}")
        return {"access_token": access_token, "token_type": "bearer"}
        
    except HTTPException as e:
        logger.warning(f"Login attempt failed: {str(e.detail)}")
        raise e
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.get("/me", response_model=UserResponse)
async def get_user_profile(
    current_user: User = Depends(get_current_user)
):
    """Get current user profile"""
    try:
        return current_user
    except Exception as e:
        logger.error(f"Error retrieving user profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving user profile"
        )

@router.put("/me", response_model=UserResponse)
async def update_user_profile(
    *,
    db: Session = Depends(get_db),
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update current user profile"""
    try:
        # Validate unique fields if email or phone is being updated
        if user_update.email and user_update.email != current_user.email:
            await UserService.validate_unique_fields(db=db, email=user_update.email)
        if user_update.phone and user_update.phone != current_user.phone:
            await UserService.validate_unique_fields(db=db, phone=user_update.phone)

        updated_user = await UserService.update_user(
            db=db,
            user_id=str(current_user.id),
            user_update=user_update
        )
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        logger.info(f"User profile updated successfully: {updated_user.email}")
        return updated_user
    except HTTPException as e:
        logger.warning(f"Profile update validation failed: {str(e)}")
        raise e
    except IntegrityError as e:
        logger.error(f"Database integrity error during update: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or phone number already in use"
        )
    except Exception as e:
        logger.exception(f"Error updating user profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating user profile"
        )

@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_profile(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete current user account"""
    try:
        deleted = await UserService.delete_user(db=db, user_id=str(current_user.id))
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        logger.info(f"User account deleted successfully: {current_user.email}")
        return None
    except HTTPException as e:
        logger.warning(f"Account deletion failed: {str(e)}")
        raise e
    except Exception as e:
        logger.exception(f"Error deleting user account: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting user account"
        )