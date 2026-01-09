"""Pydantic models for Reporting Balance."""

from uuid import UUID

from pydantic import Field

from exact_online.models.base import ExactBaseModel


class ReportingBalance(ExactBaseModel):
    """
    Summarized financial transaction data for reporting balances and period totals.

    Status values:
        20 - Open
        50 - Processed

    BalanceType values:
        B - Balance Sheet
        W - Profit & Loss
    """

    id: int = Field(alias="ID")
    amount: float | None = Field(default=None, alias="Amount")
    amount_credit: float | None = Field(default=None, alias="AmountCredit")
    amount_debit: float | None = Field(default=None, alias="AmountDebit")
    balance_type: str | None = Field(default=None, alias="BalanceType")
    cost_center_code: str | None = Field(default=None, alias="CostCenterCode")
    cost_center_description: str | None = Field(default=None, alias="CostCenterDescription")
    cost_unit_code: str | None = Field(default=None, alias="CostUnitCode")
    cost_unit_description: str | None = Field(default=None, alias="CostUnitDescription")
    count: int | None = Field(default=None, alias="Count")
    division: int | None = Field(default=None, alias="Division")
    gl_account: UUID | None = Field(default=None, alias="GLAccount")
    gl_account_code: str | None = Field(default=None, alias="GLAccountCode")
    gl_account_description: str | None = Field(default=None, alias="GLAccountDescription")
    reporting_period: int | None = Field(default=None, alias="ReportingPeriod")
    reporting_year: int | None = Field(default=None, alias="ReportingYear")
    status: int | None = Field(default=None, alias="Status")
    type: int | None = Field(default=None, alias="Type")

    def __repr__(self) -> str:
        """Return a readable representation."""
        return f"ReportingBalance(gl_account_code={self.gl_account_code!r}, amount={self.amount})"
