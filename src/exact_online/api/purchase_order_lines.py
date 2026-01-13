"""Purchase Order Lines API resource."""

from typing import ClassVar

from exact_online.api.base import BaseAPI
from exact_online.models.purchase_order import PurchaseOrderLine


class PurchaseOrderLinesAPI(BaseAPI[PurchaseOrderLine]):
    """API resource for Purchase Order Lines.

    Supports full CRUD operations: list, get, create, update, delete.

    Usage:
        lines = await client.purchase_order_lines.list(
            division=123,
            odata_filter=f"PurchaseOrderID eq guid'{order_id}'"
        )

        line = await client.purchase_order_lines.get(division=123, id="guid")

        line = await client.purchase_order_lines.create(
            division=123,
            data={"purchase_order_id": "order-guid", "item": "item-guid", ...}
        )
    """

    ENDPOINT: ClassVar[str] = "/purchaseorder/PurchaseOrderLines"
    MODEL: ClassVar[type[PurchaseOrderLine]] = PurchaseOrderLine
    ID_FIELD: ClassVar[str] = "ID"
