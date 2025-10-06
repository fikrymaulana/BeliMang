# src/merchants/schemas.py

# =========================
# ====== KODE LEAD ========
# (TIDAK DIUBAH SAMA SEKALI)
# =========================

from typing import List, Optional
from pydantic import BaseModel, HttpUrl

from .enums import ItemProductCategoryEnum, MerchantCategoryEnum


class LocationSchema(BaseModel):
    lat: float
    long: float


class ItemResponse(BaseModel):
    itemId: str
    name: str
    productCategory: ItemProductCategoryEnum
    price: int
    imageUrl: HttpUrl
    createdAt: str
    quantity: Optional[int] = None


class DetailMerchantResponse(BaseModel):
    merchantId: str
    name: str
    merchantCategory: MerchantCategoryEnum
    imageUrl: HttpUrl
    location: LocationSchema
    createdAt: str


class MerchantResponse(BaseModel):
    merchant: DetailMerchantResponse
    items: List[ItemResponse]


class NearbyResponse(BaseModel):
    data: List[MerchantResponse]
    meta: dict


# ============================================
# ====== TAMBAHAN: SKEMA ADMIN MILIKMU =======
# (HANYA DITAMBAHKAN, TANPA MENGUBAH LEAD) ====
# ============================================

from typing import Literal
from pydantic import Field
from datetime import datetime

# Dukungan Pydantic v2 & v1 untuk from_attributes/orm_mode
try:
    from pydantic import ConfigDict  # Pydantic v2
    _IS_PYDANTIC_V2 = True
except Exception:
    _IS_PYDANTIC_V2 = False


class AdminBaseModel(BaseModel):
    """
    Base model untuk skema Admin* agar bisa parse dari SQLAlchemy object.
    Kompatibel Pydantic v2 (from_attributes) & v1 (orm_mode).
    """
    if _IS_PYDANTIC_V2:
        model_config = ConfigDict(from_attributes=True)  # type: ignore[name-defined]
    else:  # Pydantic v1 fallback
        class Config:
            orm_mode = True


class AdminLocationSchema(AdminBaseModel):
    Lat: float = Field(..., description="Latitude")
    Long: float = Field(..., description="Longitude")


class AdminMerchantCreate(AdminBaseModel):
    name: str = Field(..., min_length=2, max_length=30)
    merchantCategory: Literal[
        "SmallRestaurant",
        "MediumRestaurant",
        "LargeRestaurant",
        "MerchandiseRestaurant",
        "BoothKiosk",
        "ConvenienceStore",
    ]
    imageUrl: HttpUrl
    Location: AdminLocationSchema


class AdminMerchantOut(AdminBaseModel):
    merchantId: str


class AdminMerchantRead(AdminBaseModel):
    merchantId: str
    name: str
    merchantCategory: str
    imageUrl: Optional[HttpUrl]
    Location: AdminLocationSchema
    createdAt: datetime  # akan otomatis ISO 8601 oleh Pydantic


class AdminMeta(AdminBaseModel):
    limit: int
    offset: int
    total: int


class AdminMerchantListResponse(AdminBaseModel):
    data: List[AdminMerchantRead]
    meta: AdminMeta
