"""Shop Orders API resource."""

from typing import ClassVar

from exact_online.api.base import BaseAPI
from exact_online.models.shop_order import ShopOrder


class ShopOrdersAPI(BaseAPI[ShopOrder]):
    """API resource for Shop Orders.

    Supports full CRUD operations: list, get, create, update, delete.

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
    """

    ENDPOINT: ClassVar[str] = "/manufacturing/ShopOrders"
    MODEL: ClassVar[type[ShopOrder]] = ShopOrder
    ID_FIELD: ClassVar[str] = "ID"
