"""Shop Orders API resource."""

from typing import ClassVar

from exact_online.api.base import BaseAPI
from exact_online.models.shop_order import ShopOrder


class ShopOrdersAPI(BaseAPI[ShopOrder]):
    """API resource for Shop Orders.

    Supports full CRUD operations and sync():
    - list, get, create, update, delete
    - sync() uses Sync API (1000 records/call)

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
            data={"item": "guid", "planned_quantity": 100}
        )

        # Incremental sync
        async for order in client.shop_orders.sync(division):
            await db.merge(order)
    """

    ENDPOINT: ClassVar[str] = "/manufacturing/ShopOrders"
    SYNC_ENDPOINT: ClassVar[str] = "/sync/Manufacturing/ShopOrders"
    MODEL: ClassVar[type[ShopOrder]] = ShopOrder
    ID_FIELD: ClassVar[str] = "ID"
    RESOURCE_NAME: ClassVar[str] = "shop_orders"