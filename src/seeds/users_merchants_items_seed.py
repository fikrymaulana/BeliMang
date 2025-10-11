import asyncio

from cuid2 import cuid_wrapper
from dotenv import load_dotenv
from geoalchemy2 import WKTElement
from passlib.context import CryptContext
from sqlalchemy import text

from ..admin.models import User, UserType
from ..database import async_session
from ..merchants.enums import ItemProductCategoryEnum, MerchantCategoryEnum
from ..merchants.models import Item, Merchant
from ..purchases.models import Order  # don't remove, for relationship purposes

load_dotenv()

cuid = cuid_wrapper()  # generator cuid2
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ===========================
# USERS
# ===========================
USERS = [
    {
        "username": "alice123",
        "email": "alice@example.com",
        "password": "alicepass",
        "user_type": UserType.user,
    },
    {
        "username": "bob456",
        "email": "bob@example.com",
        "password": "bobpass",
        "user_type": UserType.user,
    },
    {
        "username": "admin001",
        "email": "admin@example.com",
        "password": "adminpass",
        "user_type": UserType.admin,
    },
]

# ===========================
# MERCHANTS
# name, category, image, lat, lon
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
    (
        "Kios Mart",
        MerchantCategoryEnum.ConvenienceStore,
        "https://cdn.example.com/images/kios_mart.png",
        -6.202500,
        106.812300,
    ),
    (
        "Booth Soto Kujang",
        MerchantCategoryEnum.BoothKiosk,
        "https://cdn.example.com/images/booth_soto.jpg",
        -6.205000,
        106.817500,
    ),
    (
        "Merchandise Corner",
        MerchantCategoryEnum.MerchandiseRestaurant,
        "https://cdn.example.com/images/merch_corner.jpg",
        -6.198500,
        106.819200,
    ),
    (
        "Cafe Pelangi",
        MerchantCategoryEnum.MediumRestaurant,
        "https://cdn.example.com/images/cafe_pelangi.jpg",
        -6.203200,
        106.815400,
    ),
    (
        "Nasi Goreng Bu Rini",
        MerchantCategoryEnum.SmallRestaurant,
        "https://cdn.example.com/images/nasi_goreng_rini.jpg",
        -6.199900,
        106.814800,
    ),
    (
        "Roti Bakar 88",
        MerchantCategoryEnum.BoothKiosk,
        "https://cdn.example.com/images/roti_bakar88.jpg",
        -6.200900,
        106.817000,
    ),
    (
        "24/7 Convenience",
        MerchantCategoryEnum.ConvenienceStore,
        "https://cdn.example.com/images/247_convenience.jpg",
        -6.197700,
        106.816100,
    ),
]

