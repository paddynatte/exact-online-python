"""Sales Item Prices API resource."""

from typing import ClassVar

from exact_online.api.base import BaseAPI
from exact_online.models.sales_item_price import SalesItemPrice


class SalesItemPricesAPI(BaseAPI[SalesItemPrice]):
    """API resource for Sales Item Prices.

    Manage sales prices and price agreements for items (bulk, up to 1000 records).

    Usage:
        prices = await client.sales_item_prices.list(division=123)

        price = await client.sales_item_prices.get(division=123, id="guid")

        price = await client.sales_item_prices.create(
            division=123,
            data={"Item": "guid", "Account": "customer-guid", "Price": 99.99}
        )

        price = await client.sales_item_prices.create(
            division=123,
            data={"Item": "guid", "Price": 79.99}
        )
    """

    ENDPOINT: ClassVar[str] = "/logistics/SalesItemPrices"
    SYNC_ENDPOINT: ClassVar[str | None] = None
    MODEL: ClassVar[type[SalesItemPrice]] = SalesItemPrice
    ID_FIELD: ClassVar[str] = "ID"
