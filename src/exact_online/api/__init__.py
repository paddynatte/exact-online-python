"""API resources for Exact Online."""

from exact_online.api.base import BaseAPI
from exact_online.api.divisions import DivisionsAPI
from exact_online.api.goods_receipt_lines import GoodsReceiptLinesAPI
from exact_online.api.goods_receipts import GoodsReceiptsAPI
from exact_online.api.me import MeAPI
from exact_online.api.purchase_order_lines import PurchaseOrderLinesAPI
from exact_online.api.purchase_orders import PurchaseOrdersAPI
from exact_online.api.sales_orders import SalesOrdersAPI
from exact_online.api.shop_orders import ShopOrdersAPI
from exact_online.api.stock_count_lines import StockCountLinesAPI
from exact_online.api.stock_counts import StockCountsAPI
from exact_online.api.supplier_items import SupplierItemsAPI
from exact_online.api.units import UnitsAPI
from exact_online.api.warehouse_transfers import WarehouseTransfersAPI
from exact_online.api.warehouses import WarehousesAPI

__all__ = [
    "BaseAPI",
    "DivisionsAPI",
    "GoodsReceiptLinesAPI",
    "GoodsReceiptsAPI",
    "MeAPI",
    "PurchaseOrderLinesAPI",
    "PurchaseOrdersAPI",
    "SalesOrdersAPI",
    "ShopOrdersAPI",
    "StockCountLinesAPI",
    "StockCountsAPI",
    "SupplierItemsAPI",
    "UnitsAPI",
    "WarehousesAPI",
    "WarehouseTransfersAPI",
]
