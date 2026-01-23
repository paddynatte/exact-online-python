"""Stock Counts API resource."""

from typing import ClassVar

from exact_online.api.base import BaseAPI, ReadableMixin, SyncableMixin, WritableMixin
from exact_online.models.stock_count import StockCount


class StockCountsAPI(
    BaseAPI[StockCount],
    ReadableMixin[StockCount],
    WritableMixin[StockCount],
    SyncableMixin[StockCount],
):
    """API resource for Stock Counts.

    Supports:
    - list(), get(), create(), update(), delete()
    - sync() uses Modified filter (no Sync API support)

    Usage:
        counts = await client.stock_counts.list(division=123)

        count = await client.stock_counts.get(division=123, id="guid")

        count = await client.stock_counts.create(
            division=123,
            data={
                "warehouse": "guid",
                "stock_count_lines": [...]
            }
        )

        # Incremental sync (uses Modified filter)
        async for count in client.stock_counts.sync(division):
            await db.merge(count)
    """

    ENDPOINT: ClassVar[str] = "/inventory/StockCounts"
    MODEL: ClassVar[type[StockCount]] = StockCount
    ID_FIELD: ClassVar[str] = "StockCountID"
    RESOURCE_NAME: ClassVar[str] = "stock_counts"
