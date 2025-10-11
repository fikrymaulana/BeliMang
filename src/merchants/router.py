from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.admin.utils import require_admin
from src.database import get_db
from src.users.utils import require_user

from .schemas import (
    AdminMerchantCreate as MerchantCreate,
)
from .schemas import (
    AdminMerchantListResponse as MerchantListResponse,
)
from .schemas import (
    AdminMerchantOut as MerchantOut,
)
from .schemas import (
    NearbyResponse,
)
from .service import MerchantService

admin_router = APIRouter(dependencies=[Depends(require_admin)])


# POST /admin/merchants
@admin_router.post("", response_model=MerchantOut, status_code=status.HTTP_201_CREATED)
async def add_merchant(
    payload: MerchantCreate,
    db: AsyncSession = Depends(get_db),
):
    if not payload.name or not payload.imageUrl:
        raise HTTPException(
            status_code=400, detail="Missing required fields: name or imageUrl"
        )

    try:
        m = await MerchantService.create_merchant(db, payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"merchantId": str(m.id)}


VALID_CATEGORIES = {
    "SmallRestaurant",
    "MediumRestaurant",
    "LargeRestaurant",
    "MerchandiseRestaurant",
    "BoothKiosk",
    "ConvenienceStore",
}
VALID_CREATED_AT_SORT = {"asc", "desc"}


# GET /admin/merchants
@admin_router.get(
    "", response_model=MerchantListResponse, status_code=status.HTTP_200_OK
)
async def list_merchants(
    merchantId: Optional[str] = None,
    limit: int = Query(default=5, ge=1),
    offset: int = Query(default=0, ge=0),
    name: Optional[str] = None,
    merchantCategory: Optional[str] = None,
    createdAt: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    if merchantCategory and merchantCategory not in VALID_CATEGORIES:
        return {"data": [], "meta": {"limit": limit, "offset": offset, "total": 0}}

    sort_dir = createdAt if createdAt in VALID_CREATED_AT_SORT else None

    items, total = await MerchantService.list_merchants(
        db=db,
        merchant_id=merchantId,
        name=name,
        category=merchantCategory,
        sort_created_at=sort_dir,
        limit=limit,
        offset=offset,
    )
    return {"data": items, "meta": {"limit": limit, "offset": offset, "total": total}}


nearby_router = APIRouter(dependencies=[Depends(require_user)])


# GET /merchants/nearby/{lat},{long}
@nearby_router.get(
    "/nearby/{lat},{long}",
    response_model=NearbyResponse,
    status_code=status.HTTP_200_OK,
)
async def get_nearby(
    lat=Path(...),
    long=Path(...),
    merchantId: Optional[str] = Query(None),
    limit: int = Query(5),
    offset: int = Query(0),
    name: Optional[str] = Query(None),
    merchantCategory: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    return await MerchantService.get_nearby_merchants(
        db,
        lat,
        long,
        merchantId,
        merchantCategory,
        name,
        limit,
        offset,
    )
