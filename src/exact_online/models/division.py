"""Pydantic model for Division endpoint."""

from uuid import UUID

from pydantic import Field

from exact_online.models.base import ExactBaseModel, ODataDateTime


class Division(ExactBaseModel):
    """A division (company administration) in Exact Online.

    Divisions represent separate company administrations that users can access.
    The primary key is `code` (int), not a UUID like other entities.
    """

    code: int = Field(alias="Code")  # Primary key
    archive_date: ODataDateTime = Field(default=None, alias="ArchiveDate")
    blocking_status: int | None = Field(default=None, alias="BlockingStatus")
    country: str | None = Field(default=None, alias="Country")
    country_description: str | None = Field(default=None, alias="CountryDescription")
    created: ODataDateTime = Field(default=None, alias="Created")
    creator: UUID | None = Field(default=None, alias="Creator")
    creator_full_name: str | None = Field(default=None, alias="CreatorFullName")
    currency: str | None = Field(default=None, alias="Currency")
    currency_description: str | None = Field(default=None, alias="CurrencyDescription")
    customer: UUID | None = Field(default=None, alias="Customer")
    customer_code: str | None = Field(default=None, alias="CustomerCode")
    customer_name: str | None = Field(default=None, alias="CustomerName")
    description: str | None = Field(default=None, alias="Description")
    hid: int | None = Field(default=None, alias="HID")
    main: bool | None = Field(default=None, alias="Main")
    modified: ODataDateTime = Field(default=None, alias="Modified")
    modifier: UUID | None = Field(default=None, alias="Modifier")
    modifier_full_name: str | None = Field(default=None, alias="ModifierFullName")
    ob_number: str | None = Field(default=None, alias="OBNumber")
    siret_number: str | None = Field(default=None, alias="SiretNumber")
    start_date: ODataDateTime = Field(default=None, alias="StartDate")
    status: int | None = Field(default=None, alias="Status")
    tax_office_number: str | None = Field(default=None, alias="TaxOfficeNumber")
    tax_reference_number: str | None = Field(default=None, alias="TaxReferenceNumber")
    template_code: str | None = Field(default=None, alias="TemplateCode")
    vat_number: str | None = Field(default=None, alias="VATNumber")
    website: str | None = Field(default=None, alias="Website")
