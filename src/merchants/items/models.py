# src/merchants/items/models.py
from cuid2 import cuid_wrapper
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Numeric
from sqlalchemy.sql import func
from src.merchants.database import Base

CUID = cuid_wrapper()

class Item(Base):
    __tablename__ = "items"
    id = Column(String(36), primary_key=True, default=CUID, nullable=False)
    merchant_id = Column(String(36), ForeignKey("merchants.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False, index=True)
    category = Column(String(32), nullable=False, index=True)
    price = Column(Numeric(12, 2), nullable=True)
    sku = Column(String(64), nullable=True, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
