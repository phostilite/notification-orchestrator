# app/api/v1/endpoints/templates.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.template_service import TemplateService
from app.schemas.template import (
    TemplateCreate, 
    TemplateUpdate,
    TemplateResponse,
)
from app.core.auth import get_current_user, require_admin
from app.models.user import User
from app.schemas.common import APIResponse
from app.core.logging_config import logger
import re
from uuid import UUID

router = APIRouter()

NAME_PATTERN = re.compile(r'^[a-zA-Z0-9_-]+$')
MAX_CONTENT_LENGTH = 10000

@router.post("/", response_model=APIResponse[TemplateResponse], status_code=status.HTTP_201_CREATED)
async def create_template(
    *,
    db: Session = Depends(get_db),
    template: TemplateCreate,
    current_user: User = Depends(require_admin)
):
    """Create a new notification template."""
    try:
        # Validate template name format
        if not NAME_PATTERN.match(template.name):
            return APIResponse(
                status="error",
                data=None,
                message="Template name must contain only alphanumeric characters, underscores and hyphens"
            )

        # Check name length
        if len(template.name) > 100:
            return APIResponse(
                status="error",
                data=None,
                message="Template name cannot exceed 100 characters"
            )

        # Check content length
        if len(template.content) > MAX_CONTENT_LENGTH:
            return APIResponse(
                status="error",
                data=None,
                message=f"Template content cannot exceed {MAX_CONTENT_LENGTH} characters"
            )

        # Check if template name already exists
        existing = await TemplateService.get_template_by_name(db, template.name)
        if existing:
            return APIResponse(
                status="error",
                data=None,
                message=f"Template with name '{template.name}' already exists"
            )

        # Validate variables schema if provided
        if template.variables:
            try:
                # Add JSON schema validation logic here
                pass
            except Exception as e:
                return APIResponse(
                    status="error",
                    data=None,
                    message="Invalid variables schema format"
                )

        new_template = await TemplateService.create_template(
            db=db,
            template=template
        )
        
        return APIResponse(
            status="success",
            data=new_template,
            message="Template created successfully"
        )

    except Exception as e:
        logger.error(f"Error creating template: {str(e)}")
        return APIResponse(
            status="error",
            data=None,
            message="Error occurred while creating template"
        )

@router.put("/{template_id}", response_model=APIResponse[TemplateResponse])
async def update_template(
    *,
    db: Session = Depends(get_db),
    template_id: str,
    template_update: TemplateUpdate,
    current_user: User = Depends(require_admin)
):
    """Update a notification template."""
    try:
        # Validate template_id format
        try:
            UUID(template_id)
        except ValueError:
            return APIResponse(
                status="error",
                data=None,
                message="Invalid template ID format. Must be a valid UUID"
            )
        
        # Validate template exists
        existing = await TemplateService.get_template(db, template_id)
        if not existing:
            return APIResponse(
                status="error",
                data=None,
                message=f"Template with id {template_id} not found"
            )

        # If name is being updated, validate uniqueness and format
        if template_update.name:
            if not NAME_PATTERN.match(template_update.name):
                return APIResponse(
                    status="error",
                    data=None,
                    message="Template name must contain only alphanumeric characters, underscores and hyphens"
                )
            
            if template_update.name != existing.name:
                name_exists = await TemplateService.get_template_by_name(db, template_update.name)
                if name_exists:
                    return APIResponse(
                        status="error",
                        data=None,
                        message=f"Template with name '{template_update.name}' already exists"
                    )

        # Validate content length if provided
        if template_update.content and len(template_update.content) > MAX_CONTENT_LENGTH:
            return APIResponse(
                status="error",
                data=None,
                message=f"Template content cannot exceed {MAX_CONTENT_LENGTH} characters"
            )

        # Validate channel if being updated
        valid_channels = ["email", "sms", "push"]
        if template_update.channel:
            if template_update.channel not in valid_channels:
                return APIResponse(
                    status="error",
                    data=None,
                    message=f"Invalid channel. Must be one of: {', '.join(valid_channels)}"
                )
            
            # Check if there are existing notifications using this template
            if hasattr(existing, 'notifications') and len(existing.notifications) > 0:
                return APIResponse(
                    status="error",
                    data=None,
                    message="Cannot change channel of template with existing notifications"
                )

        # Validate version increment
        if template_update.version:
            if template_update.version <= existing.version:
                return APIResponse(
                    status="error",
                    data=None,
                    message="New version must be greater than current version"
                )

        # Validate variables schema if provided
        if template_update.variables:
            try:
                # Add JSON schema validation logic here
                pass
            except Exception as e:
                return APIResponse(
                    status="error",
                    data=None,
                    message="Invalid variables schema format"
                )

        updated_template = await TemplateService.update_template(
            db=db,
            template_id=template_id,
            template_update=template_update
        )

        return APIResponse(
            status="success",
            data=updated_template,
            message="Template updated successfully"
        )

    except Exception as e:
        logger.error(f"Error updating template: {str(e)}")
        return APIResponse(
            status="error",
            data=None,
            message="Error occurred while updating template"
        )

@router.delete("/{template_id}", response_model=APIResponse[dict])
async def delete_template(
    *,
    db: Session = Depends(get_db),
    template_id: str,
    current_user: User = Depends(require_admin)
):
    """Delete a notification template."""
    try:
        # Validate template_id format
        try:
            UUID(template_id)
        except ValueError:
            return APIResponse(
                status="error",
                data=None,
                message="Invalid template ID format. Must be a valid UUID"
            )

        # Check if template exists and has notifications
        existing = await TemplateService.get_template(db, template_id)
        if not existing:
            return APIResponse(
                status="error",
                data=None,
                message=f"Template with id {template_id} not found"
            )

        # Check if template has associated notifications
        if hasattr(existing, 'notifications') and len(existing.notifications) > 0:
            return APIResponse(
                status="error",
                data=None,
                message="Cannot delete template with existing notifications"
            )

        success = await TemplateService.delete_template(
            db=db,
            template_id=template_id
        )
        
        return APIResponse(
            status="success",
            data={"template_id": template_id},
            message="Template deleted successfully"
        )

    except Exception as e:
        logger.error(f"Error deleting template: {str(e)}")
        return APIResponse(
            status="error",
            data=None,
            message="Error occurred while deleting template"
        )