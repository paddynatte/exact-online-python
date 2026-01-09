"""Pydantic models for Item Warehouses."""

from uuid import UUID

from pydantic import Field

from exact_online.models.base import ExactBaseModel, ODataDateTime


class ItemWarehouse(ExactBaseModel):
    """
    A link between an item and a warehouse with stock information.

    OrderPolicy values:
        1 - Lot for lot
        2 - Fixed order quantity
        3 - Min/Max
        4 - Order

    ReplenishmentType values:
        1 - Purchase
        2 - Assemble
        3 - Make
        4 - Transfer
        5 - No advice
    """

    id: UUID = Field(alias="ID")
    counting_cycle: int | None = Field(default=None, alias="CountingCycle")
    created: ODataDateTime = Field(default=None, alias="Created")
    creator: UUID | None = Field(default=None, alias="Creator")
    creator_full_name: str | None = Field(default=None, alias="CreatorFullName")
    current_stock: float | None = Field(default=None, alias="CurrentStock")
    default_storage_location: UUID | None = Field(default=None, alias="DefaultStorageLocation")
    default_storage_location_code: str | None = Field(default=None, alias="DefaultStorageLocationCode")
    default_storage_location_description: str | None = Field(default=None, alias="DefaultStorageLocationDescription")
    division: int | None = Field(default=None, alias="Division")
    item: UUID | None = Field(default=None, alias="Item")
    item_code: str | None = Field(default=None, alias="ItemCode")
    item_description: str | None = Field(default=None, alias="ItemDescription")
    item_end_date: ODataDateTime = Field(default=None, alias="ItemEndDate")
    item_is_fraction_allowed_item: bool | None = Field(default=None, alias="ItemIsFractionAllowedItem")
    item_is_stock_item: bool | None = Field(default=None, alias="ItemIsStockItem")
    item_start_date: ODataDateTime = Field(default=None, alias="ItemStartDate")
    item_unit: str | None = Field(default=None, alias="ItemUnit")
    item_unit_description: str | None = Field(default=None, alias="ItemUnitDescription")
    maximum_stock: float | None = Field(default=None, alias="MaximumStock")
    modified: ODataDateTime = Field(default=None, alias="Modified")
    modifier: UUID | None = Field(default=None, alias="Modifier")
    modifier_full_name: str | None = Field(default=None, alias="ModifierFullName")
    order_policy: int | None = Field(default=None, alias="OrderPolicy")
    period: int | None = Field(default=None, alias="Period")
    planned_stock_in: float | None = Field(default=None, alias="PlannedStockIn")
    planned_stock_out: float | None = Field(default=None, alias="PlannedStockOut")
    planning_details_url: str | None = Field(default=None, alias="PlanningDetailsUrl")
    projected_stock: float | None = Field(default=None, alias="ProjectedStock")
    reorder_point: float | None = Field(default=None, alias="ReorderPoint")
    reorder_quantity: float | None = Field(default=None, alias="ReorderQuantity")
    replenishment_type: int | None = Field(default=None, alias="ReplenishmentType")
    reserved_stock: float | None = Field(default=None, alias="ReservedStock")
    safety_stock: float | None = Field(default=None, alias="SafetyStock")
    storage_location_sequence_number: int | None = Field(default=None, alias="StorageLocationSequenceNumber")
    storage_location_url: str | None = Field(default=None, alias="StorageLocationUrl")
    warehouse: UUID | None = Field(default=None, alias="Warehouse")
    warehouse_code: str | None = Field(default=None, alias="WarehouseCode")
    warehouse_description: str | None = Field(default=None, alias="WarehouseDescription")

    def __repr__(self) -> str:
        """Return a readable representation."""
        return f"ItemWarehouse(item_code={self.item_code!r}, warehouse_code={self.warehouse_code!r})"
