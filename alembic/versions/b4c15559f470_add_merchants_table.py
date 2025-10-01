"""add merchants table

Revision ID: b4c15559f470
Revises: c23456789012
Create Date: 2025-10-01 14:15:12.390322

"""

from typing import Sequence, Union

import sqlalchemy as sa
from geoalchemy2 import Geography

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b4c15559f470"
down_revision: Union[str, Sequence[str], None] = "c23456789012"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create merchants table along with enum, geography type, and indexes
    op.create_table(
        "merchants",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column(
            "merchant_category",
            sa.Enum(
                "SmallRestaurant",
                "MediumRestaurant",
                "LargeRestaurant",
                "MerchandiseRestaurant",
                "BoothKiosk",
                "ConvenienceStore",
                name="merchant_category_enum",
            ),
            nullable=False,
        ),
        sa.Column("image_url", sa.String(length=1024), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column(
            "geog",
            Geography(
                geometry_type="POINT",
                srid=4326,
                dimension=2,
                from_text="ST_GeogFromText",
                name="geography",
                nullable=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_merchants_id"), "merchants", ["id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop merchants table and indexes
    op.drop_index(op.f("ix_merchants_id"), table_name="merchants")
    op.drop_table("merchants")
