# app/services/template_service.py

from sqlalchemy.orm import Session
from app.models.template import NotificationTemplate
from app.schemas.template import TemplateCreate, TemplateUpdate

class TemplateService:
    @staticmethod
    async def create_template(db: Session, template: TemplateCreate):
        new_template = NotificationTemplate(**template.model_dump())
        db.add(new_template)
        db.commit()
        db.refresh(new_template)
        return new_template

    @staticmethod
    async def get_templates(db: Session):
        return db.query(NotificationTemplate).all()

    @staticmethod
    async def update_template(db: Session, template_id: str, template_update: TemplateUpdate):
        db_template = db.query(NotificationTemplate).filter(NotificationTemplate.id == template_id).first()
        
        if not db_template:
            raise ValueError("Template not found")

        for key, value in template_update.model_dump(exclude_unset=True).items():
            setattr(db_template, key, value)

        db.commit()
        db.refresh(db_template)
        return db_template

    @staticmethod
    async def delete_template(db: Session, template_id: str):
        db_template = db.query(NotificationTemplate).filter(NotificationTemplate.id == template_id).first()
        
        if not db_template:
            return False

        db.delete(db_template)
        db.commit()
        return True