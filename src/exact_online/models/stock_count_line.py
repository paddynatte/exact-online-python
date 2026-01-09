"""Pydantic models for Stock Count Lines."""

from typing import Any
from uuid import UUID

from pydantic import Field

from exact_online.models.base import ExactBaseModel, ODataDateTime


class StockCountLine(ExactBaseModel):
    """A line in a stock count."""

    id: UUID = Field(alias="ID")
    batch_numbers: list[Any] | None = Field(default=None, alias="BatchNumbers")
    cost_price: float | None = Field(default=None, alias="CostPrice")
    created: ODataDateTime = Field(default=None, alias="Created")
    creator: UUID | None = Field(default=None, alias="Creator")
    creator_full_name: str | None = Field(default=None, alias="CreatorFullName")
    division: int | None = Field(default=None, alias="Division")
    item: UUID | None = Field(default=None, alias="Item")
    item_code: str | None = Field(default=None, alias="ItemCode")
    item_cost_price: float | None = Field(default=None, alias="ItemCostPrice")
    item_description: str | None = Field(default=None, alias="ItemDescription")
    item_divisable: bool | None = Field(default=None, alias="ItemDivisable")
    line_number: int | None = Field(default=None, alias="LineNumber")
    modified: ODataDateTime = Field(default=None, alias="Modified")
    modifier: UUID | None = Field(default=None, alias="Modifier")
    modifier_full_name: str | None = Field(default=None, alias="ModifierFullName")
    quantity_difference: float | None = Field(default=None, alias="QuantityDifference")
    quantity_in_stock: float | None = Field(default=None, alias="QuantityInStock")
    quantity_new: float | None = Field(default=None, alias="QuantityNew")
    reason_code: str | None = Field(default=None, alias="ReasonCode")
    reason_code_description: str | None = Field(default=None, alias="ReasonCodeDescription")
    reason_code_id: UUID | None = Field(default=None, alias="ReasonCodeID")
    serial_numbers: list[Any] | None = Field(default=None, alias="SerialNumbers")
    stock_count_id: UUID | None = Field(default=None, alias="StockCountID")
    stock_keeping_unit: str | None = Field(default=None, alias="StockKeepingUnit")
    storage_location: UUID | None = Field(default=None, alias="StorageLocation")
    storage_location_code: str | None = Field(default=None, alias="StorageLocationCode")
    storage_location_description: str | None = Field(default=None, alias="StorageLocationDescription")
    storage_location_sequence_number: int | None = Field(default=None, alias="StorageLocationSequenceNumber")

    def __repr__(self) -> str:
        """Return a readable representation."""
        return f"StockCountLine(item_code={self.item_code!r}, quantity_new={self.quantity_new})"
