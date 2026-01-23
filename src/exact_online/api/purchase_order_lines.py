"""Purchase Order Lines API resource."""

from typing import ClassVar

from exact_online.api.base import BaseAPI, ReadableMixin, WritableMixin
from exact_online.models.purchase_order import PurchaseOrderLine


class PurchaseOrderLinesAPI(
    BaseAPI[PurchaseOrderLine],
    ReadableMixin[PurchaseOrderLine],
    WritableMixin[PurchaseOrderLine],
):
    """API resource for Purchase Order Lines.

    Supports: list(), get(), create(), update(), delete()

    Usage:
        # List lines for a purchase order
        lines = await client.purchase_order_lines.list(
            division=123,
            odata_filter="PurchaseOrderID eq guid'order-guid'"
        )

        # Get a specific line
        line = await client.purchase_order_lines.get(division=123, id="guid")

        # Create a line
        line = await client.purchase_order_lines.create(
            division=123,
            data={
                "purchase_order_id": "order-guid",
                "item": "item-guid",
                "quantity": 100,
            }
        )
    """

    ENDPOINT: ClassVar[str] = "/purchaseorder/PurchaseOrderLines"
    MODEL: ClassVar[type[PurchaseOrderLine]] = PurchaseOrderLine
    ID_FIELD: ClassVar[str] = "ID"
