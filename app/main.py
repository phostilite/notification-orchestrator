# app/main.py

# Standard library imports
from contextlib import asynccontextmanager
import json

# Third-party imports
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse

# Local application imports
from app.api.v1.routes import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_STR)

def custom_openapi():
    """Generate custom OpenAPI schema with per-endpoint JWT authorization."""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="A notification service API for managing notifications across multiple channels",
        routes=app.routes,
    )

    # Add JWT security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter your JWT token in the format: Bearer <token>"
        }
    }

    # Get all paths from the schema
    paths = openapi_schema["paths"]

    # Add security field to each endpoint based on path and method
    for path in paths:
        for method in paths[path]:
            endpoint = paths[path][method]
            
            # Skip if it's the root endpoint or docs
            if path == "/" or path.startswith("/docs") or path.startswith("/openapi"):
                continue

            # Add JWT security requirement to all protected endpoints
            if any(protected_path in path for protected_path in ["/notifications", "/templates", "/preferences", "/users"]):
                endpoint["security"] = [{"BearerAuth": []}]
                
                # Add security requirement to the endpoint description
                current_description = endpoint.get("description", "")
                security_desc = "\n\nAuthorization required:\n- Bearer token (JWT)"
                endpoint["description"] = current_description + security_desc

    app.openapi_schema = openapi_schema
    return app.openapi_schema

# Set custom OpenAPI schema
app.openapi = custom_openapi

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint returning API information."""
    return {
        "message": "Welcome to Notification Service API",
        "docs": "/docs",
        "version": settings.VERSION
    }