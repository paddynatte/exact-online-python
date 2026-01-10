"""Pydantic models for Purchase Orders and Purchase Order Lines."""

from uuid import UUID

from pydantic import Field

from exact_online.models.base import ExactBaseModel, ODataDateTime


class PurchaseOrderLine(ExactBaseModel):
    """A line item in a Purchase Order."""

    id: UUID = Field(alias="ID")
    purchase_order_id: UUID = Field(alias="PurchaseOrderID")
    line_number: int | None = Field(default=None, alias="LineNumber")
    item: UUID | None = Field(default=None, alias="Item")
    item_code: str | None = Field(default=None, alias="ItemCode")
    item_description: str | None = Field(default=None, alias="ItemDescription")
    quantity: float | None = Field(default=None, alias="Quantity")
    quantity_in_purchase_units: float | None = Field(
        default=None, alias="QuantityInPurchaseUnits"
    )
    unit: str | None = Field(default=None, alias="Unit")
    unit_description: str | None = Field(default=None, alias="UnitDescription")
    unit_price: float | None = Field(default=None, alias="UnitPrice")
    net_price: float | None = Field(default=None, alias="NetPrice")
    amount_dc: float | None = Field(default=None, alias="AmountDC")
    amount_fc: float | None = Field(default=None, alias="AmountFC")
    vat_amount: float | None = Field(default=None, alias="VATAmount")
    vat_code: str | None = Field(default=None, alias="VATCode")
    vat_percentage: float | None = Field(default=None, alias="VATPercentage")
    receipt_date: ODataDateTime = Field(default=None, alias="ReceiptDate")
    quantity_received: float | None = Field(default=None, alias="QuantityReceived")
    in_stock: float | None = Field(default=None, alias="InStock")
    project: UUID | None = Field(default=None, alias="Project")
    project_code: str | None = Field(default=None, alias="ProjectCode")
    project_description: str | None = Field(default=None, alias="ProjectDescription")
    timestamp: int | None = Field(default=None, alias="Timestamp")


class PurchaseOrder(ExactBaseModel):
    """A Purchase Order in Exact Online."""

    purchase_order_id: UUID = Field(alias="PurchaseOrderID")
    order_number: int | None = Field(default=None, alias="OrderNumber")
    description: str | None = Field(default=None, alias="Description")
    supplier: UUID | None = Field(default=None, alias="Supplier")
    supplier_code: str | None = Field(default=None, alias="SupplierCode")
    supplier_name: str | None = Field(default=None, alias="SupplierName")
    supplier_contact: UUID | None = Field(default=None, alias="SupplierContact")
    supplier_contact_person_full_name: str | None = Field(
        default=None, alias="SupplierContactPersonFullName"
    )
    order_date: ODataDateTime = Field(default=None, alias="OrderDate")
    receipt_date: ODataDateTime = Field(default=None, alias="ReceiptDate")
    created: ODataDateTime = Field(default=None, alias="Created")
    approved: ODataDateTime = Field(default=None, alias="Approved")
    receipt_status: int | None = Field(default=None, alias="ReceiptStatus")
    approval_status: int | None = Field(default=None, alias="ApprovalStatus")
    approval_status_description: str | None = Field(
        default=None, alias="ApprovalStatusDescription"
    )
    amount_dc: float | None = Field(default=None, alias="AmountDC")
    amount_fc: float | None = Field(default=None, alias="AmountFC")
    amount_fc_excl_vat: float | None = Field(default=None, alias="AmountFCExclVat")
    vat_amount: float | None = Field(default=None, alias="VATAmount")
    amount_discount: float | None = Field(default=None, alias="AmountDiscount")
    amount_discount_excl_vat: float | None = Field(
        default=None, alias="AmountDiscountExclVat"
    )
    currency: str | None = Field(default=None, alias="Currency")
    warehouse: UUID | None = Field(default=None, alias="Warehouse")
    warehouse_code: str | None = Field(default=None, alias="WarehouseCode")
    warehouse_description: str | None = Field(
        default=None, alias="WarehouseDescription"
    )
    delivery_account: UUID | None = Field(default=None, alias="DeliveryAccount")
    delivery_account_code: str | None = Field(
        default=None, alias="DeliveryAccountCode"
    )
    delivery_account_name: str | None = Field(
        default=None, alias="DeliveryAccountName"
    )
    delivery_address: UUID | None = Field(default=None, alias="DeliveryAddress")
    delivery_contact: UUID | None = Field(default=None, alias="DeliveryContact")
    delivery_contact_person_full_name: str | None = Field(
        default=None, alias="DeliveryContactPersonFullName"
    )
    shipping_method: UUID | None = Field(default=None, alias="ShippingMethod")
    shipping_method_code: str | None = Field(default=None, alias="ShippingMethodCode")
    shipping_method_description: str | None = Field(
        default=None, alias="ShippingMethodDescription"
    )
    your_ref: str | None = Field(default=None, alias="YourRef")
    remarks: str | None = Field(default=None, alias="Remarks")
    creator: UUID | None = Field(default=None, alias="Creator")
    creator_full_name: str | None = Field(default=None, alias="CreatorFullName")
    approver: UUID | None = Field(default=None, alias="Approver")
    approver_full_name: str | None = Field(default=None, alias="ApproverFullName")
    purchase_agent: UUID | None = Field(default=None, alias="PurchaseAgent")
    purchase_agent_full_name: str | None = Field(
        default=None, alias="PurchaseAgentFullName"
    )
    sales_order: UUID | None = Field(default=None, alias="SalesOrder")
    sales_order_number: int | None = Field(default=None, alias="SalesOrderNumber")
    purchase_order_line_count: int | None = Field(
        default=None, alias="PurchaseOrderLineCount"
    )
    purchase_order_lines: list[PurchaseOrderLine] | None = Field(
        default=None, alias="PurchaseOrderLines"
    )
    source: int | None = Field(default=None, alias="Source")
    timestamp: int | None = Field(default=None, alias="Timestamp")
