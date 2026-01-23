"""PurchaseItemPrices API resource."""

from typing import ClassVar

from exact_online.api.base import BaseAPI, SyncableMixin
from exact_online.models.purchase_item_price import PurchaseItemPrice


class PurchaseItemPricesAPI(BaseAPI[PurchaseItemPrice], SyncableMixin[PurchaseItemPrice]):
    """API resource for Purchase Item Prices (sync-only).

    Purchase prices for items from suppliers.
    This is a sync-only endpoint - only sync() is supported.
    Uses Sync API (1000 records/call) with timestamp-based filtering.

    To manage prices, use SupplierItems (which has full CRUD).
    This endpoint provides a denormalized view for efficient syncing.

    Usage:
        # Incremental sync (uses Sync API)
        async for price in client.purchase_item_prices.sync(division):
            await db.merge(price)
    """

    ENDPOINT: ClassVar[str] = "/logistics/PurchaseItemPrices"
    SYNC_ENDPOINT: ClassVar[str] = "/sync/Logistics/PurchaseItemPrices"
    MODEL: ClassVar[type[PurchaseItemPrice]] = PurchaseItemPrice
    ID_FIELD: ClassVar[str] = "ID"
    RESOURCE_NAME: ClassVar[str] = "purchase_item_prices"
