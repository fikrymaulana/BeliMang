import asyncio
from cuid2 import Cuid
from dotenv import load_dotenv
from geoalchemy2 import WKTElement
from sqlalchemy import text

from .database import async_session
from .merchants.enums import MerchantCategoryEnum, ItemProductCategoryEnum
from .merchants.models import Merchant, Item

load_dotenv()

cuid = Cuid()  # generator cuid2

# ===========================
# MERCHANTS
# ===========================
MERCHANTS = [
    (
        "Warung Kayleen",
        MerchantCategoryEnum.SmallRestaurant,
        "https://cdn.example.com/images/warung_kayleen.jpg",
        -6.200000,
        106.816666,
    ),
    (
        "Bakmi Gading",
        MerchantCategoryEnum.MediumRestaurant,
        "https://cdn.example.com/images/bakmi_gading.png",
        -6.201800,
        106.818600,
    ),
    (
        "Depot Nusantara",
        MerchantCategoryEnum.LargeRestaurant,
        "https://cdn.example.com/images/depot_nusantara.jpg",
        -6.196000,
        106.820000,
    ),
]

# ===========================
# ITEMS
# ===========================
ITEMS = {
    "Warung Kayleen": [
        (
            "Nasi Campur",
            ItemProductCategoryEnum.Food,
            18000,
            "https://cdn.example.com/images/nasi_campur.jpg",
        ),
        (
            "Es Teh",
            ItemProductCategoryEnum.Beverage,
            5000,
            "https://cdn.example.com/images/es_teh.jpg",
        ),
    ],
    "Bakmi Gading": [
        (
            "Bakmi Special",
            ItemProductCategoryEnum.Food,
            25000,
            "https://cdn.example.com/images/bakmi_special.jpg",
        ),
        (
            "Pangsit",
            ItemProductCategoryEnum.Food,
            8000,
            "https://cdn.example.com/images/pangsit.jpg",
        ),
    ],
    "Depot Nusantara": [
        (
            "Ayam Bakar",
            ItemProductCategoryEnum.Food,
            35000,
            "https://cdn.example.com/images/ayam_bakar.jpg",
        ),
        (
            "Sayur Asem",
            ItemProductCategoryEnum.Food,
            15000,
            "https://cdn.example.com/images/sayur_asem.jpg",
        ),
    ],
}


async def seed():
    async with async_session() as session:
        # Bersihkan data lama
        await session.execute(text("DELETE FROM items"))
        await session.execute(text("DELETE FROM merchants"))

        # Insert merchants
        merchant_map = {}
        for name, category, image, lat, lon in MERCHANTS:
            mid = cuid.generate()  # pakai cuid2
            m = Merchant(
                id=mid,
                name=name,
                merchant_category=category,
                image_url=image,
                latitude=lat,
                longitude=lon,
                geog=WKTElement(f"POINT({lon} {lat})", srid=4326),
            )
            session.add(m)
            merchant_map[name] = mid
        await session.commit()

        # Insert items
        for merchant_name, items in ITEMS.items():
            mid = merchant_map[merchant_name]
            for name, pc_enum, price, image_url in items:
                it = Item(
                    id=cuid.generate(),
                    merchant_id=mid,
                    name=name,
                    product_category=pc_enum,
                    price=price,
                    quantity=10,  # default stock
                    image_url=image_url,
                )
                session.add(it)
        await session.commit()

        print("✅ Seeding merchants and items completed (pakai cuid2).")


if __name__ == "__main__":
    asyncio.run(seed())
