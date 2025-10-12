from typing import List

from pydantic import BaseModel, Field, StrictFloat, StrictInt

from ..merchants.enums import ItemProductCategoryEnum
from ..merchants.schemas import MerchantResponse


class LocationIn(BaseModel):
    lat: StrictFloat = Field(...)
    long: StrictFloat = Field(...)


class OrderItemIn(BaseModel):
    itemId: str = Field(min_length=1)
    quantity: StrictInt = Field(..., ge=1)


class OrderIn(BaseModel):
    merchantId: str = Field(min_length=1)
    isStartingPoint: bool = Field(...)
    items: List[OrderItemIn]


class EstimateItem(BaseModel):
    estimateId: str
    itemId: str
    merchantId: str
    quantity: StrictInt
    price: StrictInt
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
    calculatedEstimateId: str = Field(min_length=1)


class PlaceOrderResponse(BaseModel):
    orderId: str


class OrderHistoryResponse(BaseModel):
    orderId: str
    orders: List[MerchantResponse]
