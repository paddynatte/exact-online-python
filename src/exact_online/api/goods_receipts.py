"""Goods Receipts API resource."""

from typing import ClassVar

from exact_online.api.base import BaseAPI
from exact_online.models.goods_receipt import GoodsReceipt


class GoodsReceiptsAPI(BaseAPI[GoodsReceipt]):
    """API resource for Goods Receipts.

    Supports full CRUD operations and sync():
    - list, get, create, update, delete
    - sync() uses Modified filter (no Sync API support)

    Note: For creating a GoodsReceipt, you must supply one or more
    GoodsReceiptLines and a ReceiptDate.

    Usage:
        receipts = await client.goods_receipts.list(division=123)

        receipt = await client.goods_receipts.get(division=123, id="guid")

        receipt = await client.goods_receipts.create(
            division=123,
            data={
                "receipt_date": "2024-01-01",
                "goods_receipt_lines": [
                    {"item": "item-guid", "quantity_received": 10}
                ]
            }
        )

        # Incremental sync (uses Modified filter)
        async for receipt in client.goods_receipts.sync(division):
            await db.merge(receipt)
    """

    ENDPOINT: ClassVar[str] = "/purchaseorder/GoodsReceipts"
    MODEL: ClassVar[type[GoodsReceipt]] = GoodsReceipt
    ID_FIELD: ClassVar[str] = "ID"
    RESOURCE_NAME: ClassVar[str] = "goods_receipts"
