# src/merchants/items/repository.py
from typing import Optional, Tuple, List, Dict, Any
from sqlalchemy import text
from sqlalchemy.orm import Session
from cuid2 import cuid_wrapper  # ← generate id sendiri

CUID = cuid_wrapper()  # default panjang aman untuk varchar(36)

# -----------------------------
# Helpers
# -----------------------------
def merchant_exists(db: Session, merchant_id: str) -> bool:
    row = db.execute(
        text("SELECT 1 FROM merchants WHERE id = :id"),
        {"id": merchant_id},
    ).scalar()
    return row is not None


def create_item(
    db: Session,
    merchant_id: str,
    data: Dict[str, Any],
) -> str:
    """
    Insert ke tabel items yang SUDAH ADA (dari Alembic).
    """
    # Ambil dari camelCase ATAU snake_case
    product_category = data.get("productCategory") or data.get("product_category")
    if hasattr(product_category, "value"):
        product_category = product_category.value

    image_url = data.get("imageUrl") or data.get("image_url") or ""
    if image_url is not None:
        image_url = str(image_url)

    price = int(data["price"])  # kolom DB integer & CHECK > 0

    item_id = CUID()  # ← generate id di app layer (karena DB tidak punya default)

    params = {
        "id": item_id,
        "merchant_id": merchant_id,
        "name": data["name"],
        "price": price,
        "product_category": product_category,
        "image_url": image_url,
    }

    row = db.execute(
        text("""
            INSERT INTO items (id, merchant_id, name, price, product_category, image_url)
            VALUES (:id, :merchant_id, :name, :price, :product_category, :image_url)
            RETURNING id
        """),
        params,
    ).fetchone()

    db.commit()
    return row[0]


def list_items(
    db: Session,
    *,
    merchant_id: str,
    item_id: Optional[str] = None,
    name: Optional[str] = None,
    category: Optional[str] = None,
    created_at: Optional[str] = None,  # "asc" | "desc"
    limit: int = 5,
    offset: int = 0,
) -> Tuple[List[Dict[str, Any]], int]:
    """
    Ambil items milik merchant dengan filter optional.
    """
    where = ["merchant_id = :merchant_id"]
    params: Dict[str, Any] = {"merchant_id": merchant_id, "limit": limit, "offset": offset}

    if item_id:
        where.append("id = :item_id"); params["item_id"] = item_id
    if name:
        where.append("name ILIKE :name"); params["name"] = f"%{name}%"
    if category:
        where.append("product_category = :category"); params["category"] = category

    order = "created_at ASC" if created_at == "asc" else "created_at DESC"
    where_sql = " AND ".join(where)

    total = db.execute(
        text(f"SELECT COUNT(*) FROM items WHERE {where_sql}"),
        params,
    ).scalar() or 0

    rows = db.execute(
        text(f"""
            SELECT id, merchant_id, name, price,
                   product_category AS "productCategory",
                   image_url AS "imageUrl", created_at
            FROM items
            WHERE {where_sql}
            ORDER BY {order}
            LIMIT :limit OFFSET :offset
        """),
        params,
    ).mappings().all()

    data = [dict(r) for r in rows]
    return data, int(total)
