"""Pydantic models for Supplier Items."""

from uuid import UUID

from pydantic import Field

from exact_online.models.base import ExactBaseModel, ODataDateTime


class SupplierItem(ExactBaseModel):
    """Links a supplier to an item with purchase price and unit information.

    The PurchaseUnitFactor converts between the supplier's selling unit
    and the item's base unit:

        Item base unit: PC (pieces)
        Supplier sells: BOX (boxes of 100)
        PurchaseUnitFactor: 100

        Order 5 BOX @ €50 each:
        - Cost: 5 × €50 = €250
        - Inventory: 5 × 100 = 500 PC
    """

    id: UUID = Field(alias="ID")
    barcode: str | None = Field(default=None, alias="Barcode")
    copy_remarks: int | None = Field(default=None, alias="CopyRemarks")
    country_of_origin: str | None = Field(default=None, alias="CountryOfOrigin")
    country_of_origin_description: str | None = Field(
        default=None, alias="CountryOfOriginDescription"
    )
    created: ODataDateTime = Field(default=None, alias="Created")
    creator: UUID | None = Field(default=None, alias="Creator")
    creator_full_name: str | None = Field(default=None, alias="CreatorFullName")
    currency: str | None = Field(default=None, alias="Currency")
    currency_description: str | None = Field(default=None, alias="CurrencyDescription")
    division: int | None = Field(default=None, alias="Division")
    drop_shipment: int | None = Field(default=None, alias="DropShipment")
    end_date: ODataDateTime = Field(default=None, alias="EndDate")
    item: UUID | None = Field(default=None, alias="Item")
    item_code: str | None = Field(default=None, alias="ItemCode")
    item_description: str | None = Field(default=None, alias="ItemDescription")
    item_unit: UUID | None = Field(default=None, alias="ItemUnit")
    item_unit_code: str | None = Field(default=None, alias="ItemUnitCode")
    item_unit_description: str | None = Field(default=None, alias="ItemUnitDescription")
    main_supplier: bool | None = Field(default=None, alias="MainSupplier")
    minimum_quantity: float | None = Field(default=None, alias="MinimumQuantity")
    modified: ODataDateTime = Field(default=None, alias="Modified")
    modifier: UUID | None = Field(default=None, alias="Modifier")
    modifier_full_name: str | None = Field(default=None, alias="ModifierFullName")
    notes: str | None = Field(default=None, alias="Notes")
    purchase_lead_time: int | None = Field(default=None, alias="PurchaseLeadTime")
    purchase_lot_size: int | None = Field(default=None, alias="PurchaseLotSize")
    purchase_price: float | None = Field(default=None, alias="PurchasePrice")
    purchase_unit: str | None = Field(default=None, alias="PurchaseUnit")
    purchase_unit_description: str | None = Field(
        default=None, alias="PurchaseUnitDescription"
    )
    purchase_unit_factor: float | None = Field(default=None, alias="PurchaseUnitFactor")
    purchase_vat_code: str | None = Field(default=None, alias="PurchaseVATCode")
    purchase_vat_code_description: str | None = Field(
        default=None, alias="PurchaseVATCodeDescription"
    )
    start_date: ODataDateTime = Field(default=None, alias="StartDate")
    supplier: UUID | None = Field(default=None, alias="Supplier")
    supplier_code: str | None = Field(default=None, alias="SupplierCode")
    supplier_description: str | None = Field(default=None, alias="SupplierDescription")
    supplier_item_code: str | None = Field(default=None, alias="SupplierItemCode")
