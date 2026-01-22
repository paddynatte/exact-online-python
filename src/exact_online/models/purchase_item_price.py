"""Pydantic model for PurchaseItemPrices (Sync) endpoint."""

from uuid import UUID

from pydantic import Field

from exact_online.models.base import ExactBaseModel, ODataDateTime


class PurchaseItemPrice(ExactBaseModel):
    """A purchase item price in Exact Online.

    Purchase prices for items from suppliers.
    This is a sync-only endpoint (read-only via Sync API).
    """

    timestamp: int = Field(alias="Timestamp")
    id: UUID = Field(alias="ID")
    account: UUID | None = Field(default=None, alias="Account")
    account_name: str | None = Field(default=None, alias="AccountName")
    item: UUID | None = Field(default=None, alias="Item")
    item_code: str | None = Field(default=None, alias="ItemCode")
    item_description: str | None = Field(default=None, alias="ItemDescription")
    price: float | None = Field(default=None, alias="Price")
    currency: str | None = Field(default=None, alias="Currency")
    quantity: float | None = Field(default=None, alias="Quantity")
    unit: str | None = Field(default=None, alias="Unit")
    unit_description: str | None = Field(default=None, alias="UnitDescription")
    default_item_unit: str | None = Field(default=None, alias="DefaultItemUnit")
    default_item_unit_description: str | None = Field(
        default=None, alias="DefaultItemUnitDescription"
    )
    number_of_items_per_unit: float | None = Field(
        default=None, alias="NumberOfItemsPerUnit"
    )
    barcode: str | None = Field(default=None, alias="Barcode")
    start_date: ODataDateTime = Field(default=None, alias="StartDate")
    end_date: ODataDateTime = Field(default=None, alias="EndDate")
    division: int | None = Field(default=None, alias="Division")
    created: ODataDateTime = Field(default=None, alias="Created")
    creator: UUID | None = Field(default=None, alias="Creator")
    creator_full_name: str | None = Field(default=None, alias="CreatorFullName")
    modified: ODataDateTime = Field(default=None, alias="Modified")
    modifier: UUID | None = Field(default=None, alias="Modifier")
    modifier_full_name: str | None = Field(default=None, alias="ModifierFullName")
