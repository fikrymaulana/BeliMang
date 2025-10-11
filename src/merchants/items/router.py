from __future__ import annotations

from enum import Enum
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.admin.utils import require_admin
from src.database import get_db
from src.merchants.enums import ItemProductCategoryEnum
from src.merchants.items import repository as repo

from .schemas import ErrorResponse, ItemCreate, ItemCreated, ItemsListResponse

router = APIRouter(
    dependencies=[Depends(require_admin)],
)


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"


# POST /admin/merchants/{merchant_id}/items
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
async def create_item_for_merchant(
    merchant_id: str,
    payload: ItemCreate,
    session: AsyncSession = Depends(get_db),
):
    exists = await repo.merchant_exists(session, merchant_id)
    if not exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "NotFound",
                "message": f"Merchant with id '{merchant_id}' not found",
            },
        )

    try:
        new_id = await repo.create_item(session, merchant_id, data=payload.model_dump())
    except ValueError as e:
        raise HTTPException(
            status_code=400, detail={"error": "BadRequest", "message": str(e)}
        )

    return {"itemId": str(new_id)}


# GET /admin/merchants/{merchant_id}/items
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
async def get_items_for_merchant(
    merchant_id: str,
    item_id: Optional[str] = Query(None, alias="itemId"),
    limit: int = Query(5, ge=1),
    offset: int = Query(0, ge=0),
    name: Optional[str] = Query(None),
    product_category: Optional[ItemProductCategoryEnum] = Query(
        None, alias="productCategory"
    ),
    created_at: Optional[SortOrder] = Query(None, alias="createdAt"),
    session: AsyncSession = Depends(get_db),
):
    exists = await repo.merchant_exists(session, merchant_id)
    if not exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "NotFound",
                "message": f"Merchant with id '{merchant_id}' not found",
            },
        )

    sort = created_at.value if created_at else None

    items, total = await repo.list_items(
        session,
        merchant_id=merchant_id,
        item_id=item_id,
        name=name,
        category=product_category,
        created_at=sort,
        limit=limit,
        offset=offset,
    )

    return {"data": items, "meta": {"limit": limit, "offset": offset, "total": total}}
