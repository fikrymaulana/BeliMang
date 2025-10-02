from typing import List

from cuid2 import cuid_wrapper
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.expression import select

from .models import Estimate, EstimateItem

CUID = cuid_wrapper()


class PurchaseRepository:
    @staticmethod
    async def save_estimate(
        session: AsyncSession, total_price: int, est_minutes: int
    ) -> str:
        eid = CUID()
        est = Estimate(id=eid, total_price=total_price, est_minutes=est_minutes)
        session.add(est)
        return str(eid)

    @staticmethod
    async def bulk_insert_estimate_items(
        session: AsyncSession, rows: List[EstimateItem]
    ) -> None:
        session.add_all(rows)

    @staticmethod
    async def get_estimate_with_items(
        session: AsyncSession,
        estimate_id: str,
    ):
        q = (
            select(Estimate)
            .where(Estimate.id == estimate_id)
            .options(
                selectinload(Estimate.items)
            )  # relationship Estimate.items -> list[EstimateItem]
        )
        res = await session.execute(q)
        return res.scalars().first()
