"""move_audit_fields_to_mixin

Revision ID: 76b5f3ebc8e7
Revises: ca4e2eca7525
Create Date: 2024-11-08 20:30:43.333292

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '76b5f3ebc8e7'
down_revision: Union[str, None] = 'ca4e2eca7525'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('deliverystatus_updated_by_id_fkey', 'deliverystatus', type_='foreignkey')
    op.drop_constraint('deliverystatus_created_by_id_fkey', 'deliverystatus', type_='foreignkey')
    op.drop_column('deliverystatus', 'created_by_id')
    op.drop_column('deliverystatus', 'updated_by_id')
    op.drop_constraint('notification_updated_by_id_fkey', 'notification', type_='foreignkey')
    op.drop_constraint('notification_created_by_id_fkey', 'notification', type_='foreignkey')
    op.drop_column('notification', 'created_by_id')
    op.drop_column('notification', 'updated_by_id')
    op.drop_constraint('notificationtemplate_created_by_id_fkey', 'notificationtemplate', type_='foreignkey')
    op.drop_constraint('notificationtemplate_updated_by_id_fkey', 'notificationtemplate', type_='foreignkey')
    op.drop_column('notificationtemplate', 'updated_by_id')
    op.drop_column('notificationtemplate', 'created_by_id')
    op.drop_constraint('user_created_by_id_fkey', 'user', type_='foreignkey')
    op.drop_constraint('user_updated_by_id_fkey', 'user', type_='foreignkey')
    op.drop_column('user', 'updated_by_id')
    op.drop_column('user', 'created_by_id')
    op.drop_constraint('userpreference_updated_by_id_fkey', 'userpreference', type_='foreignkey')
    op.drop_constraint('userpreference_created_by_id_fkey', 'userpreference', type_='foreignkey')
    op.drop_column('userpreference', 'updated_by_id')
    op.drop_column('userpreference', 'created_by_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('userpreference', sa.Column('created_by_id', sa.UUID(), autoincrement=False, nullable=True))
    op.add_column('userpreference', sa.Column('updated_by_id', sa.UUID(), autoincrement=False, nullable=True))
    op.create_foreign_key('userpreference_created_by_id_fkey', 'userpreference', 'user', ['created_by_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key('userpreference_updated_by_id_fkey', 'userpreference', 'user', ['updated_by_id'], ['id'], ondelete='SET NULL')
    op.add_column('user', sa.Column('created_by_id', sa.UUID(), autoincrement=False, nullable=True))
    op.add_column('user', sa.Column('updated_by_id', sa.UUID(), autoincrement=False, nullable=True))
    op.create_foreign_key('user_updated_by_id_fkey', 'user', 'user', ['updated_by_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key('user_created_by_id_fkey', 'user', 'user', ['created_by_id'], ['id'], ondelete='SET NULL')
    op.add_column('notificationtemplate', sa.Column('created_by_id', sa.UUID(), autoincrement=False, nullable=True))
    op.add_column('notificationtemplate', sa.Column('updated_by_id', sa.UUID(), autoincrement=False, nullable=True))
    op.create_foreign_key('notificationtemplate_updated_by_id_fkey', 'notificationtemplate', 'user', ['updated_by_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key('notificationtemplate_created_by_id_fkey', 'notificationtemplate', 'user', ['created_by_id'], ['id'], ondelete='SET NULL')
    op.add_column('notification', sa.Column('updated_by_id', sa.UUID(), autoincrement=False, nullable=True))
    op.add_column('notification', sa.Column('created_by_id', sa.UUID(), autoincrement=False, nullable=True))
    op.create_foreign_key('notification_created_by_id_fkey', 'notification', 'user', ['created_by_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key('notification_updated_by_id_fkey', 'notification', 'user', ['updated_by_id'], ['id'], ondelete='SET NULL')
    op.add_column('deliverystatus', sa.Column('updated_by_id', sa.UUID(), autoincrement=False, nullable=True))
    op.add_column('deliverystatus', sa.Column('created_by_id', sa.UUID(), autoincrement=False, nullable=True))
    op.create_foreign_key('deliverystatus_created_by_id_fkey', 'deliverystatus', 'user', ['created_by_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key('deliverystatus_updated_by_id_fkey', 'deliverystatus', 'user', ['updated_by_id'], ['id'], ondelete='SET NULL')
    # ### end Alembic commands ###
