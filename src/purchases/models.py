from datetime import datetime

from cuid2 import cuid_wrapper
from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
from ..merchants.models import Item, Merchant

CUID = cuid_wrapper()


class Estimate(Base):
    __tablename__ = "estimates"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=CUID())
    total_price: Mapped[int] = mapped_column(Integer, nullable=False)
    est_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    items: Mapped[list["EstimateItem"]] = relationship(
        "EstimateItem",
        back_populates="estimate",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class EstimateItem(Base):
    __tablename__ = "estimate_items"

    estimate_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("estimates.id", ondelete="CASCADE"),
        primary_key=True,
    )
    item_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("items.id", ondelete="RESTRICT"),
        primary_key=True,
    )
    merchant_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("merchants.id", ondelete="CASCADE"),
        nullable=False,
    )

    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[int] = mapped_column(Integer, nullable=False)

    item_name: Mapped[str] = mapped_column(String(255), nullable=False)
    product_category: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # enum snapshot
    image_url: Mapped[str] = mapped_column(String(1024), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    estimate: Mapped["Estimate"] = relationship("Estimate", back_populates="items")
    item: Mapped["Item"] = relationship("Item", lazy="joined")
    merchant: Mapped["Merchant"] = relationship("Merchant", lazy="joined")
