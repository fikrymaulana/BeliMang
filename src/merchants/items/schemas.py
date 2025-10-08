from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, AliasChoices, HttpUrl

# Import enum yang sudah didefinisikan di src/merchants/enum.py
from src.merchants.enums import ItemProductCategoryEnum


# ======================
# Request body (Admin)
# ======================
class ItemCreate(BaseModel):
    """Schema untuk menambah item baru."""
    model_config = ConfigDict(populate_by_name=True, extra="forbid")  # tolak field asing (sku, description, dll)

    name: str = Field(..., min_length=2, max_length=30)
    # internal field = category; input bisa "productCategory"/"category"; output pakai "productCategory"
    category: ItemProductCategoryEnum = Field(
        ...,
        validation_alias=AliasChoices("productCategory", "category"),
        serialization_alias="productCategory",
    )
    price: int = Field(..., ge=1)
    imageUrl: HttpUrl  # wajib di request


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
    # di ORM kita expose attribute 'category' (kolom fisik: product_category)
    productCategory: ItemProductCategoryEnum = Field(validation_alias="category")
    price: int  # DB: integer NOT NULL
    # DB bisa simpan '' (empty string). Pakai Optional[str] agar tidak gagal validasi.
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
