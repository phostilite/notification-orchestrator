# app/models/mixins/audit.py
from sqlalchemy import Column, UUID, ForeignKey
from sqlalchemy.orm import relationship, declared_attr
from typing import Any, Type

class AuditMixin:
    """Mixin for audit trail functionality"""
    
    @declared_attr
    def created_by_id(cls: Type[Any]) -> Column:
        return Column(UUID(as_uuid=True), ForeignKey('user.id', ondelete='SET NULL'), nullable=True)
    
    @declared_attr
    def updated_by_id(cls: Type[Any]) -> Column:
        return Column(UUID(as_uuid=True), ForeignKey('user.id', ondelete='SET NULL'), nullable=True)
    
    @declared_attr
    def created_by(cls: Type[Any]):
        return relationship(
            "User",
            foreign_keys=[cls.created_by_id],
            backref=f"{cls.__name__.lower()}_created"
        )
    
    @declared_attr
    def updated_by(cls: Type[Any]):
        return relationship(
            "User",
            foreign_keys=[cls.updated_by_id], 
            backref=f"{cls.__name__.lower()}_updated"
        )