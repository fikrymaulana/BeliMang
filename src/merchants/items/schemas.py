from datetime import datetime
from typing import Annotated, Optional

from pydantic import (
    AliasChoices,
    BaseModel,
    Field,
    StrictInt,
    StringConstraints,
)

from src.merchants.enums import ItemProductCategoryEnum


# ======================
# Request body (Admin)
# ======================
class ItemCreate(BaseModel):
    """Schema untuk menambah item baru."""

    name: str = Field(..., min_length=2, max_length=30)
    category: ItemProductCategoryEnum = Field(
        ...,
        validation_alias=AliasChoices("productCategory", "category"),
        serialization_alias="productCategory",
    )
    price: StrictInt = Field(..., ge=1)
    imageUrl: Annotated[
        str,
        StringConstraints(pattern=r"^https?://[A-Za-z0-9.-]+\.[A-Za-z]{2,}(?:/.*)?$"),
    ]


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
    itemId: str = Field(validation_alias="id")
    name: str
    # di ORM kita expose attribute 'category' (kolom fisik: product_category)
    productCategory: ItemProductCategoryEnum = Field(validation_alias="category")
    price: int  # DB: integer NOT NULL
    imageUrl: Optional[str] = Field(default=None, validation_alias="image_url")
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
