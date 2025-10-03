from typing import List

from pydantic import BaseModel, Field

from ..merchants.enums import ItemProductCategoryEnum
from ..merchants.schemas import MerchantResponse


class LocationIn(BaseModel):
    lat: str = Field(...)
    long: str = Field(...)


class OrderItemIn(BaseModel):
    itemId: str = Field(...)
    quantity: int = Field(..., ge=1)


class OrderIn(BaseModel):
    merchantId: str = Field(...)
    isStartingPoint: bool = Field(...)
    items: List[OrderItemIn]


class EstimateItem(BaseModel):
    estimateId: str
    itemId: str
    merchantId: str
    quantity: int
    price: int
    name: str
    productCategory: ItemProductCategoryEnum
    imageUrl: str


class EstimateRequest(BaseModel):
    userLocation: LocationIn
    orders: List[OrderIn]


class EstimateResponse(BaseModel):
    totalPrice: int
    estimatedDeliveryTimeInMinutes: int
    calculatedEstimateId: str


class PlaceOrderRequest(BaseModel):
    calculatedEstimateId: str = Field(...)


class PlaceOrderResponse(BaseModel):
    orderId: str


class OrderHistoryResponse(BaseModel):
    orderId: str
    orders: List[MerchantResponse]
