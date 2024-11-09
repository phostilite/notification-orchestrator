"""add_timezone_fields

Revision ID: 88491fbe47f5
Revises: 76b5f3ebc8e7
Create Date: 2024-11-09 11:53:13.353865

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '88491fbe47f5'
down_revision: Union[str, None] = '76b5f3ebc8e7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add default_timezone to user table
    op.add_column('user', 
        sa.Column('default_timezone', sa.String(50), 
        server_default='UTC', 
        nullable=False)
    )

    # Add timezone to notification table
    op.add_column('notification', 
        sa.Column('timezone', sa.String(50), 
        nullable=True)
    )

    # Ensure scheduled_for and sent_at are timezone-aware
    op.alter_column('notification', 'scheduled_for',
        type_=sa.DateTime(timezone=True),
        existing_type=sa.DateTime(),
        existing_nullable=True
    )
    
    op.alter_column('notification', 'sent_at',
        type_=sa.DateTime(timezone=True),
        existing_type=sa.DateTime(),
        existing_nullable=True
    )


def downgrade() -> None:
    # Remove timezone columns
    op.drop_column('user', 'default_timezone')
    op.drop_column('notification', 'timezone')

    # Revert datetime columns to non-timezone-aware
    op.alter_column('notification', 'scheduled_for',
        type_=sa.DateTime(),
        existing_type=sa.DateTime(timezone=True),
        existing_nullable=True
    )
    
    op.alter_column('notification', 'sent_at',
        type_=sa.DateTime(),
        existing_type=sa.DateTime(timezone=True),
        existing_nullable=True
    )