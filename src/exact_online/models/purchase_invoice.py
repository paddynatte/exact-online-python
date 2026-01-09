"""Pydantic models for Purchase Invoices."""

from typing import Any
from uuid import UUID

from pydantic import Field

from exact_online.models.base import ExactBaseModel, ODataDateTime


class PurchaseInvoice(ExactBaseModel):
    """
    A purchase invoice from a supplier.

    Status values:
        10 - Draft
        20 - Open
        50 - Processed

    Type values:
        8030 - Direct purchase invoice
        8031 - Direct purchase invoice (Credit)
        8033 - Purchase invoice
        8034 - Purchase invoice (Credit)

    Source values:
        1 - Manual entry
        3 - Purchase invoice
        4 - Purchase order
        5 - Web service
    """

    id: UUID = Field(alias="ID")
    amount: float | None = Field(default=None, alias="Amount")
    contact_person: UUID | None = Field(default=None, alias="ContactPerson")
    currency: str | None = Field(default=None, alias="Currency")
    description: str | None = Field(default=None, alias="Description")
    document: UUID | None = Field(default=None, alias="Document")
    due_date: ODataDateTime = Field(default=None, alias="DueDate")
    entry_number: int | None = Field(default=None, alias="EntryNumber")
    exchange_rate: float | None = Field(default=None, alias="ExchangeRate")
    financial_period: int | None = Field(default=None, alias="FinancialPeriod")
    financial_year: int | None = Field(default=None, alias="FinancialYear")
    invoice_date: ODataDateTime = Field(default=None, alias="InvoiceDate")
    journal: str | None = Field(default=None, alias="Journal")
    modified: ODataDateTime = Field(default=None, alias="Modified")
    payment_condition: str | None = Field(default=None, alias="PaymentCondition")
    payment_reference: str | None = Field(default=None, alias="PaymentReference")
    purchase_invoice_lines: list[Any] | None = Field(default=None, alias="PurchaseInvoiceLines")
    remarks: str | None = Field(default=None, alias="Remarks")
    source: int | None = Field(default=None, alias="Source")
    status: int | None = Field(default=None, alias="Status")
    supplier: UUID | None = Field(default=None, alias="Supplier")
    type: int | None = Field(default=None, alias="Type")
    vat_amount: float | None = Field(default=None, alias="VATAmount")
    warehouse: UUID | None = Field(default=None, alias="Warehouse")
    your_ref: str | None = Field(default=None, alias="YourRef")

    def __repr__(self) -> str:
        """Return a readable representation."""
        return f"PurchaseInvoice(entry_number={self.entry_number}, amount={self.amount})"
