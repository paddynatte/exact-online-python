"""Items API resource."""

from typing import ClassVar

from exact_online.api.base import BaseAPI
from exact_online.models.item import Item


class ItemsAPI(BaseAPI[Item]):
    """API resource for Items (products/services).

    Supports full CRUD operations and sync.

    Usage:
        # List items
        items = await client.items.list(division=123)

        # Get specific item
        item = await client.items.get(division=123, id="guid")

        # List all items (auto-pagination)
        async for item in client.items.list_all(division=123):
            print(item.code, item.description)

        # Sync (bulk, up to 1000 records)
        result = await client.items.sync(division=123, timestamp=0)
    """

    ENDPOINT: ClassVar[str] = "/logistics/Items"
    SYNC_ENDPOINT: ClassVar[str | None] = "/sync/Logistics/Items"
    MODEL: ClassVar[type[Item]] = Item
    ID_FIELD: ClassVar[str] = "ID"
