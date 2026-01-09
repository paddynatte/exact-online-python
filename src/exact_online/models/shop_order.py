"""Pydantic models for Shop Orders."""

from typing import Any
from uuid import UUID

from pydantic import Field

from exact_online.models.base import ExactBaseModel, ODataDateTime


class ShopOrder(ExactBaseModel):
    """
    A Shop Order in Exact Online.

    Status values:
        10 - Open
        20 - In process
        30 - Finished
        40 - Completed

    Type values:
        9040 - Regular (always)
    """

    id: UUID = Field(alias="ID")
    cad_drawing_url: str | None = Field(default=None, alias="CADDrawingURL")
    costcenter: str | None = Field(default=None, alias="Costcenter")
    costcenter_description: str | None = Field(default=None, alias="CostcenterDescription")
    costunit: str | None = Field(default=None, alias="Costunit")
    costunit_description: str | None = Field(default=None, alias="CostunitDescription")
    created: ODataDateTime = Field(default=None, alias="Created")
    creator: UUID | None = Field(default=None, alias="Creator")
    creator_full_name: str | None = Field(default=None, alias="CreatorFullName")
    description: str | None = Field(default=None, alias="Description")
    division: int | None = Field(default=None, alias="Division")
    entry_date: ODataDateTime = Field(default=None, alias="EntryDate")
    is_batch: int | None = Field(default=None, alias="IsBatch")
    is_fraction_allowed_item: int | None = Field(default=None, alias="IsFractionAllowedItem")
    is_in_planning: int | None = Field(default=None, alias="IsInPlanning")
    is_on_hold: int | None = Field(default=None, alias="IsOnHold")
    is_released: int | None = Field(default=None, alias="IsReleased")
    is_serial: int | None = Field(default=None, alias="IsSerial")
    item: UUID | None = Field(default=None, alias="Item")
    item_barcode: str | None = Field(default=None, alias="ItemBarcode")
    item_code: str | None = Field(default=None, alias="ItemCode")
    item_description: str | None = Field(default=None, alias="ItemDescription")
    item_picture_url: str | None = Field(default=None, alias="ItemPictureUrl")
    item_version: UUID | None = Field(default=None, alias="ItemVersion")
    item_version_description: str | None = Field(default=None, alias="ItemVersionDescription")
    modified: ODataDateTime = Field(default=None, alias="Modified")
    modifier: UUID | None = Field(default=None, alias="Modifier")
    modifier_full_name: str | None = Field(default=None, alias="ModifierFullName")
    notes: str | None = Field(default=None, alias="Notes")
    planned_date: ODataDateTime = Field(default=None, alias="PlannedDate")
    planned_quantity: float | None = Field(default=None, alias="PlannedQuantity")
    planned_start_date: ODataDateTime = Field(default=None, alias="PlannedStartDate")
    produced_quantity: float | None = Field(default=None, alias="ProducedQuantity")
    production_lead_days: int | None = Field(default=None, alias="ProductionLeadDays")
    project: UUID | None = Field(default=None, alias="Project")
    project_description: str | None = Field(default=None, alias="ProjectDescription")
    ready_to_ship_quantity: float | None = Field(default=None, alias="ReadyToShipQuantity")
    sales_order_line_count: int | None = Field(default=None, alias="SalesOrderLineCount")
    sales_order_lines: list[Any] | None = Field(default=None, alias="SalesOrderLines")
    selection_code: UUID | None = Field(default=None, alias="SelectionCode")
    selection_code_code: str | None = Field(default=None, alias="SelectionCodeCode")
    selection_code_description: str | None = Field(default=None, alias="SelectionCodeDescription")
    shop_order_by_product_plan_backflush_count: int | None = Field(
        default=None, alias="ShopOrderByProductPlanBackflushCount"
    )
    shop_order_by_product_plan_count: int | None = Field(default=None, alias="ShopOrderByProductPlanCount")
    shop_order_main: UUID | None = Field(default=None, alias="ShopOrderMain")
    shop_order_main_number: int | None = Field(default=None, alias="ShopOrderMainNumber")
    shop_order_material_plan_backflush_count: int | None = Field(
        default=None, alias="ShopOrderMaterialPlanBackflushCount"
    )
    shop_order_material_plan_count: int | None = Field(default=None, alias="ShopOrderMaterialPlanCount")
    shop_order_material_plans: list[Any] | None = Field(default=None, alias="ShopOrderMaterialPlans")
    shop_order_material_plans_non_issued_byproducts_count: int | None = Field(
        default=None, alias="ShopOrderMaterialPlansNonIssuedByproductsCount"
    )
    shop_order_material_plans_non_issued_materials_count: int | None = Field(
        default=None, alias="ShopOrderMaterialPlansNonIssuedMaterialsCount"
    )
    shop_order_number: int | None = Field(default=None, alias="ShopOrderNumber")
    shop_order_number_string: str | None = Field(default=None, alias="ShopOrderNumberString")
    shop_order_parent: UUID | None = Field(default=None, alias="ShopOrderParent")
    shop_order_parent_number: int | None = Field(default=None, alias="ShopOrderParentNumber")
    shop_order_routing_step_plan_count: int | None = Field(default=None, alias="ShopOrderRoutingStepPlanCount")
    shop_order_routing_step_plans: list[Any] | None = Field(default=None, alias="ShopOrderRoutingStepPlans")
    status: int | None = Field(default=None, alias="Status")
    sub_shop_order_count: int | None = Field(default=None, alias="SubShopOrderCount")
    type: int | None = Field(default=None, alias="Type")
    unit: str | None = Field(default=None, alias="Unit")
    unit_description: str | None = Field(default=None, alias="UnitDescription")
    warehouse: UUID | None = Field(default=None, alias="Warehouse")
    warehouse_code: str | None = Field(default=None, alias="WarehouseCode")
    warehouse_description: str | None = Field(default=None, alias="WarehouseDescription")
    your_ref: str | None = Field(default=None, alias="YourRef")
    timestamp: int | None = Field(default=None, alias="Timestamp")

    def __repr__(self) -> str:
        """Return a readable representation."""
        return f"ShopOrder(shop_order_number={self.shop_order_number}, item_code={self.item_code!r})"
