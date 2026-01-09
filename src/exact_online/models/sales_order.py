"""Pydantic models for Sales Orders."""

from typing import Any
from uuid import UUID

from pydantic import Field

from exact_online.models.base import ExactBaseModel, ODataDateTime


class SalesOrder(ExactBaseModel):
    """
    A Sales Order in Exact Online.

    Status values:
        12 - Open
        20 - Partial
        21 - Complete
        45 - Cancelled

    ApprovalStatus values:
        0 - Awaiting approval
        1 - Automatically approved
        2 - Approved
    """

    order_id: UUID = Field(alias="OrderID")
    amount_dc: float | None = Field(default=None, alias="AmountDC")
    amount_discount: float | None = Field(default=None, alias="AmountDiscount")
    amount_discount_excl_vat: float | None = Field(default=None, alias="AmountDiscountExclVat")
    amount_fc: float | None = Field(default=None, alias="AmountFC")
    amount_fc_excl_vat: float | None = Field(default=None, alias="AmountFCExclVat")
    approval_status: int | None = Field(default=None, alias="ApprovalStatus")
    approval_status_description: str | None = Field(default=None, alias="ApprovalStatusDescription")
    approved: ODataDateTime = Field(default=None, alias="Approved")
    approver: UUID | None = Field(default=None, alias="Approver")
    approver_full_name: str | None = Field(default=None, alias="ApproverFullName")
    created: ODataDateTime = Field(default=None, alias="Created")
    creator: UUID | None = Field(default=None, alias="Creator")
    creator_full_name: str | None = Field(default=None, alias="CreatorFullName")
    currency: str | None = Field(default=None, alias="Currency")
    custom_field: str | None = Field(default=None, alias="CustomField")
    deliver_to: UUID | None = Field(default=None, alias="DeliverTo")
    deliver_to_contact_person: UUID | None = Field(default=None, alias="DeliverToContactPerson")
    deliver_to_contact_person_full_name: str | None = Field(default=None, alias="DeliverToContactPersonFullName")
    deliver_to_name: str | None = Field(default=None, alias="DeliverToName")
    delivery_address: UUID | None = Field(default=None, alias="DeliveryAddress")
    delivery_date: ODataDateTime = Field(default=None, alias="DeliveryDate")
    delivery_status: int | None = Field(default=None, alias="DeliveryStatus")
    delivery_status_description: str | None = Field(default=None, alias="DeliveryStatusDescription")
    description: str | None = Field(default=None, alias="Description")
    discount: float | None = Field(default=None, alias="Discount")
    division: int | None = Field(default=None, alias="Division")
    document: UUID | None = Field(default=None, alias="Document")
    document_number: int | None = Field(default=None, alias="DocumentNumber")
    document_subject: str | None = Field(default=None, alias="DocumentSubject")
    incoterm_address: str | None = Field(default=None, alias="IncotermAddress")
    incoterm_code: str | None = Field(default=None, alias="IncotermCode")
    incoterm_version: int | None = Field(default=None, alias="IncotermVersion")
    invoice_status: int | None = Field(default=None, alias="InvoiceStatus")
    invoice_status_description: str | None = Field(default=None, alias="InvoiceStatusDescription")
    invoice_to: UUID | None = Field(default=None, alias="InvoiceTo")
    invoice_to_contact_person: UUID | None = Field(default=None, alias="InvoiceToContactPerson")
    invoice_to_contact_person_full_name: str | None = Field(default=None, alias="InvoiceToContactPersonFullName")
    invoice_to_name: str | None = Field(default=None, alias="InvoiceToName")
    modified: ODataDateTime = Field(default=None, alias="Modified")
    modifier: UUID | None = Field(default=None, alias="Modifier")
    modifier_full_name: str | None = Field(default=None, alias="ModifierFullName")
    order_date: ODataDateTime = Field(default=None, alias="OrderDate")
    ordered_by: UUID | None = Field(default=None, alias="OrderedBy")
    ordered_by_contact_person: UUID | None = Field(default=None, alias="OrderedByContactPerson")
    ordered_by_contact_person_full_name: str | None = Field(default=None, alias="OrderedByContactPersonFullName")
    ordered_by_name: str | None = Field(default=None, alias="OrderedByName")
    order_number: int | None = Field(default=None, alias="OrderNumber")
    payment_condition: str | None = Field(default=None, alias="PaymentCondition")
    payment_condition_description: str | None = Field(default=None, alias="PaymentConditionDescription")
    payment_reference: str | None = Field(default=None, alias="PaymentReference")
    remarks: str | None = Field(default=None, alias="Remarks")
    sales_channel: UUID | None = Field(default=None, alias="SalesChannel")
    sales_channel_code: str | None = Field(default=None, alias="SalesChannelCode")
    sales_channel_description: str | None = Field(default=None, alias="SalesChannelDescription")
    sales_order_lines: list[Any] | None = Field(default=None, alias="SalesOrderLines")
    sales_order_order_charge_lines: list[Any] | None = Field(default=None, alias="SalesOrderOrderChargeLines")
    salesperson: UUID | None = Field(default=None, alias="Salesperson")
    salesperson_full_name: str | None = Field(default=None, alias="SalespersonFullName")
    selection_code: UUID | None = Field(default=None, alias="SelectionCode")
    selection_code_code: str | None = Field(default=None, alias="SelectionCodeCode")
    selection_code_description: str | None = Field(default=None, alias="SelectionCodeDescription")
    shipping_method: UUID | None = Field(default=None, alias="ShippingMethod")
    shipping_method_description: str | None = Field(default=None, alias="ShippingMethodDescription")
    status: int | None = Field(default=None, alias="Status")
    status_description: str | None = Field(default=None, alias="StatusDescription")
    tax_schedule: UUID | None = Field(default=None, alias="TaxSchedule")
    tax_schedule_code: str | None = Field(default=None, alias="TaxScheduleCode")
    tax_schedule_description: str | None = Field(default=None, alias="TaxScheduleDescription")
    warehouse_code: str | None = Field(default=None, alias="WarehouseCode")
    warehouse_description: str | None = Field(default=None, alias="WarehouseDescription")
    warehouse_id: UUID | None = Field(default=None, alias="WarehouseID")
    your_ref: str | None = Field(default=None, alias="YourRef")
    timestamp: int | None = Field(default=None, alias="Timestamp")

    def __repr__(self) -> str:
        """Return a readable representation."""
        return f"SalesOrder(order_number={self.order_number}, description={self.description!r})"
