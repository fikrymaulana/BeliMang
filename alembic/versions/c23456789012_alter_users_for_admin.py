"""Alter users table for admin support

Revision ID: c23456789012
Revises: b12345678901
Create Date: 2025-09-25 15:41:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c23456789012'
down_revision: Union[str, Sequence[str], None] = 'b12345678901'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add username column
    op.add_column('users', sa.Column('username', sa.String(length=30), nullable=False))
    # Add type column with enum
    user_type = sa.Enum('admin', 'user', name='usertype')
    user_type.create(op.get_bind())
    op.add_column('users', sa.Column('type', user_type, nullable=False, server_default='user'))
    # Drop unique index on email
    op.drop_index('ix_users_email', table_name='users')
    # Add unique constraint on username
    op.create_unique_constraint('uq_users_username', 'users', ['username'])
    # Add unique constraint on (email, type)
    op.create_unique_constraint('uq_users_email_type', 'users', ['email', 'type'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop constraints
    op.drop_constraint('uq_users_email_type', 'users', type_='unique')
    op.drop_constraint('uq_users_username', 'users', type_='unique')
    # Add back unique on email
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    # Drop columns
    op.drop_column('users', 'type')
    op.drop_column('users', 'username')
    # Drop enum
    user_type = sa.Enum('admin', 'user', name='usertype')
    user_type.drop(op.get_bind())