"""Pydantic models for Units."""

from uuid import UUID

from pydantic import Field

from exact_online.models.base import ExactBaseModel


class Unit(ExactBaseModel):
    """A unit of measurement in Exact Online.

    Units define how items are measured and sold (e.g., PC, BOX, KG).
    Referenced by SupplierItem.item_unit and SupplierItem.purchase_unit.
    """

    id: UUID = Field(alias="ID")
    active: bool | None = Field(default=None, alias="Active")
    code: str | None = Field(default=None, alias="Code")
    description: str | None = Field(default=None, alias="Description")
    division: int | None = Field(default=None, alias="Division")
    main: int | None = Field(default=None, alias="Main")
    time_unit: str | None = Field(default=None, alias="TimeUnit")
    type: str | None = Field(default=None, alias="Type")
