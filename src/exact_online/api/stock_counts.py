"""Stock Counts API resource."""

from typing import ClassVar

from exact_online.api.base import BaseAPI
from exact_online.models.stock_count import StockCount


class StockCountsAPI(BaseAPI[StockCount]):
    """API resource for Stock Counts.

    Supports full CRUD operations: list, get, create, update, delete.

    Status values:
        12 - Open (draft)
        21 - Processed

    Note: For creating a StockCount, you must supply StockCountLines,
    StockCountDate, and Warehouse.

    Usage:
        counts = await client.stock_counts.list(division=123)

        count = await client.stock_counts.get(division=123, id="guid")

        count = await client.stock_counts.create(
            division=123,
            data={
                "warehouse": "warehouse-guid",
                "stock_count_date": "2024-01-01",
                "status": 12,  # Open
                "stock_count_lines": [
                    {"item": "item-guid", "quantity_new": 100}
                ]
            }
        )
    """

    ENDPOINT: ClassVar[str] = "/inventory/StockCounts"
    MODEL: ClassVar[type[StockCount]] = StockCount
    ID_FIELD: ClassVar[str] = "StockCountID"
