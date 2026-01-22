"""Items API resource."""

from typing import ClassVar

from exact_online.api.base import BaseAPI
from exact_online.models.item import Item


class ItemsAPI(BaseAPI[Item]):
    """API resource for Logistics Items.

    Items are used in sales, purchase orders, shop orders, and more.
    Supports full CRUD operations and sync():
    - list, get, create, update, delete
    - sync() uses Modified filter (no Sync API support)

    Usage:
        # List all items
        items = await client.items.list(division=123)

        # List only sales items
        sales_items = await client.items.list(
            division=123,
            odata_filter="IsSalesItem eq true"
        )

        # List only purchase items
        purchase_items = await client.items.list(
            division=123,
            odata_filter="IsPurchaseItem eq true"
        )

        # Get specific item
        item = await client.items.get(division=123, id="guid")

        # Create an item
        item = await client.items.create(
            division=123,
            data={
                "code": "ITEM001",
                "description": "My Item",
                "is_sales_item": True,
                "is_purchase_item": True,
            }
        )

        # Incremental sync (uses Modified filter)
        async for item in client.items.sync(division):
            await db.merge(item)
    """

    ENDPOINT: ClassVar[str] = "/logistics/Items"
    MODEL: ClassVar[type[Item]] = Item
    ID_FIELD: ClassVar[str] = "ID"
    RESOURCE_NAME: ClassVar[str] = "items"
