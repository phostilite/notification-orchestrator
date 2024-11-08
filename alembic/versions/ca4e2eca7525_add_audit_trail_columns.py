"""add_audit_trail_columns

Revision ID: ca4e2eca7525
Revises: a2860a97145e
Create Date: 2024-11-08 20:08:02.803004

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ca4e2eca7525'
down_revision: Union[str, None] = 'a2860a97145e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('deliverystatus', sa.Column('created_by_id', sa.UUID(), nullable=True))
    op.add_column('deliverystatus', sa.Column('updated_by_id', sa.UUID(), nullable=True))
    op.create_foreign_key(None, 'deliverystatus', 'user', ['created_by_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key(None, 'deliverystatus', 'user', ['updated_by_id'], ['id'], ondelete='SET NULL')
    op.add_column('notification', sa.Column('created_by_id', sa.UUID(), nullable=True))
    op.add_column('notification', sa.Column('updated_by_id', sa.UUID(), nullable=True))
    op.create_foreign_key(None, 'notification', 'user', ['created_by_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key(None, 'notification', 'user', ['updated_by_id'], ['id'], ondelete='SET NULL')
    op.add_column('notificationtemplate', sa.Column('created_by_id', sa.UUID(), nullable=True))
    op.add_column('notificationtemplate', sa.Column('updated_by_id', sa.UUID(), nullable=True))
    op.create_foreign_key(None, 'notificationtemplate', 'user', ['created_by_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key(None, 'notificationtemplate', 'user', ['updated_by_id'], ['id'], ondelete='SET NULL')
    op.add_column('user', sa.Column('created_by_id', sa.UUID(), nullable=True))
    op.add_column('user', sa.Column('updated_by_id', sa.UUID(), nullable=True))
    op.alter_column('user', 'is_admin',
               existing_type=sa.BOOLEAN(),
               nullable=True,
               existing_server_default=sa.text('false'))
    op.create_foreign_key(None, 'user', 'user', ['updated_by_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key(None, 'user', 'user', ['created_by_id'], ['id'], ondelete='SET NULL')
    op.add_column('userpreference', sa.Column('created_by_id', sa.UUID(), nullable=True))
    op.add_column('userpreference', sa.Column('updated_by_id', sa.UUID(), nullable=True))
    op.create_foreign_key(None, 'userpreference', 'user', ['updated_by_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key(None, 'userpreference', 'user', ['created_by_id'], ['id'], ondelete='SET NULL')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'userpreference', type_='foreignkey')
    op.drop_constraint(None, 'userpreference', type_='foreignkey')
    op.drop_column('userpreference', 'updated_by_id')
    op.drop_column('userpreference', 'created_by_id')
    op.drop_constraint(None, 'user', type_='foreignkey')
    op.drop_constraint(None, 'user', type_='foreignkey')
    op.alter_column('user', 'is_admin',
               existing_type=sa.BOOLEAN(),
               nullable=False,
               existing_server_default=sa.text('false'))
    op.drop_column('user', 'updated_by_id')
    op.drop_column('user', 'created_by_id')
    op.drop_constraint(None, 'notificationtemplate', type_='foreignkey')
    op.drop_constraint(None, 'notificationtemplate', type_='foreignkey')
    op.drop_column('notificationtemplate', 'updated_by_id')
    op.drop_column('notificationtemplate', 'created_by_id')
    op.drop_constraint(None, 'notification', type_='foreignkey')
    op.drop_constraint(None, 'notification', type_='foreignkey')
    op.drop_column('notification', 'updated_by_id')
    op.drop_column('notification', 'created_by_id')
    op.drop_constraint(None, 'deliverystatus', type_='foreignkey')
    op.drop_constraint(None, 'deliverystatus', type_='foreignkey')
    op.drop_column('deliverystatus', 'updated_by_id')
    op.drop_column('deliverystatus', 'created_by_id')
    # ### end Alembic commands ###