# ===========================
# ITEMS
# (name, category_enum, price, image_url)
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
        (
            "Kerupuk",
            ItemProductCategoryEnum.Snack,
            3000,
            "https://cdn.example.com/images/kerupuk.jpg",
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
        (
            "Teh Botol",
            ItemProductCategoryEnum.Beverage,
            7000,
            "https://cdn.example.com/images/teh_botel.jpg",
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
        (
            "Sambal Terasi",
            ItemProductCategoryEnum.Condiments,
            5000,
            "https://cdn.example.com/images/sambal_terasi.jpg",
        ),
    ],
    "Kios Mart": [
        (
            "Air Mineral",
            ItemProductCategoryEnum.Beverage,
            3000,
            "https://cdn.example.com/images/air_mineral.jpg",
        ),
        (
            "Roti",
            ItemProductCategoryEnum.Snack,
            7000,
            "https://cdn.example.com/images/roti.jpg",
        ),
    ],
    "Booth Soto Kujang": [
        (
            "Soto",
            ItemProductCategoryEnum.Food,
            20000,
            "https://cdn.example.com/images/soto.jpg",
        ),
        (
            "Kerupuk",
            ItemProductCategoryEnum.Snack,
            3000,
            "https://cdn.example.com/images/kerupuk.jpg",
        ),
    ],
    "Merchandise Corner": [
        (
            "T-Shirt",
            ItemProductCategoryEnum.Additions,
            90000,
            "https://cdn.example.com/images/tshirt.jpg",
        ),
        (
            "Sticker",
            ItemProductCategoryEnum.Additions,
            15000,
            "https://cdn.example.com/images/sticker.jpg",
        ),
    ],
    "Cafe Pelangi": [
        (
            "Americano",
            ItemProductCategoryEnum.Beverage,
            25000,
            "https://cdn.example.com/images/americano.jpg",
        ),
        (
            "Cappuccino",
            ItemProductCategoryEnum.Beverage,
            30000,
            "https://cdn.example.com/images/cappuccino.jpg",
        ),
        (
            "Croissant",
            ItemProductCategoryEnum.Snack,
            18000,
            "https://cdn.example.com/images/croissant.jpg",
        ),
    ],
    "Nasi Goreng Bu Rini": [
        (
            "Nasi Goreng",
            ItemProductCategoryEnum.Food,
            20000,
            "https://cdn.example.com/images/nasi_goreng.jpg",
        ),
        (
            "Teh Manis",
            ItemProductCategoryEnum.Beverage,
            5000,
            "https://cdn.example.com/images/teh_manis.jpg",
        ),
    ],
    "Roti Bakar 88": [
        (
            "Roti Bakar Coklat",
            ItemProductCategoryEnum.Snack,
            12000,
            "https://cdn.example.com/images/roti_bakar_coklat.jpg",
        ),
        (
            "Susu Panas",
            ItemProductCategoryEnum.Beverage,
            8000,
            "https://cdn.example.com/images/susu_panas.jpg",
        ),
    ],
    "24/7 Convenience": [
        (
            "Indomie Goreng",
            ItemProductCategoryEnum.Food,
            12000,
            "https://cdn.example.com/images/indomie_goreng.jpg",
        ),
        (
            "Kopi Kaleng",
            ItemProductCategoryEnum.Beverage,
            9000,
            "https://cdn.example.com/images/kopi_kaleng.jpg",
        ),
    ],
}


async def seed():
    async with async_session() as session:
        # ============= CLEAN =============
        await session.execute(text("DELETE FROM order_items"))
        await session.execute(text("DELETE FROM orders"))
        await session.execute(text("DELETE FROM estimate_items"))
        await session.execute(text("DELETE FROM estimates"))
        await session.execute(text("DELETE FROM items"))
        await session.execute(text("DELETE FROM merchants"))
        usernames = tuple(u["username"] for u in USERS)
        #         await session.execute(
        #             text("DELETE FROM users WHERE username = ANY(:usernames)"),
        #             {"usernames": list(usernames)},
        #         )
        #
        #         # ============= USERS =============
        #         for u in USERS:
        #             user = User(
        #                 id=cuid(),
        #                 username=u["username"],
        #                 email=u["email"],
        #                 password_hash=pwd_context.hash(u["password"]),
        #             )
        #             session.add(user)
        #         await session.commit()

        # ============= MERCHANTS =========
        merchant_id_by_name: dict[str, str] = {}
        for name, category, image, lat, lon in MERCHANTS:
            mid = cuid()  # cuid2 string
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
            merchant_id_by_name[name] = mid
        await session.commit()

        # ============= ITEMS =============
        for merchant_name, items in ITEMS.items():
            mid = merchant_id_by_name[merchant_name]
            for name, pc_enum, price, image_url in items:
                it = Item(
                    id=cuid(),
                    merchant_id=mid,
                    name=name,
                    product_category=pc_enum,
                    price=price,
                    image_url=image_url,
                )
                session.add(it)
        await session.commit()

        print(
            "✅ Seeding users, merchants, and items completed (cuid2 for merchants & items)."
        )


if __name__ == "__main__":
    asyncio.run(seed())
