from cuid2 import cuid_wrapper
from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.sql import func

from ...database import Base
from ..enums import ItemProductCategoryEnum

CUID = cuid_wrapper()


class Item(Base):
    __tablename__ = "items"

    id = Column(String(36), primary_key=True, default=CUID, nullable=False, index=True)
    merchant_id = Column(
        String(36),
        ForeignKey("merchants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name = Column(String(255), nullable=False, index=True)

    # ORM attribute = `category`, nama kolom fisik di DB = product_category
    category = Column(
        "product_category",
        SQLEnum(
            ItemProductCategoryEnum,
            name=ItemProductCategoryEnum.__pg_name__,
            create_type=False,
        ),
        nullable=False,
        index=True,
    )

    price = Column(Integer, CheckConstraint("price > 0"), nullable=False)

    sku = Column(String(64), nullable=True, index=True)
    description = Column(Text, nullable=True)

    image_url = Column(String(1024), nullable=False, server_default="")

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
