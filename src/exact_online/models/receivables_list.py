"""Pydantic models for Receivables List."""

from typing import Any
from uuid import UUID

from pydantic import Field

from exact_online.models.base import ExactBaseModel, ODataDateTime


class ReceivablesListItem(ExactBaseModel):
    """A customer payment term entry."""

    hid: int = Field(alias="HID")
    account_code: str | None = Field(default=None, alias="AccountCode")
    account_id: UUID | None = Field(default=None, alias="AccountId")
    account_name: str | None = Field(default=None, alias="AccountName")
    amount: float | None = Field(default=None, alias="Amount")
    amount_in_transit: float | None = Field(default=None, alias="AmountInTransit")
    currency_code: str | None = Field(default=None, alias="CurrencyCode")
    description: str | None = Field(default=None, alias="Description")
    due_date: ODataDateTime = Field(default=None, alias="DueDate")
    entry_number: int | None = Field(default=None, alias="EntryNumber")
    id: UUID | None = Field(default=None, alias="Id")
    invoice_date: ODataDateTime = Field(default=None, alias="InvoiceDate")
    invoice_number: int | None = Field(default=None, alias="InvoiceNumber")
    journal_code: str | None = Field(default=None, alias="JournalCode")
    journal_description: str | None = Field(default=None, alias="JournalDescription")
    notes: list[Any] | None = Field(default=None, alias="Notes")
    your_ref: str | None = Field(default=None, alias="YourRef")

    def __repr__(self) -> str:
        """Return a readable representation."""
        return f"ReceivablesListItem(account_name={self.account_name!r}, amount={self.amount})"
