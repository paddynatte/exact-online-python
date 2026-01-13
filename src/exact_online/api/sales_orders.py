"""Sales Orders API resource."""

from typing import ClassVar

from exact_online.api.base import BaseAPI
from exact_online.models.sales_order import SalesOrder


class SalesOrdersAPI(BaseAPI[SalesOrder]):
    """API resource for Sales Orders.

    Supports full CRUD operations: list, get, create, update, delete.

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
            data={"ordered_by": "guid", "sales_order_lines": [...]}
        )
    """

    ENDPOINT: ClassVar[str] = "/salesorder/SalesOrders"
    MODEL: ClassVar[type[SalesOrder]] = SalesOrder
    ID_FIELD: ClassVar[str] = "OrderID"
