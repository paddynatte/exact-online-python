"""Supplier Items API resource."""

from typing import ClassVar

from exact_online.api.base import BaseAPI
from exact_online.models.supplier_item import SupplierItem


class SupplierItemsAPI(BaseAPI[SupplierItem]):
    """API resource for Supplier Items.

    Links suppliers to items with purchase prices, units, and lead times.
    Supports full CRUD operations: list, get, create, update, delete.

    Key fields:
        - item: The item being supplied
        - supplier: The supplier
        - purchase_price: Price per purchase unit
        - purchase_unit: Unit code for purchasing (e.g., "BOX")
        - purchase_unit_factor: Multiplier from purchase unit to item unit
        - main_supplier: Whether this is the primary supplier

    Usage:
        # List all supplier items for an item
        items = await client.supplier_items.list(
            division=123,
            odata_filter=f"Item eq guid'{item_id}'"
        )

        # List all items from a supplier
        items = await client.supplier_items.list(
            division=123,
            odata_filter=f"Supplier eq guid'{supplier_id}'"
        )

        # Create supplier-item link
        item = await client.supplier_items.create(
            division=123,
            data={
                "item": "item-guid",
                "supplier": "supplier-guid",
                "purchase_price": 50.00,
                "purchase_unit": "BOX",
                "purchase_unit_factor": 100,
                "main_supplier": True,
            }
        )
    """

    ENDPOINT: ClassVar[str] = "/logistics/SupplierItem"
    MODEL: ClassVar[type[SupplierItem]] = SupplierItem
    ID_FIELD: ClassVar[str] = "ID"
