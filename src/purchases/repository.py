from collections.abc import Sequence
from typing import List, Optional

from cuid2 import cuid_wrapper
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import or_
from sqlalchemy.sql.expression import select

from ..merchants.enums import MerchantCategoryEnum
from ..merchants.models import Item, Merchant
from .models import Estimate, EstimateItem, Order, OrderItem

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

    @staticmethod
    async def create_order_from_estimate(
        session: AsyncSession, user_id: str, estimate_id: str
    ):
        # Create order
        order = Order(user_id=user_id, estimate_id=estimate_id)
        session.add(order)
        await session.flush()

        # Copy from estimate items to order items
        stmt = select(EstimateItem).where(EstimateItem.estimate_id == estimate_id)
        result = await session.execute(stmt)
        est_items = result.scalars().all()

        items_rows = []
        for ei in est_items:
            oi = OrderItem(
                order_id=order.id,
                item_id=ei.item_id,
                quantity=ei.quantity,
                price=ei.unit_price,
            )
            items_rows.append(oi)
        session.add_all(items_rows)

        return str(order.id)

    @staticmethod
    async def fetch_orders_for_user(
        session: AsyncSession,
        user_id: str,
        merchant_id: Optional[str] = None,
        name: Optional[str] = None,
        merchant_category: Optional[MerchantCategoryEnum] = None,
        limit: int = 5,
        offset: int = 0,
    ) -> Sequence[Order]:
        # Base query: orders for user
        stmt = (
            select(Order)
            .where(Order.user_id == user_id)
            .options(
                selectinload(Order.order_items)
                .selectinload(OrderItem.item)
                .selectinload(Item.merchant)
            )
            .order_by(Order.created_at.desc())
        )

        # If name or merchant_category filters exist, we need to join to those tables
        # Build join-based filters to avoid loading unrelated orders
        if merchant_id or name or merchant_category:
            # join through relationships
            stmt = stmt.join(Order.order_items).join(OrderItem.item).join(Item.merchant)

            if merchant_id:
                stmt = stmt.where(Item.merchant_id == merchant_id)

            if merchant_category:
                stmt = stmt.where(Merchant.merchant_category == merchant_category)

            if name:
                pattern = f"%{name}%"
                stmt = stmt.where(
                    or_(Merchant.name.ilike(pattern), Item.name.ilike(pattern))
                )

            # distinct orders to avoid duplicates due to join
            stmt = stmt.distinct()

        # Pagination
        stmt = stmt.limit(limit).offset(offset)

        result = await session.execute(stmt)
        orders = result.scalars().unique().all()
        return orders
