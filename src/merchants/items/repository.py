# src/merchants/items/repository.py
from __future__ import annotations
from typing import Optional, Tuple, List, Dict, Any
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from cuid2 import cuid_wrapper

CUID = cuid_wrapper()
VALID_ITEM_CATEGORIES = {"Beverage", "Food", "Snack", "Condiments", "Additions"}

async def merchant_exists(db: AsyncSession, merchant_id: str) -> bool:
    res = await db.execute(text("SELECT 1 FROM merchants WHERE id = :id"), {"id": merchant_id})
    return res.scalar() is not None

async def create_item(
    db: AsyncSession,
    merchant_id: str,
    data: Dict[str, Any],
) -> str:
    # --- normalisasi + validasi minimal ---
    name = data.get("name")
    if not name or not isinstance(name, str):
        raise ValueError("name is required")

    try:
        price = int(data.get("price"))
    except Exception:
        raise ValueError("price must be an integer")
    if price <= 0:
        raise ValueError("price must be > 0")

    category = data.get("category") or data.get("productCategory") or data.get("product_category")
    if hasattr(category, "value"):
        category = category.value
    if category not in VALID_ITEM_CATEGORIES:
        raise ValueError(f"productCategory must be one of {sorted(VALID_ITEM_CATEGORIES)}")

    image_url = (data.get("imageUrl") or data.get("image_url") or "")
    image_url = str(image_url)

    item_id = CUID()

    try:
        row = (
            await db.execute(
                text(
                    """
                    INSERT INTO items (id, merchant_id, name, price, product_category, image_url)
                    VALUES (:id, :merchant_id, :name, :price, :product_category, :image_url)
                    RETURNING id
                    """
                ),
                {
                    "id": item_id,
                    "merchant_id": merchant_id,
                    "name": name,
                    "price": price,
                    "product_category": category,
                    "image_url": image_url,
                },
            )
        ).fetchone()
        await db.commit()
    except Exception:
        await db.rollback()
        raise

    return row[0]

async def list_items(
    db: AsyncSession,
    *,
    merchant_id: str,
    item_id: Optional[str] = None,
    name: Optional[str] = None,
    category: Optional[str] = None,
    created_at: Optional[str] = None,  # "asc" | "desc"
    limit: int = 5,
    offset: int = 0,
) -> Tuple[List[Dict[str, Any]], int]:
    where = ["merchant_id = :merchant_id"]
    params: Dict[str, Any] = {"merchant_id": merchant_id, "limit": limit, "offset": offset}

    if item_id:
        where.append("id = :item_id"); params["item_id"] = item_id
    if name:
        where.append("name ILIKE :name"); params["name"] = f"%{name}%"
    if category:
        where.append("product_category = :category"); params["category"] = category

    where_sql = " AND ".join(where)
    order = "created_at ASC" if created_at == "asc" else "created_at DESC"

    total = (
        await db.execute(text(f"SELECT COUNT(*) FROM items WHERE {where_sql}"), params)
    ).scalar() or 0

    rows = (
        await db.execute(
            text(
                f"""
                SELECT
                  id,
                  merchant_id,
                  name,
                  price,
                  product_category AS category,   -- alias utk schema (productCategory)
                  NULLIF(image_url, '') AS image_url,  -- kosong -> null
                  created_at
                FROM items
                WHERE {where_sql}
                ORDER BY {order}
                LIMIT :limit OFFSET :offset
                """
            ),
            params,
        )
    ).mappings().all()

    data = [dict(r) for r in rows]
    return data, int(total)
