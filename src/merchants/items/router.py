# src/merchants/items/router.py
from __future__ import annotations

from enum import Enum
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

# ====== DB & AUTH ======
from src.merchants.database import get_db
from src.admin.utils import verify_token

# Pakai repo yang SQL Core (ABSOLUTE IMPORT, bukan relatif)
from src.merchants.items import repository as repo

from .schemas import (
    ItemCreate,
    ItemCreated,
    ItemsListResponse,
    ErrorResponse,
    ItemCategory,
)

router = APIRouter(tags=["Admin - Items"])


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"


# -----------------------------
# Admin Guard (robust)
# -----------------------------
_security = HTTPBearer(auto_error=False)

def admin_guard(creds: HTTPAuthorizationCredentials = Depends(_security)):
    # 401 kalau token tidak ada
    if creds is None or not getattr(creds, "credentials", None):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Unauthorized", "message": "Missing Bearer token"},
        )

    # verify_token milikmu akan raise 401 kalau invalid/expired
    payload = verify_token(creds)

    # Wajib admin
    t = (payload or {}).get("type")
    if t is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Unauthorized", "message": "Token missing 'type' claim"},
        )
    if str(t).lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "Forbidden", "message": "Admin access required"},
        )
    return payload


# ========================================================================
# POST /admin/merchants/{merchant_id}/items
# ========================================================================
@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=ItemCreated,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Merchant Not Found"},
    },
)
def create_item_for_merchant(
    merchant_id: str,             # CUID → string
    payload: ItemCreate,
    db: Session = Depends(get_db),
    _admin=Depends(admin_guard),
):
    """Tambah item ke merchant"""
    # 404 kalau merchant tidak ada
    try:
        if not repo.merchant_exists(db, merchant_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "NotFound", "message": f"Merchant with id '{merchant_id}' not found"},
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"merchant_exists failed: {e}")

    try:
        # mode="json" → HttpUrl/Enum otomatis jadi string
        data = payload.model_dump(by_alias=True, mode="json")
        new_id = repo.create_item(db, merchant_id, data=data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "BadRequest", "message": f"create_item failed: {e}"},
        )

    return {"itemId": str(new_id)}


# ========================================================================
# GET /admin/merchants/{merchant_id}/items
# ========================================================================
@router.get(
    "",
    response_model=ItemsListResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Merchant Not Found"},
    },
    summary="Get items of a merchant with optional filters",
)
def get_items_for_merchant(
    merchant_id: str,  # CUID → string
    item_id: Optional[str] = Query(None, alias="itemId"),
    limit: int = Query(5, ge=1),
    offset: int = Query(0, ge=0),
    name: Optional[str] = Query(None),
    product_category: Optional[ItemCategory] = Query(None, alias="productCategory"),
    created_at: Optional[SortOrder] = Query(None, alias="createdAt"),
    db: Session = Depends(get_db),
    _admin=Depends(admin_guard),
):
    """Ambil items milik merchant"""
    try:
        if not repo.merchant_exists(db, merchant_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "NotFound", "message": f"Merchant with id '{merchant_id}' not found"},
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"merchant_exists failed: {e}")

    sort = created_at.value if created_at else None
    category = str(product_category) if product_category else None

    try:
        items, total = repo.list_items(
            db,
            merchant_id=merchant_id,
            item_id=item_id,
            name=name,
            category=category,
            created_at=sort,
            limit=limit,
            offset=offset,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"list_items failed: {e}")

    return {"data": items, "meta": {"limit": limit, "offset": offset, "total": total}}
