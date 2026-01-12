"""Stock Count Lines API resource."""

from typing import ClassVar

from exact_online.api.base import BaseAPI
from exact_online.models.stock_count_line import StockCountLine


class StockCountLinesAPI(BaseAPI[StockCountLine]):
    """API resource for Stock Count Lines.

    Manage individual lines within stock counts (bulk, up to 1000 records).

    Usage:
        lines = await client.stock_count_lines.list(division=123)

        line = await client.stock_count_lines.get(division=123, id="guid")

        line = await client.stock_count_lines.create(
            division=123,
            data={"StockCountID": "guid", "Item": "guid", "QuantityNew": 100}
        )
    """

    ENDPOINT: ClassVar[str] = "/inventory/StockCountLines"
    SYNC_ENDPOINT: ClassVar[str | None] = None
    MODEL: ClassVar[type[StockCountLine]] = StockCountLine
    ID_FIELD: ClassVar[str] = "ID"
