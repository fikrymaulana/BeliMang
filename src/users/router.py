from typing import List
from typing_extensions import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from src.merchants.enums import MerchantCategoryEnum

from ..purchases.schemas import (
    OrderHistoryResponse,
    PlaceOrderRequest,
    PlaceOrderResponse,
)
from ..users.utils import require_user

from ..purchases.schemas import EstimateResponse, EstimateRequest
from ..purchases.service import PurchaseService

from ..database import get_db
from .schemas import UserRegister, UserLogin, TokenResponse
from .service import create_user, authenticate_user

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserRegister, db: AsyncSession = Depends(get_db)):
    try:
        result = await create_user(db, user_data)
        return result
    except ValueError as e:
        error_msg = str(e)
        if "already exists" in error_msg:
            raise HTTPException(status_code=409, detail=error_msg)
        else:
            raise HTTPException(status_code=400, detail=error_msg)


@router.post("/login", response_model=TokenResponse)
async def login_user(login_data: UserLogin, db: AsyncSession = Depends(get_db)):
    try:
        result = await authenticate_user(db, login_data.username, login_data.password)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/estimate", response_model=EstimateResponse, status_code=status.HTTP_200_OK
)
async def post_users_estimate(
    body: EstimateRequest,
    session: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(require_user),
):
    return await PurchaseService.calculate_estimate(session, body)


@router.post(
    "/orders",
    response_model=PlaceOrderResponse,
    status_code=status.HTTP_201_CREATED,
)
async def place_order(
    body: PlaceOrderRequest,
    session: AsyncSession = Depends(get_db),
    user=Depends(require_user),
):
    order_id = await PurchaseService.place_order_from_estimate(
        session, body.calculatedEstimateId, user.get("sub")
    )
    return PlaceOrderResponse(orderId=order_id)


@router.get(
    "/orders",
    response_model=List[OrderHistoryResponse],
    status_code=status.HTTP_200_OK,
)
async def get_user_orders(
    merchantId: Optional[str] = Query(None),
    limit: int = Query(5, ge=0),
    offset: int = Query(0, ge=0),
    name: Optional[str] = Query(None),
    merchantCategory: Optional[MerchantCategoryEnum] = Query(None),
    session: AsyncSession = Depends(get_db),
    user=Depends(require_user),
):
    results = await PurchaseService.list_user_orders(
        session=session,
        user_id=user.get("sub"),
        merchantId=merchantId,
        name=name,
        merchantCategory=merchantCategory,
        limit=limit,
        offset=offset,
    )
    return results
