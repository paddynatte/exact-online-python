"""Pydantic models for Bill of Material Materials."""

from uuid import UUID

from pydantic import Field

from exact_online.models.base import ExactBaseModel, ODataDateTime


class BillOfMaterialMaterial(ExactBaseModel):
    """
    A material in a Bill of Material version linked to a make item.

    Type values:
        1 - Material
        2 - Byproduct
    """

    id: UUID = Field(alias="ID")
    average_cost: float | None = Field(default=None, alias="AverageCost")
    backflush: int | None = Field(default=None, alias="Backflush")
    calculator_type: int | None = Field(default=None, alias="CalculatorType")
    cost_batch: float | None = Field(default=None, alias="CostBatch")
    cost_center: str | None = Field(default=None, alias="CostCenter")
    cost_center_description: str | None = Field(default=None, alias="CostCenterDescription")
    cost_unit: str | None = Field(default=None, alias="CostUnit")
    cost_unit_description: str | None = Field(default=None, alias="CostUnitDescription")
    creator_full_name: str | None = Field(default=None, alias="CreatorFullName")
    description: str | None = Field(default=None, alias="Description")
    detail_drawing: str | None = Field(default=None, alias="DetailDrawing")
    division: int | None = Field(default=None, alias="Division")
    item_version: UUID | None = Field(default=None, alias="ItemVersion")
    line_number: int | None = Field(default=None, alias="LineNumber")
    net_weight: float | None = Field(default=None, alias="NetWeight")
    net_weight_unit: str | None = Field(default=None, alias="NetWeightUnit")
    notes: str | None = Field(default=None, alias="Notes")
    part_item: UUID | None = Field(default=None, alias="PartItem")
    part_item_average_cost: float | None = Field(default=None, alias="PartItemAverageCost")
    part_item_code: str | None = Field(default=None, alias="PartItemCode")
    part_item_cost_price_standard: float | None = Field(default=None, alias="PartItemCostPriceStandard")
    part_item_description: str | None = Field(default=None, alias="PartItemDescription")
    quantity: float | None = Field(default=None, alias="Quantity")
    quantity_batch: float | None = Field(default=None, alias="QuantityBatch")
    routing_step_id: UUID | None = Field(default=None, alias="RoutingStepID")
    syscreated: ODataDateTime = Field(default=None, alias="syscreated")
    syscreator: UUID | None = Field(default=None, alias="syscreator")
    sysmodified: ODataDateTime = Field(default=None, alias="sysmodified")
    sysmodifier: UUID | None = Field(default=None, alias="sysmodifier")
    type: int | None = Field(default=None, alias="Type")
    waste_percentage: float | None = Field(default=None, alias="WastePercentage")

    def __repr__(self) -> str:
        """Return a readable representation."""
        return f"BillOfMaterialMaterial(part_item_code={self.part_item_code!r}, quantity={self.quantity})"
