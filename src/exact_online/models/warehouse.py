"""Pydantic model for Warehouse endpoint."""

from uuid import UUID

from pydantic import Field

from exact_online.models.base import ExactBaseModel, ODataDateTime


class Warehouse(ExactBaseModel):
    """A warehouse in Exact Online.

    Warehouses are locations where inventory is stored.
    Supports full CRUD operations (GET, POST, PUT, DELETE).
    """

    id: UUID = Field(alias="ID")
    code: str | None = Field(default=None, alias="Code")
    created: ODataDateTime = Field(default=None, alias="Created")
    creator: UUID | None = Field(default=None, alias="Creator")
    creator_full_name: str | None = Field(default=None, alias="CreatorFullName")
    default_storage_location: UUID | None = Field(
        default=None, alias="DefaultStorageLocation"
    )
    default_storage_location_code: str | None = Field(
        default=None, alias="DefaultStorageLocationCode"
    )
    default_storage_location_description: str | None = Field(
        default=None, alias="DefaultStorageLocationDescription"
    )
    description: str | None = Field(default=None, alias="Description")
    division: int | None = Field(default=None, alias="Division")
    email: str | None = Field(default=None, alias="EMail")
    main: int | None = Field(default=None, alias="Main")
    manager_user: UUID | None = Field(default=None, alias="ManagerUser")
    modified: ODataDateTime = Field(default=None, alias="Modified")
    modifier: UUID | None = Field(default=None, alias="Modifier")
    modifier_full_name: str | None = Field(default=None, alias="ModifierFullName")
    use_storage_locations: int | None = Field(default=None, alias="UseStorageLocations")
