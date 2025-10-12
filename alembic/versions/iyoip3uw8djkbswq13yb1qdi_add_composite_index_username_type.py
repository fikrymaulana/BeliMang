"""Add composite index for username and type

Revision ID: iyoip3uw8djkbswq13yb1qdi
Revises: c23456789012
Create Date: 2025-10-01 03:12:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'iyoip3uw8djkbswq13yb1qdi'
down_revision: Union[str, Sequence[str], None] = 'c23456789012'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create composite index on (username, type) for authentication queries
    op.create_index(
        'ix_users_username_type',
        'users',
        ['username', 'type'],
        unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop the composite index
    op.drop_index('ix_users_username_type', table_name='users')