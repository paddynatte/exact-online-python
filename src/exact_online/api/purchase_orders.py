"""Purchase Orders API resource."""

from typing import ClassVar

from exact_online.api.base import BaseAPI, ReadableMixin, SyncableMixin, WritableMixin
from exact_online.models.purchase_order import PurchaseOrder


class PurchaseOrdersAPI(
    BaseAPI[PurchaseOrder],
    ReadableMixin[PurchaseOrder],
    WritableMixin[PurchaseOrder],
    SyncableMixin[PurchaseOrder],
):
    """API resource for Purchase Orders.

    Supports:
    - list(), get(), create(), update(), delete()
    - sync() uses Sync API (1000 records/call)

    Usage:
        orders = await client.purchase_orders.list(division=123)

        order = await client.purchase_orders.get(division=123, id="guid")

        order = await client.purchase_orders.create(
            division=123,
            data={"supplier": "guid", "purchase_order_lines": [...]}
        )

        # Incremental sync
        async for order in client.purchase_orders.sync(division):
            await db.merge(order)
    """

    ENDPOINT: ClassVar[str] = "/purchaseorder/PurchaseOrders"
    SYNC_ENDPOINT: ClassVar[str] = "/sync/PurchaseOrder/PurchaseOrders"
    MODEL: ClassVar[type[PurchaseOrder]] = PurchaseOrder
    ID_FIELD: ClassVar[str] = "PurchaseOrderID"
    RESOURCE_NAME: ClassVar[str] = "purchase_orders"
