"""Pydantic models for Goods Receipts and Goods Receipt Lines."""

from uuid import UUID

from pydantic import Field

from exact_online.models.base import ExactBaseModel, ODataDateTime


class GoodsReceiptLine(ExactBaseModel):
    """A line item in a Goods Receipt."""

    id: UUID = Field(alias="ID")
    goods_receipt_id: UUID | None = Field(default=None, alias="GoodsReceiptID")
    item: UUID | None = Field(default=None, alias="Item")
    item_code: str | None = Field(default=None, alias="ItemCode")
    item_description: str | None = Field(default=None, alias="ItemDescription")
    line_number: int | None = Field(default=None, alias="LineNumber")
    location: UUID | None = Field(default=None, alias="Location")
    location_code: str | None = Field(default=None, alias="LocationCode")
    location_description: str | None = Field(default=None, alias="LocationDescription")
    notes: str | None = Field(default=None, alias="Notes")
    project: UUID | None = Field(default=None, alias="Project")
    project_code: str | None = Field(default=None, alias="ProjectCode")
    project_description: str | None = Field(default=None, alias="ProjectDescription")
    purchase_order_id: UUID | None = Field(default=None, alias="PurchaseOrderID")
    purchase_order_line_id: UUID | None = Field(default=None, alias="PurchaseOrderLineID")
    purchase_order_number: int | None = Field(default=None, alias="PurchaseOrderNumber")
    quantity_ordered: float | None = Field(default=None, alias="QuantityOrdered")
    quantity_received: float | None = Field(default=None, alias="QuantityReceived")
    unit: str | None = Field(default=None, alias="Unit")
    unit_code: str | None = Field(default=None, alias="UnitCode")
    unit_description: str | None = Field(default=None, alias="UnitDescription")


class GoodsReceipt(ExactBaseModel):
    """A Goods Receipt in Exact Online."""

    id: UUID = Field(alias="ID")
    created: ODataDateTime = Field(default=None, alias="Created")
    creator: UUID | None = Field(default=None, alias="Creator")
    creator_full_name: str | None = Field(default=None, alias="CreatorFullName")
    description: str | None = Field(default=None, alias="Description")
    division: int | None = Field(default=None, alias="Division")
    document: UUID | None = Field(default=None, alias="Document")
    document_subject: str | None = Field(default=None, alias="DocumentSubject")
    entry_number: int | None = Field(default=None, alias="EntryNumber")
    goods_receipt_line_count: int | None = Field(
        default=None, alias="GoodsReceiptLineCount"
    )
    goods_receipt_lines: list[GoodsReceiptLine] | None = Field(
        default=None, alias="GoodsReceiptLines"
    )
    modified: ODataDateTime = Field(default=None, alias="Modified")
    modifier: UUID | None = Field(default=None, alias="Modifier")
    modifier_full_name: str | None = Field(default=None, alias="ModifierFullName")
    receipt_date: ODataDateTime = Field(default=None, alias="ReceiptDate")
    receipt_number: int | None = Field(default=None, alias="ReceiptNumber")
    remarks: str | None = Field(default=None, alias="Remarks")
    supplier: UUID | None = Field(default=None, alias="Supplier")
    supplier_code: str | None = Field(default=None, alias="SupplierCode")
    supplier_contact: UUID | None = Field(default=None, alias="SupplierContact")
    supplier_contact_full_name: str | None = Field(
        default=None, alias="SupplierContactFullName"
    )
    supplier_name: str | None = Field(default=None, alias="SupplierName")
    warehouse: UUID | None = Field(default=None, alias="Warehouse")
    warehouse_code: str | None = Field(default=None, alias="WarehouseCode")
    warehouse_description: str | None = Field(
        default=None, alias="WarehouseDescription"
    )
    your_ref: str | None = Field(default=None, alias="YourRef")
