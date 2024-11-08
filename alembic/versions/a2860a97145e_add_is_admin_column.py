"""add_is_admin_column

Revision ID: a2860a97145e
Revises: 386619f630e1
Create Date: 2024-11-08 19:01:41.006532

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a2860a97145e'
down_revision: Union[str, None] = '386619f630e1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add is_admin column
    op.add_column('user', 
        sa.Column('is_admin', sa.Boolean(), 
        nullable=False, 
        server_default='false')
    )

def downgrade() -> None:
    # Remove column if migration needs to be reversed
    op.drop_column('user', 'is_admin')