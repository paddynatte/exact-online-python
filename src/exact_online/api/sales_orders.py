"""Sales Orders API resource."""

from typing import ClassVar

from exact_online.api.base import BaseAPI
from exact_online.models.sales_order import SalesOrder


class SalesOrdersAPI(BaseAPI[SalesOrder]):
    """API resource for Sales Orders.

    Supports full CRUD operations and sync (bulk, up to 1000 records).

    Status values:
        12 - Open
        20 - Partial
        21 - Complete
        45 - Cancelled

    Usage:
        orders = await client.sales_orders.list(division=123)

        order = await client.sales_orders.get(division=123, id="guid")

        order = await client.sales_orders.create(
            division=123,
            data={"OrderedBy": "guid", "SalesOrderLines": [...]}
        )

        result = await client.sales_orders.sync(division=123, timestamp=0)
    """

    ENDPOINT: ClassVar[str] = "/salesorder/SalesOrders"
    SYNC_ENDPOINT: ClassVar[str | None] = "/sync/SalesOrder/SalesOrderHeaders"
    MODEL: ClassVar[type[SalesOrder]] = SalesOrder
    ID_FIELD: ClassVar[str] = "OrderID"
