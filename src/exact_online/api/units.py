"""Units API resource."""

from typing import Any, ClassVar

from exact_online.api.base import BaseAPI
from exact_online.models.unit import Unit


class UnitsAPI(BaseAPI[Unit]):
    """API resource for Units (read-only).

    Units define how items are measured (e.g., PC, BOX, KG).
    Referenced by SupplierItem for item_unit and purchase_unit.

    This endpoint only supports GET operations.

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

    async def create(self, division: int, data: dict[str, Any]) -> Unit:
        """Not supported - Units endpoint is read-only."""
        raise NotImplementedError("Units endpoint is read-only (GET only)")

    async def update(self, division: int, id: str, data: dict[str, Any]) -> Unit:
        """Not supported - Units endpoint is read-only."""
        raise NotImplementedError("Units endpoint is read-only (GET only)")

    async def delete(self, division: int, id: str) -> None:
        """Not supported - Units endpoint is read-only."""
        raise NotImplementedError("Units endpoint is read-only (GET only)")
