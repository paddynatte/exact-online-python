"""Stock Count Lines API resource."""

from typing import ClassVar

from exact_online.api.base import BaseAPI, ReadableMixin, WritableMixin
from exact_online.models.stock_count import StockCountLine


class StockCountLinesAPI(
    BaseAPI[StockCountLine],
    ReadableMixin[StockCountLine],
    WritableMixin[StockCountLine],
):
    """API resource for Stock Count Lines.

    Supports: list(), get(), create(), update(), delete()

    Usage:
        # List lines for a stock count
        lines = await client.stock_count_lines.list(
            division=123,
            odata_filter="StockCountID eq guid'stock-count-guid'"
        )

        # Get a specific line
        line = await client.stock_count_lines.get(division=123, id="guid")

        # Create a line
        line = await client.stock_count_lines.create(
            division=123,
            data={
                "stock_count_id": "stock-count-guid",
                "item": "item-guid",
                "quantity_new": 100,
            }
        )
    """

    ENDPOINT: ClassVar[str] = "/inventory/StockCountLines"
    MODEL: ClassVar[type[StockCountLine]] = StockCountLine
    ID_FIELD: ClassVar[str] = "ID"
