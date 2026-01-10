"""Pydantic models for Accounts (customers, suppliers, etc.)."""

from uuid import UUID

from pydantic import Field

from exact_online.models.base import ExactBaseModel, ODataDateTime


class Account(ExactBaseModel):
    """An Account in Exact Online (customer, supplier, or other relation).

    Accounts are the core relation entity in Exact Online. They can represent
    customers, suppliers, or other business relationships depending on the
    classification flags.
    """

    id: UUID = Field(alias="ID")
    code: str | None = Field(default=None, alias="Code")
    name: str | None = Field(default=None, alias="Name")
    search_code: str | None = Field(default=None, alias="SearchCode")
    is_supplier: bool | None = Field(default=None, alias="IsSupplier")
    is_sales: bool | None = Field(default=None, alias="IsSales")
    is_reseller: bool | None = Field(default=None, alias="IsReseller")
    is_competitor: bool | None = Field(default=None, alias="IsCompetitor")
    is_mailing: bool | None = Field(default=None, alias="IsMailing")
    is_accountant: bool | None = Field(default=None, alias="IsAccountant")
    status: str | None = Field(default=None, alias="Status")
    email: str | None = Field(default=None, alias="Email")
    phone: str | None = Field(default=None, alias="Phone")
    fax: str | None = Field(default=None, alias="Fax")
    website: str | None = Field(default=None, alias="Website")
    address_line1: str | None = Field(default=None, alias="AddressLine1")
    address_line2: str | None = Field(default=None, alias="AddressLine2")
    address_line3: str | None = Field(default=None, alias="AddressLine3")
    postcode: str | None = Field(default=None, alias="Postcode")
    city: str | None = Field(default=None, alias="City")
    state: str | None = Field(default=None, alias="State")
    country: str | None = Field(default=None, alias="Country")
    country_name: str | None = Field(default=None, alias="CountryName")
    vat_number: str | None = Field(default=None, alias="VATNumber")
    chamber_of_commerce: str | None = Field(default=None, alias="ChamberOfCommerce")
    currency: str | None = Field(default=None, alias="Currency")
    credit_line: float | None = Field(default=None, alias="CreditLine")
    payment_condition_sales: str | None = Field(
        default=None, alias="PaymentConditionSales"
    )
    payment_condition_sales_description: str | None = Field(
        default=None, alias="PaymentConditionSalesDescription"
    )
    payment_condition_purchase: str | None = Field(
        default=None, alias="PaymentConditionPurchase"
    )
    payment_condition_purchase_description: str | None = Field(
        default=None, alias="PaymentConditionPurchaseDescription"
    )
    bank_account: UUID | None = Field(default=None, alias="BankAccount")
    iban: str | None = Field(default=None, alias="IBAN")
    bic: str | None = Field(default=None, alias="BIC")
    account_manager: UUID | None = Field(default=None, alias="AccountManager")
    account_manager_full_name: str | None = Field(
        default=None, alias="AccountManagerFullName"
    )
    classification: UUID | None = Field(default=None, alias="Classification")
    classification_description: str | None = Field(
        default=None, alias="ClassificationDescription"
    )
    created: ODataDateTime = Field(default=None, alias="Created")
    modified: ODataDateTime = Field(default=None, alias="Modified")
    start_date: ODataDateTime = Field(default=None, alias="StartDate")
    end_date: ODataDateTime = Field(default=None, alias="EndDate")
    logo_url: str | None = Field(default=None, alias="LogoUrl")
    remarks: str | None = Field(default=None, alias="Remarks")
    timestamp: int | None = Field(default=None, alias="Timestamp")

    def __repr__(self) -> str:
        """Return a readable representation."""
        return f"Account(code={self.code!r}, name={self.name!r})"
