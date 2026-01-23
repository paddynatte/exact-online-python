"""Goods Receipts API resource."""

from typing import ClassVar

from exact_online.api.base import BaseAPI, ReadableMixin, SyncableMixin, WritableMixin
from exact_online.models.goods_receipt import GoodsReceipt


class GoodsReceiptsAPI(
    BaseAPI[GoodsReceipt],
    ReadableMixin[GoodsReceipt],
    WritableMixin[GoodsReceipt],
    SyncableMixin[GoodsReceipt],
):
    """API resource for Goods Receipts.

    Supports:
    - list(), get(), create(), update(), delete()
    - sync() uses Modified filter (no Sync API support)

    Usage:
        receipts = await client.goods_receipts.list(division=123)

        receipt = await client.goods_receipts.get(division=123, id="guid")

        receipt = await client.goods_receipts.create(
            division=123,
            data={
                "supplier": "guid",
                "goods_receipt_lines": [...]
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
