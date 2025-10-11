from typing import List, Optional, Tuple

from fastapi import HTTPException
from geoalchemy2 import WKTElement
from pydantic import HttpUrl
from sqlalchemy import asc, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from . import models
from .enums import MerchantCategoryEnum
from .repository import MerchantRepository
from .schemas import (
    AdminMerchantCreate as MerchantCreate,
)
from .schemas import (
    DetailMerchantResponse,
    ItemResponse,
    LocationSchema,
    MerchantResponse,
)


class MerchantService:
    @staticmethod
    async def create_merchant(
        db: AsyncSession, payload: MerchantCreate
    ) -> models.Merchant:
        """
        Create a new merchant (admin). Uses async DB db.
        Expects payload to contain merchantCategory and location (robust to Location/location naming).
        """
        try:
            category_enum = MerchantCategoryEnum[payload.merchantCategory]
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid merchantCategory")

        loc_obj = getattr(payload, "location", None) or getattr(
            payload, "Location", None
        )
        if loc_obj is None:
            raise HTTPException(status_code=400, detail="Missing location in payload")

        lat = getattr(loc_obj, "lat", None)
        if lat is None:
            lat = getattr(loc_obj, "Lat", None)
        long = getattr(loc_obj, "long", None)
        if long is None:
            long = getattr(loc_obj, "Long", None)

        if lat is None or long is None:
            raise HTTPException(
                status_code=400, detail="Invalid location: missing lat/long"
            )

        m = models.Merchant(
            name=payload.name,
            merchant_category=category_enum,
            image_url=str(payload.imageUrl),
            latitude=float(lat),
            longitude=float(long),
            geog=WKTElement(f"POINT({long} {lat})", srid=4326),
        )

        db.add(m)
        await db.commit()
        await db.refresh(m)
        return m

    @staticmethod
    async def list_merchants(
        db: AsyncSession,
        merchant_id: Optional[str] = None,
        name: Optional[str] = None,
        category: Optional[str] = None,
        sort_created_at: Optional[str] = None,
        limit: int = 5,
        offset: int = 0,
    ) -> Tuple[List[dict], int]:
        """
        Return (items, total) for admin listing. All DB ops are async.
        Items formatted as dict suitable for admin responses.
        """
        where_clauses = []
        if merchant_id:
            where_clauses.append(models.Merchant.id == merchant_id)
        if name:
            where_clauses.append(models.Merchant.name.ilike(f"%{name}%"))
        if category:
            try:
                category_enum = MerchantCategoryEnum[category]
                where_clauses.append(models.Merchant.merchant_category == category_enum)
            except Exception:
                return [], 0

        count_stmt = select(func.count()).select_from(models.Merchant)
        if where_clauses:
            count_stmt = count_stmt.where(*where_clauses)
        total_res = await db.execute(count_stmt)
        total = total_res.scalar_one()

        stmt = select(models.Merchant)
        if where_clauses:
            stmt = stmt.where(*where_clauses)

        if sort_created_at:
            if sort_created_at == "asc":
                stmt = stmt.order_by(asc(models.Merchant.created_at))
            elif sort_created_at == "desc":
                stmt = stmt.order_by(desc(models.Merchant.created_at))
        else:
            stmt = stmt.order_by(desc(models.Merchant.created_at))  # default order

        stmt = stmt.limit(limit).offset(offset)

        result = await db.execute(stmt)
        rows = result.scalars().all()

        items = [
            {
                "merchantId": str(r.id),
                "name": r.name,
                "merchantCategory": r.merchant_category,
                "imageUrl": r.image_url,
                "location": {"lat": r.latitude, "long": r.longitude},
                "createdAt": r.created_at,
            }
            for r in rows
        ]
        return items, int(total)

    @staticmethod
    async def get_nearby_merchants(
        db: AsyncSession,
        lat: float,
        long: float,
        merchantId: Optional[str],
        merchantCategory: Optional[str],
        name: Optional[str],
        limit: int,
        offset: int,
    ):
        try:
            lat = float(lat)
            long = float(long)
        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail="Invalid latitude or longitude")

        if (
            merchantCategory
            and merchantCategory not in MerchantCategoryEnum.__members__
        ):
            return {"data": [], "meta": {"limit": limit, "offset": offset, "total": 0}}

        merchants = await MerchantRepository.get_nearby_merchants(
            lat=lat,
            long=long,
            merchantId=merchantId,
            merchantCategory=merchantCategory,
            name=name,
            limit=limit,
            offset=offset,
            db=db,
        )

        data = []
        for m in merchants:
            items = [
                ItemResponse(
                    itemId=str(i.id),
                    name=i.name,
                    productCategory=i.product_category,
                    imageUrl=HttpUrl(i.image_url),
                    price=i.price,
                    createdAt=i.created_at.isoformat(),
                )
                for i in m.items
            ]

            data.append(
                MerchantResponse(
                    merchant=DetailMerchantResponse(
                        merchantId=str(m.id),
                        name=m.name,
                        merchantCategory=m.merchant_category,
                        imageUrl=HttpUrl(m.image_url),
                        location=LocationSchema(lat=m.latitude, long=m.longitude),
                        createdAt=m.created_at.isoformat(),
                    ),
                    items=items,
                )
            )

        return {
            "data": data,
            "meta": {"limit": limit, "offset": offset, "total": len(data)},
        }
