"""Pydantic model for Account (CRM) endpoint."""

from uuid import UUID

from pydantic import Field

from exact_online.models.base import ExactBaseModel, ODataDateTime


class Account(ExactBaseModel):
    """An account (customer/supplier) in Exact Online CRM.

    Accounts represent business relationships - customers, suppliers, or both.
    Supports full CRUD operations (GET, POST, PUT, DELETE).
    """

    id: UUID = Field(alias="ID")
    code: str | None = Field(default=None, alias="Code")
    name: str | None = Field(default=None, alias="Name")
    search_code: str | None = Field(default=None, alias="SearchCode")
    status: str | None = Field(default=None, alias="Status")
    email: str | None = Field(default=None, alias="Email")
    phone: str | None = Field(default=None, alias="Phone")
    phone_extension: str | None = Field(default=None, alias="PhoneExtension")
    fax: str | None = Field(default=None, alias="Fax")
    website: str | None = Field(default=None, alias="Website")
    address_line_1: str | None = Field(default=None, alias="AddressLine1")
    address_line_2: str | None = Field(default=None, alias="AddressLine2")
    address_line_3: str | None = Field(default=None, alias="AddressLine3")
    city: str | None = Field(default=None, alias="City")
    postcode: str | None = Field(default=None, alias="Postcode")
    state: str | None = Field(default=None, alias="State")
    state_name: str | None = Field(default=None, alias="StateName")
    country: str | None = Field(default=None, alias="Country")
    country_name: str | None = Field(default=None, alias="CountryName")
    is_supplier: bool | None = Field(default=None, alias="IsSupplier")
    is_sales: bool | None = Field(default=None, alias="IsSales")
    is_reseller: bool | None = Field(default=None, alias="IsReseller")
    is_competitor: int | None = Field(default=None, alias="IsCompetitor")
    is_accountant: int | None = Field(default=None, alias="IsAccountant")
    blocked: bool | None = Field(default=None, alias="Blocked")
    vat_number: str | None = Field(default=None, alias="VATNumber")
    chamber_of_commerce: str | None = Field(default=None, alias="ChamberOfCommerce")
    gln_number: str | None = Field(default=None, alias="GlnNumber")
    payment_condition_purchase: str | None = Field(
        default=None, alias="PaymentConditionPurchase"
    )
    payment_condition_purchase_description: str | None = Field(
        default=None, alias="PaymentConditionPurchaseDescription"
    )
    payment_condition_sales: str | None = Field(
        default=None, alias="PaymentConditionSales"
    )
    payment_condition_sales_description: str | None = Field(
        default=None, alias="PaymentConditionSalesDescription"
    )
    purchase_currency: str | None = Field(default=None, alias="PurchaseCurrency")
    sales_currency: str | None = Field(default=None, alias="SalesCurrency")
    purchase_vat_code: str | None = Field(default=None, alias="PurchaseVATCode")
    sales_vat_code: str | None = Field(default=None, alias="SalesVATCode")
    discount_purchase: float | None = Field(default=None, alias="DiscountPurchase")
    discount_sales: float | None = Field(default=None, alias="DiscountSales")
    credit_line_purchase: float | None = Field(default=None, alias="CreditLinePurchase")
    credit_line_sales: float | None = Field(default=None, alias="CreditLineSales")
    purchase_lead_days: int | None = Field(default=None, alias="PurchaseLeadDays")
    code_at_supplier: str | None = Field(default=None, alias="CodeAtSupplier")
    can_drop_ship: bool | None = Field(default=None, alias="CanDropShip")
    shipping_lead_days: int | None = Field(default=None, alias="ShippingLeadDays")
    shipping_method: UUID | None = Field(default=None, alias="ShippingMethod")
    account_manager: UUID | None = Field(default=None, alias="AccountManager")
    account_manager_full_name: str | None = Field(
        default=None, alias="AccountManagerFullName"
    )
    main_contact: UUID | None = Field(default=None, alias="MainContact")
    invoice_account: UUID | None = Field(default=None, alias="InvoiceAccount")
    invoice_account_code: str | None = Field(default=None, alias="InvoiceAccountCode")
    invoice_account_name: str | None = Field(default=None, alias="InvoiceAccountName")
    parent: UUID | None = Field(default=None, alias="Parent")
    reseller: UUID | None = Field(default=None, alias="Reseller")
    price_list: UUID | None = Field(default=None, alias="PriceList")
    gl_account_purchase: UUID | None = Field(default=None, alias="GLAccountPurchase")
    gl_account_sales: UUID | None = Field(default=None, alias="GLAccountSales")
    glap: UUID | None = Field(default=None, alias="GLAP")
    glar: UUID | None = Field(default=None, alias="GLAR")
    invoicing_method: int | None = Field(default=None, alias="InvoicingMethod")
    invoice_attachment_type: int | None = Field(
        default=None, alias="InvoiceAttachmentType"
    )
    language: str | None = Field(default=None, alias="Language")
    language_description: str | None = Field(default=None, alias="LanguageDescription")
    division: int | None = Field(default=None, alias="Division")
    created: ODataDateTime = Field(default=None, alias="Created")
    creator: UUID | None = Field(default=None, alias="Creator")
    creator_full_name: str | None = Field(default=None, alias="CreatorFullName")
    modified: ODataDateTime = Field(default=None, alias="Modified")
    modifier: UUID | None = Field(default=None, alias="Modifier")
    modifier_full_name: str | None = Field(default=None, alias="ModifierFullName")
    start_date: ODataDateTime = Field(default=None, alias="StartDate")
    end_date: ODataDateTime = Field(default=None, alias="EndDate")
    remarks: str | None = Field(default=None, alias="Remarks")
    trade_name: str | None = Field(default=None, alias="TradeName")
    type: str | None = Field(default=None, alias="Type")
