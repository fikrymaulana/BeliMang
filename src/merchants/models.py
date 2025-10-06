# src/merchants/models.py
from datetime import datetime
from typing import Any, List

from cuid2 import cuid_wrapper
from geoalchemy2 import Geography
from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    func,
    Computed,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
from .enums import ItemProductCategoryEnum, MerchantCategoryEnum

CUID = cuid_wrapper()


class Merchant(Base):
    __tablename__ = "merchants"

    # CUID2 rata-rata 24~27 char, 36 aman juga
    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True, default=CUID)

    name: Mapped[str] = mapped_column(String(255), nullable=False)

    merchant_category: Mapped[MerchantCategoryEnum] = mapped_column(
        Enum(
            MerchantCategoryEnum,
            name="merchant_category_enum",
            create_type=False,  # hormati tipe enum existing dari migrasi awal
        ),
        nullable=False,
    )

    image_url: Mapped[str] = mapped_column(String(1024), nullable=False)

    # koordinat
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)

    # Kolom geografi: POINT(lon lat), SRID 4326 — STORED computed
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

    __table_args__ = (
        CheckConstraint("latitude BETWEEN -90 AND 90", name="ck_merchants_lat_range"),
        CheckConstraint("longitude BETWEEN -180 AND 180", name="ck_merchants_long_range"),
        # Index GiST untuk percepat pencarian geospasial
        Index("ix_merchants_geog", "geog", postgresql_using="gist"),
    )


class Item(Base):
    __tablename__ = "items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True, default=CUID)

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
            name=ItemProductCategoryEnum.__pg_name__,  # pastikan enum ini memang punya __pg_name__
            create_type=False,                         # set False jika tipe sudah dibuat via migrasi
        ),
        nullable=False,
    )

    price: Mapped[int] = mapped_column(Integer, CheckConstraint("price >= 1"), nullable=False)

    image_url: Mapped[str] = mapped_column(String(1024), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    merchant: Mapped["Merchant"] = relationship(
        "Merchant",
        back_populates="items",
        primaryjoin="Item.merchant_id==Merchant.id",
    )
