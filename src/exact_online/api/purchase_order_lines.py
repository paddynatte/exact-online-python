"""Purchase Order Lines API resource."""

from typing import ClassVar

from exact_online.api.base import BaseAPI
from exact_online.models.purchase_order import PurchaseOrderLine


class PurchaseOrderLinesAPI(BaseAPI[PurchaseOrderLine]):
    """API resource for Purchase Order Lines.

    Supports CRUD operations but NOT sync (no sync endpoint available) (bulk, up to 1000 records).

    Usage:
        lines = await client.purchase_order_lines.list(
            division=123,
            filter=f"PurchaseOrderID eq guid'{order_id}'"
        )

        line = await client.purchase_order_lines.get(division=123, id="guid")

        line = await client.purchase_order_lines.create(
            division=123,
            data={"PurchaseOrderID": "order-guid", "Item": "item-guid", ...}
        )
    """

    ENDPOINT: ClassVar[str] = "/purchaseorder/PurchaseOrderLines"
    SYNC_ENDPOINT: ClassVar[str | None] = None
    MODEL: ClassVar[type[PurchaseOrderLine]] = PurchaseOrderLine
    ID_FIELD: ClassVar[str] = "ID"
