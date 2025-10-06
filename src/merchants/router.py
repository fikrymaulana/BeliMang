# src/merchants/router.py

from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    Path,
    Query,
    status,
    HTTPException,
)
from sqlalchemy.orm import Session
    # if your linter complains about unused import, keep it — used for nearby (async)
from sqlalchemy.ext.asyncio import AsyncSession

# ====== AUTH ======
from ..admin.utils import verify_token

# ====== DATABASE ======
from .database import get_db as get_db_sync
from ..database import get_db as get_db_async

# ====== SERVICE ======
from . import service

# ====== SCHEMAS ======
# Pakai skema Admin* untuk endpoint ADMIN, dan skema lead untuk nearby
from .schemas import (
    AdminMerchantCreate as MerchantCreate,
    AdminMerchantOut as MerchantOut,
    AdminMerchantListResponse as MerchantListResponse,
    NearbyResponse,  # dari blok lead, jangan diubah
)

# ====== ITEMS SUB-ROUTER ======
from src.merchants.items.router import router as items_router


# -----------------------------------------------------------------------------
# ADMIN ROUTER (/admin/merchants)
# -----------------------------------------------------------------------------
admin_router = APIRouter(
    prefix="/admin/merchants",
    tags=["Merchants"],
)


# === POST /admin/merchants ====================================================
@admin_router.post(
    "/",
    response_model=MerchantOut,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"description": "Bad Request – validation failed"},
        401: {"description": "Unauthorized – missing or invalid token"},
    },
)
def add_merchant(
    payload: MerchantCreate,
    db: Session = Depends(get_db_sync),
    _user=Depends(verify_token),
):
    """Tambah merchant baru"""
    # --- 400: request doesn’t pass validation (manual minimal) ---
    if not payload.name or not payload.imageUrl:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required fields: name or imageUrl",
        )

    try:
        m = service.create_merchant(db, payload)
    except Exception as e:
        # fallback 400 jika ada error bisnis/DB
        raise HTTPException(status_code=400, detail=str(e))

    return {"merchantId": str(m.id)}


# === GET /admin/merchants =====================================================
VALID_CATEGORIES = {
    "SmallRestaurant",
    "MediumRestaurant",
    "LargeRestaurant",
    "MerchandiseRestaurant",
    "BoothKiosk",
    "ConvenienceStore",
}
VALID_CREATED_AT_SORT = {"asc", "desc"}


@admin_router.get(
    "/",
    response_model=MerchantListResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"description": "Unauthorized – missing or invalid token"},
    },
)
def list_merchants(
    merchantId: Optional[str] = None,
    limit: int = Query(default=5, ge=1),
    offset: int = Query(default=0, ge=0),
    name: Optional[str] = None,
    merchantCategory: Optional[str] = None,
    createdAt: Optional[str] = None,
    db: Session = Depends(get_db_sync),
    _user=Depends(verify_token),
):
    """List merchants"""
    if merchantCategory and merchantCategory not in VALID_CATEGORIES:
        return {"data": [], "meta": {"limit": limit, "offset": offset, "total": 0}}

    sort_dir = createdAt if createdAt in VALID_CREATED_AT_SORT else None

    items, total = service.list_merchants(
        db=db,
        merchant_id=merchantId,
        name=name,
        category=merchantCategory,
        sort_created_at=sort_dir,
        limit=limit,
        offset=offset,
    )

    return {"data": items, "meta": {"limit": limit, "offset": offset, "total": total}}


# -----------------------------------------------------------------------------
# ADMIN ITEMS ROUTER (nested under /admin/merchants/:merchantId/items)
# -----------------------------------------------------------------------------
# Tambahkan default responses untuk semua endpoint items di bawah prefix ini
items_router.responses = {
    400: {"description": "Bad Request – validation failed"},
    401: {"description": "Unauthorized – missing or invalid token"},
    404: {"description": "Merchant not found"},
}

admin_router.include_router(
    items_router,
    prefix="/{merchant_id}/items",
    tags=["Admin - Items"],
)


# -----------------------------------------------------------------------------
# NEARBY ROUTER (dari lead, TIDAK DIUBAH)
# -----------------------------------------------------------------------------
nearby_router = APIRouter()


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
    session: AsyncSession = Depends(get_db_async),
    _=Depends(verify_token),
):
    from .service import MerchantService
    return await MerchantService.get_nearby_merchants(
        session, lat, long, merchantId, merchantCategory, name, limit, offset
    )


# -----------------------------------------------------------------------------
# ROOT ROUTER EXPORT
# -----------------------------------------------------------------------------
router = APIRouter()
router.include_router(admin_router)
router.include_router(nearby_router)
