"""Pydantic models for Stock Counts and Stock Count Lines."""

from uuid import UUID

from pydantic import Field

from exact_online.models.base import ExactBaseModel, ODataDateTime


class StockCountLine(ExactBaseModel):
    """A line item in a Stock Count."""

    id: UUID = Field(alias="ID")
    stock_count_id: UUID | None = Field(default=None, alias="StockCountID")
    batch_number: str | None = Field(default=None, alias="BatchNumber")
    cost_price: float | None = Field(default=None, alias="CostPrice")
    created: ODataDateTime = Field(default=None, alias="Created")
    creator: UUID | None = Field(default=None, alias="Creator")
    creator_full_name: str | None = Field(default=None, alias="CreatorFullName")
    division: int | None = Field(default=None, alias="Division")
    item: UUID | None = Field(default=None, alias="Item")
    item_code: str | None = Field(default=None, alias="ItemCode")
    item_cost_price_standard: float | None = Field(
        default=None, alias="ItemCostPriceStandard"
    )
    item_description: str | None = Field(default=None, alias="ItemDescription")
    item_divisable: bool | None = Field(default=None, alias="ItemDivisable")
    line_number: int | None = Field(default=None, alias="LineNumber")
    modified: ODataDateTime = Field(default=None, alias="Modified")
    modifier: UUID | None = Field(default=None, alias="Modifier")
    modifier_full_name: str | None = Field(default=None, alias="ModifierFullName")
    quantity_difference: float | None = Field(default=None, alias="QuantityDifference")
    quantity_in_stock: float | None = Field(default=None, alias="QuantityInStock")
    quantity_new: float | None = Field(default=None, alias="QuantityNew")
    serial_number: str | None = Field(default=None, alias="SerialNumber")
    source: int | None = Field(default=None, alias="Source")
    stock_keeping_unit: str | None = Field(default=None, alias="StockKeepingUnit")
    storage_location: UUID | None = Field(default=None, alias="StorageLocation")
    storage_location_code: str | None = Field(
        default=None, alias="StorageLocationCode"
    )
    storage_location_description: str | None = Field(
        default=None, alias="StorageLocationDescription"
    )


class StockCount(ExactBaseModel):
    """A Stock Count in Exact Online.

    Status values:
        12 - Open (draft)
        21 - Processed
    """

    stock_count_id: UUID = Field(alias="StockCountID")
    counted_by: UUID | None = Field(default=None, alias="CountedBy")
    created: ODataDateTime = Field(default=None, alias="Created")
    creator: UUID | None = Field(default=None, alias="Creator")
    creator_full_name: str | None = Field(default=None, alias="CreatorFullName")
    description: str | None = Field(default=None, alias="Description")
    division: int | None = Field(default=None, alias="Division")
    entry_number: int | None = Field(default=None, alias="EntryNumber")
    modified: ODataDateTime = Field(default=None, alias="Modified")
    modifier: UUID | None = Field(default=None, alias="Modifier")
    modifier_full_name: str | None = Field(default=None, alias="ModifierFullName")
    offset_gl_inventory: UUID | None = Field(default=None, alias="OffsetGLInventory")
    offset_gl_inventory_code: str | None = Field(
        default=None, alias="OffsetGLInventoryCode"
    )
    offset_gl_inventory_description: str | None = Field(
        default=None, alias="OffsetGLInventoryDescription"
    )
    source: int | None = Field(default=None, alias="Source")
    status: int | None = Field(default=None, alias="Status")
    stock_count_date: ODataDateTime = Field(default=None, alias="StockCountDate")
    stock_count_lines: list[StockCountLine] | None = Field(
        default=None, alias="StockCountLines"
    )
    stock_count_number: int | None = Field(default=None, alias="StockCountNumber")
    warehouse: UUID | None = Field(default=None, alias="Warehouse")
    warehouse_code: str | None = Field(default=None, alias="WarehouseCode")
    warehouse_description: str | None = Field(
        default=None, alias="WarehouseDescription"
    )
