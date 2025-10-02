import math
from typing import Dict, List, Tuple

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.purchases.models import EstimateItem

from ..merchants.models import Item, Merchant
from ..merchants.repository import MerchantRepository

from .repository import PurchaseRepository
from .schemas import EstimateRequest, EstimateResponse

R_EARTH_KM = 6371.0
COURIER_SPEED_KMH = 40.0
AREA_LIMIT_M2 = 3_000_000  # 3 square kilometers


class PurchaseService:
    @staticmethod
    def _haversine_km(lat1: float, long1: float, lat2: float, long2: float) -> float:
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat_rad = lat2_rad - lat1_rad
        delta_long_rad = math.radians(long2 - long1)

        a = (math.sin(delta_lat_rad / 2) ** 2) + (
            math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_long_rad / 2) ** 2
        )
        central_angle = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R_EARTH_KM * central_angle

    @staticmethod
    def _bbox_area_cartesian_m2(points: List[Tuple[float, float]]) -> float:
        """
        Approx area of bounding box on local Cartesian approximation around center latitude.
        points: list of (lat, long)
        """
        lats = [p[0] for p in points]
        longs = [p[1] for p in points]
        lat_min, lat_max = min(lats), max(lats)
        long_min, long_max = min(longs), max(longs)

        # Meters per degree (approx)
        lat_mid = (lat_min + lat_max) / 2.0
        m_per_deg_lat = 111_132.0
        m_per_deg_long = 111_320.0 * math.cos(math.radians(lat_mid))
        width_m = max(0.0, (long_max - long_min) * m_per_deg_long)
        height_m = max(0.0, (lat_max - lat_min) * m_per_deg_lat)

        return width_m * height_m

    @staticmethod
    def _nearest_neighbor_route_km(
        start_idx: int, coords: List[Tuple[float, float]]
    ) -> float:
        """
        coords: list of (lat, long) for all merchants + last point = user location
        start_idx: index merchant that is starting point
        We will always finish at the last index (user).
        Route: start -> visit all other merchants -> user
        """
        n = len(coords)
        user_idx = n - 1

        to_visit = [i for i in range(n - 1)]  # exclude user
        to_visit.remove(start_idx)

        current = start_idx
        total_km = 0.0

        # Visit remaining merchants greedily
        while to_visit:
            dists = [
                (
                    i,
                    PurchaseService._haversine_km(
                        coords[current][0],
                        coords[current][1],
                        coords[i][0],
                        coords[i][1],
                    ),
                )
                for i in to_visit
            ]
            next, dist = min(dists, key=lambda x: x[1])
            total_km += dist
            current = next
            to_visit.remove(next)

        # Go to user at the end
        d_last = PurchaseService._haversine_km(
            coords[current][0],
            coords[current][1],
            coords[user_idx][0],
            coords[user_idx][1],
        )
        total_km += d_last

        return total_km

    @staticmethod
    async def calculate_estimate(
        session: AsyncSession, body: EstimateRequest
    ) -> EstimateResponse:
        # User's coordinates validation
        try:
            u_lat = float(body.userLocation.lat)
            u_long = float(body.userLocation.long)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid user coordinates")
        # No orders validation
        if not body.orders or len(body.orders) == 0:
            raise HTTPException(
                status_code=400, detail="At least one order is required."
            )
        # No starting point validation
        starting_points = sum(1 for o in body.orders if o.isStartingPoint)
        if starting_points != 1:
            raise HTTPException(
                status_code=400,
                detail="Exactly one order must be marked as the starting point.",
            )

        # Get merchants and items
        merchant_ids = [o.merchantId for o in body.orders]
        merchants: Dict[str, Merchant] = await MerchantRepository.get_merchants_by_ids(
            session, merchant_ids
        )
        # 404 if any merchant not found
        missing_merchants = [mid for mid in merchant_ids if mid not in merchants]
        if missing_merchants:
            raise HTTPException(
                status_code=404,
                detail=f"Merchants not found: {', '.join(missing_merchants)}",
            )

        # Get items for each merchant and validate orders
        total_price = 0
        for o in body.orders:
            items_map: Dict[
                str, Item
            ] = await MerchantRepository.get_items_by_merchant_and_item_ids(
                session, o.merchantId, [it.itemId for it in o.items]
            )
            missing_items = [it.itemId for it in o.items if it.itemId not in items_map]
            if missing_items:
                raise HTTPException(
                    status_code=404,
                    detail=f"Items not found for merchant {o.merchantId}: {', '.join(missing_items)}",
                )
            # sum price
            for it in o.items:
                total_price += int(items_map[it.itemId].price) * int(it.quantity)

        # If bounding box area > 3 km^2
        pts = [(u_lat, u_long)]
        pts.extend(
            [
                (
                    float(merchants[o.merchantId].latitude),
                    float(merchants[o.merchantId].longitude),
                )
                for o in body.orders
            ]
        )
        area_m2 = PurchaseService._bbox_area_cartesian_m2(pts)
        if area_m2 > AREA_LIMIT_M2:
            raise HTTPException(
                status_code=400,
                detail="The area covered by the merchants and user location exceeds the limit of 3 square kilometers.",
            )

        # Prepare coordinates for TSP
        # coords: list of (lat, long) for all merchants + last point = user location
        coords: List[tuple] = []
        start_idx = -1
        for idx, o in enumerate(body.orders):
            m = merchants[o.merchantId]
            coords.append((float(m.latitude), float(m.longitude)))
            if o.isStartingPoint:
                start_idx = idx
        coords.append((u_lat, u_long))  # user location at the end

        # if no starting point specified
        if start_idx == -1:
            raise HTTPException(
                status_code=400,
                detail="No starting point specified among the merchants.",
            )

        # Nearest neighbor TSP -> total distance in km
        total_km = PurchaseService._nearest_neighbor_route_km(start_idx, coords)

        # Estimate time in minutes (round to integer)
        est_minutes = max(1, round((total_km / COURIER_SPEED_KMH) * 60.0))

        # Create estimate row
        estimate_id = await PurchaseRepository.save_estimate(
            session,
            total_price=total_price,
            est_minutes=est_minutes,
        )

        # Create estimate items rows
        rows = []
        for o in body.orders:
            items_map: Dict[
                str, Item
            ] = await MerchantRepository.get_items_by_merchant_and_item_ids(
                session, o.merchantId, [it.itemId for it in o.items]
            )
            for it in o.items:
                item: Item = items_map[it.itemId]
                rows.append(
                    EstimateItem(
                        estimate_id=estimate_id,
                        item_id=item.id,
                        merchant_id=o.merchantId,
                        quantity=it.quantity,
                        unit_price=item.price,
                        item_name=item.name,
                        product_category=item.product_category,
                        image_url=item.image_url,
                    )
                )
        await PurchaseRepository.bulk_insert_estimate_items(session, rows)
        await session.commit()

        return EstimateResponse(
            totalPrice=total_price,
            estimatedDeliveryTimeInMinutes=est_minutes,
            calculatedEstimateId=estimate_id,
        )
