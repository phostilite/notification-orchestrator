"""initial migration

Revision ID: 386619f630e1
Revises: 
Create Date: 2024-11-07 00:36:21.393525

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '386619f630e1'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('notificationtemplate',
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('version', sa.Integer(), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('variables', sa.JSON(), nullable=True),
    sa.Column('channel', sa.String(length=20), nullable=False),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name', 'version', name='uix_template_version')
    )
    op.create_table('user',
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('phone', sa.String(length=20), nullable=True),
    sa.Column('full_name', sa.String(length=100), nullable=True),
    sa.Column('hashed_password', sa.String(length=255), nullable=False),
    sa.Column('is_verified', sa.Boolean(), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_phone'), 'user', ['phone'], unique=True)
    op.create_table('notification',
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('template_id', sa.UUID(), nullable=False),
    sa.Column('channel', sa.String(length=20), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('variables', sa.JSON(), nullable=True),
    sa.Column('priority', sa.Integer(), nullable=True),
    sa.Column('scheduled_for', sa.DateTime(), nullable=True),
    sa.Column('sent_at', sa.DateTime(), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.Column('retry_count', sa.Integer(), nullable=True),
    sa.Column('max_retries', sa.Integer(), nullable=True),
    sa.Column('error_message', sa.Text(), nullable=True),
    sa.Column('notification_metadata', sa.JSON(), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['template_id'], ['notificationtemplate.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('userpreference',
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('channel', sa.String(length=20), nullable=False),
    sa.Column('enabled', sa.Boolean(), nullable=True),
    sa.Column('quiet_hours_start', sa.Time(), nullable=True),
    sa.Column('quiet_hours_end', sa.Time(), nullable=True),
    sa.Column('frequency_limit', sa.Integer(), nullable=True),
    sa.Column('priority_threshold', sa.Integer(), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id', 'channel', name='uix_user_channel')
    )
    op.create_table('deliverystatus',
    sa.Column('notification_id', sa.UUID(), nullable=False),
    sa.Column('attempt_number', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('provider_response', sa.JSON(), nullable=True),
    sa.Column('error_code', sa.String(length=50), nullable=True),
    sa.Column('error_message', sa.Text(), nullable=True),
    sa.Column('delivered_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['notification_id'], ['notification.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('deliverystatus')
    op.drop_table('userpreference')
    op.drop_table('notification')
    op.drop_index(op.f('ix_user_phone'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    op.drop_table('notificationtemplate')
    # ### end Alembic commands ###