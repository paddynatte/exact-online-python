"""Shop Orders API resource."""

from typing import ClassVar

from exact_online.api.base import BaseAPI
from exact_online.models.shop_order import ShopOrder


class ShopOrdersAPI(BaseAPI[ShopOrder]):
    """API resource for Shop Orders.

    Supports full CRUD operations and sync (bulk, up to 1000 records).

    Status values:
        10 - Open
        20 - In process
        30 - Finished
        40 - Completed

    Usage:
        orders = await client.shop_orders.list(division=123)

        order = await client.shop_orders.get(division=123, id="guid")

        order = await client.shop_orders.create(
            division=123,
            data={"Item": "guid", "PlannedQuantity": 100}
        )

        result = await client.shop_orders.sync(division=123, timestamp=0)
    """

    ENDPOINT: ClassVar[str] = "/manufacturing/ShopOrders"
    SYNC_ENDPOINT: ClassVar[str | None] = "/sync/Manufacturing/ShopOrders"
    MODEL: ClassVar[type[ShopOrder]] = ShopOrder
    ID_FIELD: ClassVar[str] = "ID"
