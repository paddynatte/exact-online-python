"""Goods Receipt Lines API resource."""

from typing import ClassVar

from exact_online.api.base import BaseAPI
from exact_online.models.goods_receipt import GoodsReceiptLine


class GoodsReceiptLinesAPI(BaseAPI[GoodsReceiptLine]):
    """API resource for Goods Receipt Lines.

    Supports full CRUD operations: list, get, create, update, delete.

    Usage:
        lines = await client.goods_receipt_lines.list(
            division=123,
            odata_filter=f"GoodsReceiptID eq guid'{receipt_id}'"
        )

        line = await client.goods_receipt_lines.get(division=123, id="guid")

        line = await client.goods_receipt_lines.create(
            division=123,
            data={"goods_receipt_id": "receipt-guid", "item": "item-guid", ...}
        )
    """

    ENDPOINT: ClassVar[str] = "/purchaseorder/GoodsReceiptLines"
    MODEL: ClassVar[type[GoodsReceiptLine]] = GoodsReceiptLine
    ID_FIELD: ClassVar[str] = "ID"
