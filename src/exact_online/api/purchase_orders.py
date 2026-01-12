"""Purchase Orders API resource."""

from typing import ClassVar

from exact_online.api.base import BaseAPI
from exact_online.models.purchase_order import PurchaseOrder


class PurchaseOrdersAPI(BaseAPI[PurchaseOrder]):
    """API resource for Purchase Orders.

    Supports full CRUD operations and sync (bulk, up to 1000 records).

    Usage:
        orders = await client.purchase_orders.list(division=123)

        order = await client.purchase_orders.get(division=123, id="guid")

        order = await client.purchase_orders.create(
            division=123,
            data={"Supplier": "guid", "PurchaseOrderLines": [...]}
        )

        result = await client.purchase_orders.sync(division=123, timestamp=0)
    """

    ENDPOINT: ClassVar[str] = "/purchaseorder/PurchaseOrders"
    SYNC_ENDPOINT: ClassVar[str | None] = "/sync/PurchaseOrder/PurchaseOrders"
    MODEL: ClassVar[type[PurchaseOrder]] = PurchaseOrder
    ID_FIELD: ClassVar[str] = "PurchaseOrderID"
