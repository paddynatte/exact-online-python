"""Sales Orders API resource."""

from typing import ClassVar

from exact_online.api.base import BaseAPI, ReadableMixin, SyncableMixin, WritableMixin
from exact_online.models.sales_order import SalesOrder


class SalesOrdersAPI(
    BaseAPI[SalesOrder],
    ReadableMixin[SalesOrder],
    WritableMixin[SalesOrder],
    SyncableMixin[SalesOrder],
):
    """API resource for Sales Orders.

    Supports:
    - list(), get(), create(), update(), delete()
    - sync() uses Sync API (1000 records/call)

    Usage:
        orders = await client.sales_orders.list(division=123)

        order = await client.sales_orders.get(division=123, id="guid")

        order = await client.sales_orders.create(
            division=123,
            data={"ordered_by": "guid", "sales_order_lines": [...]}
        )

        # Incremental sync
        async for order in client.sales_orders.sync(division):
            await db.merge(order)
    """

    ENDPOINT: ClassVar[str] = "/salesorder/SalesOrders"
    SYNC_ENDPOINT: ClassVar[str] = "/sync/SalesOrder/SalesOrderHeaders"
    MODEL: ClassVar[type[SalesOrder]] = SalesOrder
    ID_FIELD: ClassVar[str] = "OrderID"
    RESOURCE_NAME: ClassVar[str] = "sales_orders"
