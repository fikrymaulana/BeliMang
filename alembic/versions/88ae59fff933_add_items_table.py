"""add items table

Revision ID: 88ae59fff933
Revises: b4c15559f470
Create Date: 2025-10-01 14:58:59.720517

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "88ae59fff933"
down_revision: Union[str, Sequence[str], None] = "b4c15559f470"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Create items table along with foreign key and indexes
    op.create_table(
        "items",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("merchant_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column(
            "price", sa.Integer(), sa.CheckConstraint("price > 0"), nullable=False
        ),
        sa.Column(
            "quantity", sa.Integer(), nullable=False, server_default=sa.text("0")
        ),
        sa.Column(
            "product_category",
            sa.Enum(
                "Beverage",
                "Food",
                "Snack",
                "Condiments",
                "Additions",
                name="item_product_category_enum",
            ),
            nullable=False,
            server_default="Food",
        ),
        sa.Column(
            "image_url", sa.String(length=1024), nullable=False, server_default=""
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["merchant_id"], ["merchants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_items_id"), "items", ["id"], unique=False)
    op.create_index("ix_items_merchant_id", "items", ["merchant_id"])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop items table and indexes
    op.drop_index(op.f("ix_items_id"), table_name="items")
    op.drop_table("items")
