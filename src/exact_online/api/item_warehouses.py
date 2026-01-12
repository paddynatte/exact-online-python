"""Item Warehouses API resource."""

from typing import ClassVar

from exact_online.api.base import BaseAPI
from exact_online.models.item_warehouse import ItemWarehouse


class ItemWarehousesAPI(BaseAPI[ItemWarehouse]):
    """API resource for Item Warehouses.

    Link items to warehouses with stock level information (bulk, up to 1000 records).

    Usage:
        links = await client.item_warehouses.list(division=123)

        link = await client.item_warehouses.get(division=123, id="guid")

        link = await client.item_warehouses.create(
            division=123,
            data={"Item": "item-guid", "Warehouse": "warehouse-guid"}
        )
    """

    ENDPOINT: ClassVar[str] = "/inventory/ItemWarehouses"
    SYNC_ENDPOINT: ClassVar[str | None] = None
    MODEL: ClassVar[type[ItemWarehouse]] = ItemWarehouse
    ID_FIELD: ClassVar[str] = "ID"
