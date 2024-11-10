# app/api/v1/endpoints/users.py

# Standard library imports
from datetime import timedelta
from typing import Dict, Optional

# Third-party imports
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

# Local application imports
from app.core.auth import create_access_token, get_current_user
from app.core.config import settings
from app.core.logging_config import logger
from app.db.session import get_db
from app.models.user import User
from app.schemas.common import APIResponse
from app.schemas.user import (
    Token,
    UserCreate,
    UserResponse,
    UserUpdate,
    UserWithToken
)
from app.services.user_service import UserService

# Router initialization
router = APIRouter()

# app/api/v1/endpoints/users.py
from fastapi.responses import JSONResponse

@router.post("/register", response_model=APIResponse[UserWithToken], status_code=status.HTTP_201_CREATED)
async def register_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate
):
    """Register a new user"""
    try:
        # Validate unique fields first
        await UserService.validate_unique_fields(db=db, email=user_in.email, phone=user_in.phone)
        
        # Create user if validation passes
        user = await UserService.create_user(db=db, user_create=user_in)
        
        # Generate token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=access_token_expires
        )

        # Create response with proper model validation
        user_response = UserResponse(
            id=user.id,
            email=user.email,
            phone=user.phone,
            full_name=user.full_name,
            is_verified=user.is_verified,
            is_admin=user.is_admin,
            preferences=[],
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        
        response_data = UserWithToken(
            user=user_response,
            token=Token(
                access_token=access_token,
                token_type="bearer"
            )
        )
        
        return APIResponse(
            status="success",
            data=response_data,
            message="User registered successfully"
        )

    except HTTPException as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=APIResponse(
                status="error",
                data=None,
                message=str(e.detail)
            ).model_dump()
        )
        
    except IntegrityError as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=APIResponse(
                status="error",
                data=None,
                message="User with this email or phone already exists"
            ).model_dump()
        )
        
    except Exception as e:
        logger.exception(f"Unexpected error during registration: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=APIResponse(
                status="error",
                data=None,
                message="Internal server error occurred"
            ).model_dump()
        )

@router.post("/login", response_model=APIResponse[Token])
async def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """Authenticate user and return token"""
    try:
        if not form_data.username or not form_data.password:
            return APIResponse(
                status="error",
                data=None,
                message="Email and password are required"
            )

        user = await UserService.authenticate_user(
            db=db,
            email=form_data.username,
            password=form_data.password
        )
        
        if not user:
            return APIResponse(
                status="error",
                data=None,
                message="Invalid email or password"
            )
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=access_token_expires
        )
        logger.info(f"User logged in successfully: {user.email}")
        return APIResponse(
            status="success",
            data={"access_token": access_token, "token_type": "bearer"},
            message="Login successful"
        )
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        return APIResponse(
            status="error",
            data=None,
            message="An error occurred while processing your request"
        )

# app/api/v1/endpoints/users.py

@router.get(
    "/me",
    response_model=APIResponse[UserResponse],
    responses={
        401: {"description": "Authentication failed"},
        500: {"description": "Internal server error"}
    }
)
async def get_user_profile(
    current_user: Optional[User] = Depends(get_current_user)
) -> APIResponse[UserResponse]:
    try:
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )

        user_response = UserResponse.from_orm(current_user)
        return APIResponse(
            status="success",
            data=user_response,
            message="User profile retrieved successfully"
        )
    except HTTPException as he:
        logger.error(f"Authentication error: {str(he)}")
        raise he
    except Exception as e:
        logger.error(f"Error retrieving user profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving user profile"
        )

@router.put("/me", response_model=APIResponse[UserResponse])
async def update_user_profile(
    *,
    db: Session = Depends(get_db),
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update current user profile"""
    try:
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
            return APIResponse(
                status="error",
                data=None,
                message="User not found"
            )
        logger.info(f"User profile updated successfully: {updated_user.email}")
        return APIResponse(
            status="success",
            data=updated_user,
            message="User profile updated successfully"
        )
    except HTTPException as e:
        logger.warning(f"Profile update validation failed: {str(e)}")
        return APIResponse(
            status="error",
            data=None,
            message=str(e.detail)
        )
    except IntegrityError as e:
        logger.error(f"Database integrity error during update: {str(e)}")
        return APIResponse(
            status="error",
            data=None,
            message="Email or phone number already in use"
        )
    except Exception as e:
        logger.exception(f"Error updating user profile: {str(e)}")
        return APIResponse(
            status="error",
            data=None,
            message="Error updating user profile"
        )

@router.delete("/me", response_model=APIResponse[Dict])
async def delete_user_profile(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete current user account"""
    try:
        deleted = await UserService.delete_user(db=db, user_id=str(current_user.id))
        if not deleted:
            return APIResponse(
                status="error",
                data=None,
                message="User not found"
            )
        logger.info(f"User account deleted successfully: {current_user.email}")
        return APIResponse(
            status="success",
            data={"email": current_user.email},
            message="User account deleted successfully"
        )
    except Exception as e:
        logger.exception(f"Error deleting user account: {str(e)}")
        return APIResponse(
            status="error",
            data=None,
            message="Error deleting user account"
        )