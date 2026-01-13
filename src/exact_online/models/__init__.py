"""Pydantic models for Exact Online API entities.

Note: With return_dicts=True, you typically don't need to import these models
directly - the SDK returns snake_case dicts automatically.
"""

from exact_online.models.base import (
    ExactBaseModel,
    ListResult,
    ModifiedSyncResult,
    SyncResult,
)
from exact_online.models.me import Me
from exact_online.models.purchase_order import PurchaseOrder, PurchaseOrderLine
from exact_online.models.sales_order import SalesOrder
from exact_online.models.shop_order import ShopOrder
from exact_online.models.warehouse_transfer import WarehouseTransfer

__all__ = [
    "ExactBaseModel",
    "ListResult",
    "Me",
    "ModifiedSyncResult",
    "PurchaseOrder",
    "PurchaseOrderLine",
    "SalesOrder",
    "ShopOrder",
    "SyncResult",
    "WarehouseTransfer",
]
