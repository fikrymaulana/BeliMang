# src/merchants/items/schemas.py
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict, Field, AliasChoices, HttpUrl

# Enum kategori produk
ItemCategory = Literal["Beverage", "Food", "Snack", "Condiments", "Additions"]

# ======================
# Request body (Admin)
# ======================
class ItemCreate(BaseModel):
    """Schema untuk menambah item baru."""
    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(..., min_length=2, max_length=30)
    category: ItemCategory = Field(
        ...,
        validation_alias=AliasChoices("productCategory", "category"),
        serialization_alias="productCategory",
    )
    price: int = Field(..., ge=1)
    imageUrl: HttpUrl


# ======================
# Response body
# ======================
class ItemCreated(BaseModel):
    itemId: str


# ======================
# Untuk GET list
# ======================
class ItemsMeta(BaseModel):
    limit: int
    offset: int
    total: int


class ItemRow(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    itemId: str = Field(validation_alias="id")
    name: str
    productCategory: ItemCategory = Field(validation_alias="category")
    price: Optional[float] = None
    imageUrl: Optional[HttpUrl] = None
    createdAt: datetime = Field(validation_alias="created_at")


class ItemsListResponse(BaseModel):
    data: list[ItemRow]
    meta: ItemsMeta


# ======================
# Error response
# ======================
class ErrorResponse(BaseModel):
    error: str
    message: str
