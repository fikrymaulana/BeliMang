from datetime import datetime
from typing import Any, List

from cuid2 import cuid_wrapper
from geoalchemy2 import Geography
from sqlalchemy import (
    Computed,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
from .enums import ItemProductCategoryEnum, MerchantCategoryEnum

CUID = cuid_wrapper()


class Merchant(Base):
    __tablename__ = "merchants"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, index=True, default=CUID
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    merchant_category: Mapped[MerchantCategoryEnum] = mapped_column(
        Enum(
            MerchantCategoryEnum,
            name="merchant_category_enum",
            create_type=False,
        ),
        nullable=False,
    )

    image_url: Mapped[str] = mapped_column(String(1024), nullable=False)

    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)

    geog: Mapped[Any] = mapped_column(
        Geography(geometry_type="POINT", srid=4326),
        Computed(
            "ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)::geography",
            persisted=True,
        ),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    items: Mapped[List["Item"]] = relationship(
        "Item",
        back_populates="merchant",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    __table_args__ = (Index("ix_merchants_geog", "geog", postgresql_using="gist"),)


class Item(Base):
    __tablename__ = "items"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, index=True, default=CUID
    )

    merchant_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("merchants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)

    product_category: Mapped[ItemProductCategoryEnum] = mapped_column(
        Enum(
            ItemProductCategoryEnum,
            name=ItemProductCategoryEnum.__pg_name__,
            create_type=False,
        ),
        nullable=False,
    )

    price: Mapped[int] = mapped_column(Integer, nullable=False)
    image_url: Mapped[str] = mapped_column(String(1024), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    merchant: Mapped["Merchant"] = relationship(
        "Merchant",
        back_populates="items",
        primaryjoin="Item.merchant_id==Merchant.id",
    )
