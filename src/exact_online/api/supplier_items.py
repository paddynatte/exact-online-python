"""Supplier Items API resource."""

from typing import ClassVar

from exact_online.api.base import BaseAPI
from exact_online.models.supplier_item import SupplierItem


class SupplierItemsAPI(BaseAPI[SupplierItem]):
    """API resource for Supplier Items.

    Links suppliers to items and manages purchase prices (bulk, up to 1000 records).

    Usage:  
        items = await client.supplier_items.list(division=123)

        item = await client.supplier_items.get(division=123, id="guid")

        item = await client.supplier_items.create(
            division=123,
            data={"Item": "item-guid", "Supplier": "supplier-guid"}
        )
    """

    ENDPOINT: ClassVar[str] = "/logistics/SupplierItem"
    SYNC_ENDPOINT: ClassVar[str | None] = None
    MODEL: ClassVar[type[SupplierItem]] = SupplierItem
    ID_FIELD: ClassVar[str] = "ID"
