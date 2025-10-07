# src/merchants/router.py
from typing import Optional, Callable, TypeVar

from fastapi import APIRouter, Depends, Path, Query, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session as SyncSession

# ====== AUTH ======
from src.admin.utils import require_admin, verify_token

# ====== DATABASE: async-only dari src/database.py ======
from src.database import get_db  # AsyncSession

# ====== SERVICE ======
from .service import MerchantService

# ====== SCHEMAS ======
from .schemas import (
    AdminMerchantCreate as MerchantCreate,
    AdminMerchantOut as MerchantOut,
    AdminMerchantListResponse as MerchantListResponse,
    NearbyResponse,
)

# ====== ITEMS SUB-ROUTER (sudah async) ======
from src.merchants.items.router import router as items_router


# util kecil untuk menjalankan kode ORM sync di atas AsyncSession
T = TypeVar("T")
async def _run_with_sync_session(async_sess: AsyncSession, fn: Callable[[SyncSession], T]) -> T:
    def _inner(sync_conn):
        # buat SyncSession yang bound ke connection milik AsyncSession
        with SyncSession(bind=sync_conn) as s:
            return fn(s)
    return await async_sess.run_sync(_inner)


# =============================================================================
# ADMIN ROUTER (/admin/merchants/*) — Wajib Admin
# =============================================================================
admin_router = APIRouter(
    prefix="/admin/merchants",
    tags=["Admin - Merchants"],
    dependencies=[Depends(require_admin)],   # semua endpoint admin wajib admin
)

@admin_router.post(
    "",  # penting: "" bukan "/"
    response_model=MerchantOut,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"description": "Bad Request – validation failed"},
        401: {"description": "Unauthorized – missing or invalid token"},
        403: {"description": "Admin access required"},
    },
)
async def add_merchant(
    payload: MerchantCreate,
    session: AsyncSession = Depends(get_db),   # AsyncSession dari src/database.py
):
    """Tambah merchant baru (ADMIN)."""
    if not payload.name or not payload.imageUrl:
        raise HTTPException(status_code=400, detail="Missing required fields: name or imageUrl")

    def _op(sync_db: SyncSession):
        return MerchantService.create_merchant(sync_db, payload)

    try:
        m = await _run_with_sync_session(session, _op)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
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

@admin_router.get(
    "",  # penting: "" bukan "/"
    response_model=MerchantListResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"description": "Unauthorized – missing or invalid token"},
        403: {"description": "Admin access required"},
    },
)
async def list_merchants(
    merchantId: Optional[str] = None,
    limit: int = Query(default=5, ge=1),
    offset: int = Query(default=0, ge=0),
    name: Optional[str] = None,
    merchantCategory: Optional[str] = None,
    createdAt: Optional[str] = None,
    session: AsyncSession = Depends(get_db),   # AsyncSession dari src/database.py
):
    """List merchants (ADMIN)."""
    if merchantCategory and merchantCategory not in VALID_CATEGORIES:
        return {"data": [], "meta": {"limit": limit, "offset": offset, "total": 0}}

    sort_dir = createdAt if createdAt in VALID_CREATED_AT_SORT else None

    def _op(sync_db: SyncSession):
        return MerchantService.list_merchants(
            db=sync_db,
            merchant_id=merchantId,
            name=name,
            category=merchantCategory,
            sort_created_at=sort_dir,
            limit=limit,
            offset=offset,
        )

    try:
        items, total = await _run_with_sync_session(session, _op)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"data": items, "meta": {"limit": limit, "offset": offset, "total": total}}


# === NEST ITEMS: /admin/merchants/{merchant_id}/items =========================
# items_router sendiri sudah admin-guard; tambahkan default responses
items_router.responses = {
    400: {"description": "Bad Request – validation failed"},
    401: {"description": "Unauthorized – missing or invalid token"},
    403: {"description": "Admin access required"},
    404: {"description": "Merchant not found"},
}
admin_router.include_router(
    items_router,
    prefix="/{merchant_id}/items",
    tags=["Admin - Items"],
    dependencies=[Depends(require_admin)],
)


# =============================================================================
# NEARBY ROUTER (tetap async)
# =============================================================================
nearby_router = APIRouter(tags=["Merchants"])

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
    session: AsyncSession = Depends(get_db),   # AsyncSession
    _=Depends(verify_token),  # kalau endpoint ini public, hapus dependensi ini
):
    return await MerchantService.get_nearby_merchants(
        session, lat, long, merchantId, merchantCategory, name, limit, offset
    )


# =============================================================================
# ROOT ROUTER EXPORT
# =============================================================================
router = APIRouter()
router.include_router(admin_router)
router.include_router(nearby_router)
