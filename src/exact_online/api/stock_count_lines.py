"""Stock Count Lines API resource."""

from typing import ClassVar

from exact_online.api.base import BaseAPI
from exact_online.models.stock_count import StockCountLine


class StockCountLinesAPI(BaseAPI[StockCountLine]):
    """API resource for Stock Count Lines.

    Supports full CRUD operations: list, get, create, update, delete.

    Usage:
        lines = await client.stock_count_lines.list(
            division=123,
            odata_filter=f"StockCountID eq guid'{count_id}'"
        )

        line = await client.stock_count_lines.get(division=123, id="guid")

        line = await client.stock_count_lines.create(
            division=123,
            data={
                "stock_count_id": "count-guid",
                "item": "item-guid",
                "quantity_new": 100
            }
        )
    """

    ENDPOINT: ClassVar[str] = "/inventory/StockCountLines"
    MODEL: ClassVar[type[StockCountLine]] = StockCountLine
    ID_FIELD: ClassVar[str] = "ID"
