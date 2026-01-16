"""Warehouses API resource."""

from typing import ClassVar

from exact_online.api.base import BaseAPI
from exact_online.models.warehouse import Warehouse


class WarehousesAPI(BaseAPI[Warehouse]):
    """API resource for Warehouses.

    Warehouses are locations where inventory is stored.
    Supports full CRUD operations (GET, POST, PUT, DELETE).

    Usage:
        # List all warehouses
        warehouses = await client.warehouses.list(division=123)

        # Get a specific warehouse
        warehouse = await client.warehouses.get(division=123, id="guid")

        # Create a warehouse
        warehouse = await client.warehouses.create(
            division=123,
            data={"code": "WH01", "description": "Main Warehouse"}
        )

        # Update a warehouse
        warehouse = await client.warehouses.update(
            division=123,
            id="guid",
            data={"description": "Updated Description"}
        )

        # Delete a warehouse
        await client.warehouses.delete(division=123, id="guid")
    """

    ENDPOINT: ClassVar[str] = "/inventory/Warehouses"
    MODEL: ClassVar[type[Warehouse]] = Warehouse
    ID_FIELD: ClassVar[str] = "ID"
