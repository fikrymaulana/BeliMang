from typing import Optional

from fastapi import HTTPException
from pydantic import HttpUrl

from .enums import MerchantCategoryEnum
from .repository import MerchantRepository
from .schemas import (
    DetailMerchantResponse,
    ItemResponse,
    LocationSchema,
    MerchantResponse,
)


class MerchantService:
    @staticmethod
    async def get_nearby_merchants(
        session,
        lat: float,
        long: float,
        merchantId: Optional[str],
        merchantCategory: Optional[str],
        name: Optional[str],
        limit: int,
        offset: int,
    ):
        # Validate lat/long
        try:
            lat = float(lat)
            long = float(long)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid latitude or longitude")

        # Validate category
        if (
            merchantCategory
            and merchantCategory not in MerchantCategoryEnum.__members__
        ):
            return {"data": [], "meta": {"limit": limit, "offset": offset, "total": 0}}

        merchants = await MerchantRepository.get_nearby_merchants(
            lat, long, merchantId, merchantCategory, name, limit, offset, session
        )

        # Format response
        data = []
        for m in merchants:
            items = [
                ItemResponse(
                    itemId=str(i.id),
                    name=i.name,
                    productCategory=i.product_category,
                    imageUrl=HttpUrl(i.image_url),
                    price=i.price,
                    quantity=i.quantity,
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
