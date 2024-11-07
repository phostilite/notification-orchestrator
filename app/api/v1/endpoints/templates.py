# app/api/v1/endpoints/templates.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.template_service import TemplateService
from app.schemas.template import (
    TemplateCreate,
    TemplateUpdate,
    TemplateResponse
)
from app.core.auth import get_current_user, require_admin
from app.models.user import User

router = APIRouter()

@router.post("/templates", response_model=TemplateResponse)
async def create_template(
    *,
    db: Session = Depends(get_db),
    template: TemplateCreate,
    current_user: User = Depends(require_admin)
):
    """
    Create a new notification template.
    """
    try:
        result = await TemplateService.create_template(
            db=db,
            template=template
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/templates", response_model=List[TemplateResponse])
async def list_templates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all notification templates.
    """
    templates = await TemplateService.get_templates(db=db)
    return templates

@router.put("/templates/{template_id}", response_model=TemplateResponse)
async def update_template(
    *,
    db: Session = Depends(get_db),
    template_id: str,
    template_update: TemplateUpdate,
    current_user: User = Depends(require_admin)
):
    """
    Update a notification template.
    """
    try:
        template = await TemplateService.update_template(
            db=db,
            template_id=template_id,
            template_update=template_update
        )
        return template
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/templates/{template_id}")
async def delete_template(
    *,
    db: Session = Depends(get_db),
    template_id: str,
    current_user: User = Depends(require_admin)
):
    """
    Delete a notification template.
    """
    try:
        success = await TemplateService.delete_template(
            db=db,
            template_id=template_id
        )
        if not success:
            raise HTTPException(
                status_code=404,
                detail="Template not found"
            )
        return {"message": "Template deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")