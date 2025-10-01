from typing import List

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
    quantity: int
    imageUrl: HttpUrl
    createdAt: str


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
