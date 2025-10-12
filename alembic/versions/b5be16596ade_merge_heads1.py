"""empty message

Revision ID: b5be16596ade
Revises: 88ae59fff933, iyoip3uw8djkbswq13yb1qdi
Create Date: 2025-10-02 00:12:16.011477

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b5be16596ade'
down_revision: Union[str, Sequence[str], None] = ('88ae59fff933', 'iyoip3uw8djkbswq13yb1qdi')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
