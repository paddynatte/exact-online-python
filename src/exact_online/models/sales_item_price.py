"""Pydantic models for Sales Item Prices."""

from uuid import UUID

from pydantic import Field

from exact_online.models.base import ExactBaseModel, ODataDateTime


class SalesItemPrice(ExactBaseModel):
    """
    A sales price for an item.

    When account is provided, creates a Price Agreement.
    Without account, creates a standard sales price.
    """

    id: UUID = Field(alias="ID")
    account: UUID | None = Field(default=None, alias="Account")
    account_name: str | None = Field(default=None, alias="AccountName")
    barcode: str | None = Field(default=None, alias="Barcode")
    created: ODataDateTime = Field(default=None, alias="Created")
    creator: UUID | None = Field(default=None, alias="Creator")
    creator_full_name: str | None = Field(default=None, alias="CreatorFullName")
    currency: str | None = Field(default=None, alias="Currency")
    default_item_unit: str | None = Field(default=None, alias="DefaultItemUnit")
    default_item_unit_description: str | None = Field(default=None, alias="DefaultItemUnitDescription")
    division: int | None = Field(default=None, alias="Division")
    employee: UUID | None = Field(default=None, alias="Employee")
    end_date: ODataDateTime = Field(default=None, alias="EndDate")
    item: UUID | None = Field(default=None, alias="Item")
    item_code: str | None = Field(default=None, alias="ItemCode")
    item_description: str | None = Field(default=None, alias="ItemDescription")
    modified: ODataDateTime = Field(default=None, alias="Modified")
    modifier: UUID | None = Field(default=None, alias="Modifier")
    modifier_full_name: str | None = Field(default=None, alias="ModifierFullName")
    number_of_items_per_unit: float | None = Field(default=None, alias="NumberOfItemsPerUnit")
    price: float | None = Field(default=None, alias="Price")
    project: UUID | None = Field(default=None, alias="Project")
    project_description: str | None = Field(default=None, alias="ProjectDescription")
    quantity: float | None = Field(default=None, alias="Quantity")
    start_date: ODataDateTime = Field(default=None, alias="StartDate")
    unit: str | None = Field(default=None, alias="Unit")
    unit_description: str | None = Field(default=None, alias="UnitDescription")

    def __repr__(self) -> str:
        """Return a readable representation."""
        return f"SalesItemPrice(item_code={self.item_code!r}, price={self.price})"
