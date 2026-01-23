"""Units API resource."""

from typing import ClassVar

from exact_online.api.base import BaseAPI, ReadableMixin
from exact_online.models.unit import Unit


class UnitsAPI(BaseAPI[Unit], ReadableMixin[Unit]):
    """API resource for Units (read-only).

    Units define how items are measured (e.g., PC, BOX, KG).
    Referenced by SupplierItem for item_unit and purchase_unit.

    This endpoint only supports read operations: list(), get()

    Usage:
        # List all units
        units = await client.units.list(division=123)

        # Get a specific unit
        unit = await client.units.get(division=123, id="guid")

        # Filter active units
        units = await client.units.list(
            division=123,
            odata_filter="Active eq true"
        )
    """

    ENDPOINT: ClassVar[str] = "/logistics/Units"
    MODEL: ClassVar[type[Unit]] = Unit
    ID_FIELD: ClassVar[str] = "ID"
