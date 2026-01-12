"""Purchase Item Prices API resource (sync-only)."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, cast

from exact_online.models.base import SyncResult
from exact_online.models.purchase_item_price import PurchaseItemPrice

if TYPE_CHECKING:
    from exact_online.client import Client


class PurchaseItemPricesAPI:
    """API resource for Purchase Item Prices.

    This is a sync-only API - no CRUD operations are available.
    Use sync() to retrieve purchase prices (bulk, up to 1000 records).

    Note: Does not support $select=* due to large number of properties.

    Usage:
        result = await client.purchase_item_prices.sync(division=123, timestamp=0)

        result = await client.purchase_item_prices.sync(
            division=123,
            timestamp=stored_timestamp
        )
    """

    SYNC_ENDPOINT = "/sync/Logistics/PurchaseItemPrices"

    def __init__(self, client: Client) -> None:
        """Initialize the API resource."""
        self._client = client

    async def sync(
        self,
        division: int,
        *,
        timestamp: int = 0,
        select: Sequence[str] | None = None,
    ) -> SyncResult[PurchaseItemPrice]:
        """Sync purchase item prices.

        Returns up to 1000 records modified since the given timestamp.
        Use the returned timestamp for the next sync call.

        Note: Only timestamp filter is allowed for optimal performance.

        Args:
            division: The division ID.
            timestamp: Sync from this timestamp (0 = get all).
            select: Optional list of fields (do not use '*').

        Returns:
            SyncResult containing items, next timestamp, and has_more flag.
        """
        params: dict[str, Any] = {}

        if timestamp > 0:
            params["$filter"] = f"Timestamp gt {timestamp}"

        if select:
            params["$select"] = ",".join(select)

        response = await self._client.request(
            method="GET",
            endpoint=self.SYNC_ENDPOINT,
            division=division,
            params=params,
        )

        data = response.get("d", {})
        results = data if isinstance(data, list) else data.get("results", [])

        items = cast(
            list[PurchaseItemPrice],
            [PurchaseItemPrice.model_validate(item) for item in results],
        )

        next_timestamp = timestamp
        for item in results:
            item_ts = item.get("Timestamp") or 0
            if isinstance(item_ts, str):
                try:
                    item_ts = int(item_ts)
                except ValueError:
                    item_ts = 0
            if item_ts > next_timestamp:
                next_timestamp = item_ts

        has_more = len(results) >= 1000

        return SyncResult(
            items=items,
            timestamp=next_timestamp,
            has_more=has_more,
        )
