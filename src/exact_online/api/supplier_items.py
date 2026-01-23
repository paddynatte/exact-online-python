"""Supplier Items API resource."""

from typing import ClassVar

from exact_online.api.base import BaseAPI, ReadableMixin, WritableMixin
from exact_online.models.supplier_item import SupplierItem


class SupplierItemsAPI(
    BaseAPI[SupplierItem],
    ReadableMixin[SupplierItem],
    WritableMixin[SupplierItem],
):
    """API resource for Supplier Items.

    Links suppliers to items with purchase prices, units, and lead times.

    Supports: list(), get(), create(), update(), delete()

    Usage:
        # List all supplier items
        items = await client.supplier_items.list(division=123)

        # List items for a specific supplier
        items = await client.supplier_items.list(
            division=123,
            odata_filter="Supplier eq guid'supplier-guid'"
        )

        # Get a specific supplier item
        item = await client.supplier_items.get(division=123, id="guid")

        # Create a supplier item
        item = await client.supplier_items.create(
            division=123,
            data={
                "supplier": "supplier-guid",
                "item": "item-guid",
                "purchase_price": 10.00,
            }
        )
    """

    ENDPOINT: ClassVar[str] = "/logistics/SupplierItem"
    MODEL: ClassVar[type[SupplierItem]] = SupplierItem
    ID_FIELD: ClassVar[str] = "ID"
