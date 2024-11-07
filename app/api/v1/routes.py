# app/api/v1/routes.py
from fastapi import APIRouter
from app.api.v1.endpoints import notifications, templates, preferences, users

api_router = APIRouter()

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