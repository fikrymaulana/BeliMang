"""add estimates and estimate_items tables

Revision ID: 847cbb0dcf3b
Revises: b5be16596ade
Create Date: 2025-10-02 00:53:50.018215

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "847cbb0dcf3b"
down_revision: Union[str, Sequence[str], None] = "b5be16596ade"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "estimates",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("total_price", sa.Integer(), nullable=False),
        sa.Column("est_minutes", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "estimate_items",
        sa.Column("estimate_id", sa.String(length=36), nullable=False),
        sa.Column("item_id", sa.String(length=36), nullable=False),
        sa.Column("merchant_id", sa.String(length=36), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("unit_price", sa.Integer(), nullable=False),
        sa.Column("item_name", sa.String(length=255), nullable=False),
        sa.Column("product_category", sa.String(length=50), nullable=False),
        sa.Column("image_url", sa.String(length=1024), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["estimate_id"], ["estimates.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["item_id"], ["items.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["merchant_id"], ["merchants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("estimate_id", "item_id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("estimate_items")
    op.drop_table("estimates")
