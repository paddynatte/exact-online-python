"""Pydantic models for Item Extra Fields."""

from uuid import UUID

from pydantic import Field

from exact_online.models.base import ExactBaseModel, ODataDateTime


class ItemExtraField(ExactBaseModel):
    """
    Extra field information stored on an item.

    Extra information can be defined via Item maintenance and Free field master data.
    The Number field determines the unique name as FreeField{Number}.
    """

    description: str | None = Field(default=None, alias="Description")
    item_id: UUID | None = Field(default=None, alias="ItemID")
    modified: ODataDateTime = Field(default=None, alias="Modified")
    number: int | None = Field(default=None, alias="Number")
    value: str | None = Field(default=None, alias="Value")

    def __repr__(self) -> str:
        """Return a readable representation."""
        return f"ItemExtraField(number={self.number}, description={self.description!r}, value={self.value!r})"
