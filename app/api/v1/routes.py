# app/api/v1/routes.py

# Third-party imports
from fastapi import APIRouter

# Local application imports
from app.api.v1.endpoints import (
    notifications,
    preferences,
    templates,
    users
)

# Main API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(
    users.router,
    prefix="/users",
    tags=["users"]
)

api_router.include_router(
    notifications.router,
    prefix="/notifications",
    tags=["notifications"]
)

api_router.include_router(
    templates.router,
    prefix="/templates",
    tags=["templates"]
)

api_router.include_router(
    preferences.router,
    prefix="/preferences",
    tags=["preferences"]
)