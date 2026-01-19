"""Warehouses API resource."""

from typing import ClassVar

from exact_online.api.base import BaseAPI
from exact_online.models.warehouse import Warehouse


class WarehousesAPI(BaseAPI[Warehouse]):
    """API resource for Warehouses.

    Warehouses are locations where inventory is stored.
    Supports full CRUD operations and sync():
    - list, get, create, update, delete
    - sync() uses Modified filter (no Sync API support)

    Usage:
        warehouses = await client.warehouses.list(division=123)

        warehouse = await client.warehouses.get(division=123, id="guid")

        warehouse = await client.warehouses.create(
            division=123,
            data={"code": "WH01", "description": "Main Warehouse"}
        )

        # Incremental sync (uses Modified filter)
        async for warehouse in client.warehouses.sync(division):
            await db.merge(warehouse)
    """

    ENDPOINT: ClassVar[str] = "/inventory/Warehouses"
    MODEL: ClassVar[type[Warehouse]] = Warehouse
    ID_FIELD: ClassVar[str] = "ID"
    RESOURCE_NAME: ClassVar[str] = "warehouses"
