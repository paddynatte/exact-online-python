"""Purchase Orders API resource."""

from typing import ClassVar

from exact_online.api.base import BaseAPI
from exact_online.models.purchase_order import PurchaseOrder


class PurchaseOrdersAPI(BaseAPI[PurchaseOrder]):
    """API resource for Purchase Orders.

    Supports full CRUD operations: list, get, create, update, delete.

    Usage:
        orders = await client.purchase_orders.list(division=123)

        order = await client.purchase_orders.get(division=123, id="guid")

        order = await client.purchase_orders.create(
            division=123,
            data={"supplier": "guid", "purchase_order_lines": [...]}
        )
    """

    ENDPOINT: ClassVar[str] = "/purchaseorder/PurchaseOrders"
    MODEL: ClassVar[type[PurchaseOrder]] = PurchaseOrder
    ID_FIELD: ClassVar[str] = "PurchaseOrderID"
