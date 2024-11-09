# app/models/template.py

# Third-party imports
import jinja2
from sqlalchemy import Column, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

# Local application imports
from .base import Base

class NotificationTemplate(Base):
    """Template model for notification content"""
    name = Column(String(100), nullable=False)
    version = Column(Integer, nullable=False, default=1)
    content = Column(Text, nullable=False)
    variables = Column(JSON)  # JSON schema for required variables
    channel = Column(String(20), nullable=False)  # email, sms, push
    description = Column(String(255))
    
    # Relationships
    notifications = relationship("Notification", back_populates="template")

    def render(self, variables: dict) -> str:
        """Render template with given variables"""
        try:
            template = jinja2.Template(self.content)
            return template.render(**variables)
        except jinja2.TemplateError as e:
            raise ValueError(f"Template rendering error: {str(e)}")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('name', 'version', name='uix_template_version'),
    )