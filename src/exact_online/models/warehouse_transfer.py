"""Pydantic models for Warehouse Transfers."""

from typing import Any
from uuid import UUID

from pydantic import Field

from exact_online.models.base import ExactBaseModel, ODataDateTime


class WarehouseTransfer(ExactBaseModel):
    """
    A warehouse or location transfer.

    When WarehouseFrom equals WarehouseTo, this is a location transfer.

    Status values:
        10 - Open
        50 - Complete

    Source values:
        1 - Manual entry
        2 - Import
        3 - Transfer advice
        4 - Web service
    """

    transfer_id: UUID = Field(alias="TransferID")
    created: ODataDateTime = Field(default=None, alias="Created")
    creator: UUID | None = Field(default=None, alias="Creator")
    creator_full_name: str | None = Field(default=None, alias="CreatorFullName")
    description: str | None = Field(default=None, alias="Description")
    division: int | None = Field(default=None, alias="Division")
    entry_date: ODataDateTime = Field(default=None, alias="EntryDate")
    modified: ODataDateTime = Field(default=None, alias="Modified")
    modifier: UUID | None = Field(default=None, alias="Modifier")
    modifier_full_name: str | None = Field(default=None, alias="ModifierFullName")
    planned_delivery_date: ODataDateTime = Field(default=None, alias="PlannedDeliveryDate")
    planned_receipt_date: ODataDateTime = Field(default=None, alias="PlannedReceiptDate")
    remarks: str | None = Field(default=None, alias="Remarks")
    source: int | None = Field(default=None, alias="Source")
    status: int | None = Field(default=None, alias="Status")
    transfer_date: ODataDateTime = Field(default=None, alias="TransferDate")
    transfer_number: int | None = Field(default=None, alias="TransferNumber")
    warehouse_from: UUID | None = Field(default=None, alias="WarehouseFrom")
    warehouse_from_code: str | None = Field(default=None, alias="WarehouseFromCode")
    warehouse_from_description: str | None = Field(default=None, alias="WarehouseFromDescription")
    warehouse_to: UUID | None = Field(default=None, alias="WarehouseTo")
    warehouse_to_code: str | None = Field(default=None, alias="WarehouseToCode")
    warehouse_to_description: str | None = Field(default=None, alias="WarehouseToDescription")
    warehouse_transfer_lines: list[Any] | None = Field(default=None, alias="WarehouseTransferLines")

    def __repr__(self) -> str:
        """Return a readable representation."""
        return f"WarehouseTransfer(transfer_number={self.transfer_number}, description={self.description!r})"
