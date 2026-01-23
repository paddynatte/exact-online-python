"""Goods Receipt Lines API resource."""

from typing import ClassVar

from exact_online.api.base import BaseAPI, ReadableMixin, WritableMixin
from exact_online.models.goods_receipt import GoodsReceiptLine


class GoodsReceiptLinesAPI(
    BaseAPI[GoodsReceiptLine],
    ReadableMixin[GoodsReceiptLine],
    WritableMixin[GoodsReceiptLine],
):
    """API resource for Goods Receipt Lines.

    Supports: list(), get(), create(), update(), delete()

    Usage:
        # List lines for a goods receipt
        lines = await client.goods_receipt_lines.list(
            division=123,
            odata_filter="GoodsReceiptID eq guid'receipt-guid'"
        )

        # Get a specific line
        line = await client.goods_receipt_lines.get(division=123, id="guid")

        # Create a line
        line = await client.goods_receipt_lines.create(
            division=123,
            data={
                "goods_receipt_id": "receipt-guid",
                "item": "item-guid",
                "quantity_received": 100,
            }
        )
    """

    ENDPOINT: ClassVar[str] = "/purchaseorder/GoodsReceiptLines"
    MODEL: ClassVar[type[GoodsReceiptLine]] = GoodsReceiptLine
    ID_FIELD: ClassVar[str] = "ID"
