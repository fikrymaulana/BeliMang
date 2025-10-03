from typing import Optional

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..admin.utils import verify_token

from ..database import get_db
from .schemas import NearbyResponse
from .service import MerchantService

router = APIRouter()


@router.get(
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
    session: AsyncSession = Depends(get_db),
    _=Depends(verify_token),
):
    return await MerchantService.get_nearby_merchants(
        session, lat, long, merchantId, merchantCategory, name, limit, offset
    )
