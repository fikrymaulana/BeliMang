from collections.abc import Iterable
from typing import Dict, Optional

from geoalchemy2 import Geography
from geoalchemy2 import functions as geofunc
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from .enums import MerchantCategoryEnum
from .models import Item, Merchant


class MerchantRepository:
    @staticmethod
    async def get_nearby_merchants(
        lat: float,
        long: float,
        merchantId: Optional[str],
        merchantCategory: Optional[str],
        name: Optional[str],
        limit: int,
        offset: int,
        db: AsyncSession,
    ):
        distance_expr = geofunc.ST_Distance(
            Merchant.geog,
            func.cast(func.ST_SetSRID(func.ST_MakePoint(long, lat), 4326), Geography),
        )
        stmt = select(Merchant)

        # If we have a name filter, we need to use a subquery to avoid JOIN issues
        if name:
            # Subquery to get merchant IDs that match the name filter
            subq = (
                select(Merchant.id)
                .outerjoin(Merchant.items)
                .where(
                    or_(Merchant.name.ilike(f"%{name}%"), Item.name.ilike(f"%{name}%"))
                )
                .distinct()
            )

            stmt = select(Merchant).where(Merchant.id.in_(subq))
        else:
            stmt = select(Merchant)

        if merchantId:
            stmt = stmt.where(Merchant.id == merchantId)

        if merchantCategory:
            stmt = stmt.where(
                Merchant.merchant_category == MerchantCategoryEnum[merchantCategory]
            )

        stmt = stmt.order_by(distance_expr).limit(limit).offset(offset)

        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_merchant_by_id(db: AsyncSession, merchant_id: str) -> Merchant | None:
        stmt = select(Merchant).where(Merchant.id == merchant_id)
        result = await db.execute(stmt)
        return result.scalars().first()

    @staticmethod
    async def get_merchants_by_ids(
        db: AsyncSession, merchant_ids: Iterable[str]
    ) -> Dict[str, Merchant]:
        stmt = select(Merchant).where(Merchant.id.in_(merchant_ids))
        result = await db.execute(stmt)
        merchants = result.scalars().all()
        return {str(merchant.id): merchant for merchant in merchants}

    @staticmethod
    async def get_items_by_merchant_and_item_ids(
        db: AsyncSession, merchant_id: str, item_ids: Iterable[str]
    ) -> Dict[str, Item]:
        stmt = select(Item).where(
            Item.merchant_id == merchant_id, Item.id.in_(item_ids)
        )
        result = await db.execute(stmt)
        items = result.scalars().all()
        return {str(item.id): item for item in items}
