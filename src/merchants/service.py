# src/merchants/service.py

from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc
from fastapi import HTTPException
from pydantic import HttpUrl

from . import models
from .enums import MerchantCategoryEnum
from .schemas import (
    AdminMerchantCreate as MerchantCreate,
    DetailMerchantResponse,
    ItemResponse,
    LocationSchema,
    MerchantResponse,
)
from .repository import MerchantRepository


class MerchantService:
    # =========================
    # ====== ADMIN (SYNC) =====
    # =========================

    @staticmethod
    def create_merchant(db: Session, payload: MerchantCreate) -> models.Merchant:
        """
        Buat merchant baru untuk endpoint ADMIN (sync).
        Memetakan skema Admin* ke model versi lead (merchant_category, image_url, latitude, longitude).
        Kolom geog akan terisi otomatis via computed/trigger sesuai migrasi.
        """
        try:
            category_enum = MerchantCategoryEnum[payload.merchantCategory]
        except KeyError:
            raise ValueError("Invalid merchantCategory")

        m = models.Merchant(
            name=payload.name,
            merchant_category=category_enum,
            image_url=str(payload.imageUrl),
            latitude=payload.Location.Lat,
            longitude=payload.Location.Long,  # geog auto (computed/trigger)
        )
        db.add(m)
        db.commit()
        db.refresh(m)
        return m

    @staticmethod
    def list_merchants(
        db: Session,
        merchant_id: Optional[str] = None,
        name: Optional[str] = None,
        category: Optional[str] = None,
        sort_created_at: Optional[str] = None,
        limit: int = 5,
        offset: int = 0,
    ) -> Tuple[List[dict], int]:
        """
        Mengembalikan:
          items: List[dict] yang cocok ke AdminMerchantRead (Location.Lat/Long)
          total: int
        Model yang dipakai: models.Merchant (versi lead).
        """
        query = db.query(models.Merchant)

        if merchant_id:
            query = query.filter(models.Merchant.id == merchant_id)
        if name:
            query = query.filter(models.Merchant.name.ilike(f"%{name}%"))
        if category:
            try:
                category_enum = MerchantCategoryEnum[category]
                query = query.filter(models.Merchant.merchant_category == category_enum)
            except KeyError:
                return [], 0

        if sort_created_at == "asc":
            query = query.order_by(asc(models.Merchant.created_at))
        elif sort_created_at == "desc":
            query = query.order_by(desc(models.Merchant.created_at))

        total = query.count()
        rows: List[models.Merchant] = query.limit(limit).offset(offset).all()

        items = [
            {
                "merchantId": str(r.id),
                "name": r.name,
                "merchantCategory": str(r.merchant_category.name if hasattr(r.merchant_category, "name") else r.merchant_category),
                "imageUrl": r.image_url,
                "Location": {"Lat": r.latitude, "Long": r.longitude},
                "createdAt": r.created_at,
            }
            for r in rows
        ]
        return items, total

    # =========================
    # ====== LEAD (ASYNC) =====
    # =========================

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
        try:
            lat = float(lat)
            long = float(long)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid latitude or longitude")

        if (
            merchantCategory
            and merchantCategory not in MerchantCategoryEnum.__members__
        ):
            return {"data": [], "meta": {"limit": limit, "offset": offset, "total": 0}}

        merchants = await MerchantRepository.get_nearby_merchants(
            lat, long, merchantId, merchantCategory, name, limit, offset, session
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
