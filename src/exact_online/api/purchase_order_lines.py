"""Purchase Order Lines API resource."""

from typing import ClassVar

from exact_online.api.base import BaseAPI
from exact_online.models.purchase_order import PurchaseOrderLine


class PurchaseOrderLinesAPI(BaseAPI[PurchaseOrderLine]):
    """API resource for Purchase Order Lines.

    Supports CRUD operations but NOT sync (no sync endpoint available).

    Usage:
        # List lines for a specific order
        lines = await client.purchase_order_lines.list(
            division=123,
            filter=f"PurchaseOrderID eq guid'{order_id}'"
        )

        # Get specific line
        line = await client.purchase_order_lines.get(division=123, id="guid")

        # Create line
        line = await client.purchase_order_lines.create(
            division=123,
            data={"PurchaseOrderID": "order-guid", "Item": "item-guid", ...}
        )
    """

    ENDPOINT: ClassVar[str] = "/purchaseorder/PurchaseOrderLines"
    SYNC_ENDPOINT: ClassVar[str | None] = None  # Does not support sync
    MODEL: ClassVar[type[PurchaseOrderLine]] = PurchaseOrderLine
    ID_FIELD: ClassVar[str] = "ID"
