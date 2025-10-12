import enum


class MerchantCategoryEnum(str, enum.Enum):
    SmallRestaurant = "SmallRestaurant"
    MediumRestaurant = "MediumRestaurant"
    LargeRestaurant = "LargeRestaurant"
    MerchandiseRestaurant = "MerchandiseRestaurant"
    BoothKiosk = "BoothKiosk"
    ConvenienceStore = "ConvenienceStore"

    __pg_name__ = "merchant_category_enum"


class ItemProductCategoryEnum(str, enum.Enum):
    Beverage = "Beverage"
    Food = "Food"
    Snack = "Snack"
    Condiments = "Condiments"
    Additions = "Additions"

    __pg_name__ = "item_product_category_enum"
