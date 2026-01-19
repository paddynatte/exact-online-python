"""Divisions API resource."""

from typing import Any, ClassVar

from exact_online.api.base import BaseAPI
from exact_online.models.division import Division


class DivisionsAPI(BaseAPI[Division]):
    """API resource for Divisions (read-only).

    Returns only divisions that are accessible to the signed-in user.
    The primary key is `Code` (int), not a UUID like other entities.

    This endpoint only supports GET operations and sync():
    - sync() uses Modified filter (no Sync API support)

    Usage:
        divisions = await client.divisions.list(division=123)

        division = await client.divisions.get(division=123, id="456")

        # Incremental sync (uses Modified filter)
        async for division in client.divisions.sync(division):
            await db.merge(division)
    """

    ENDPOINT: ClassVar[str] = "/hrm/Divisions"
    MODEL: ClassVar[type[Division]] = Division
    ID_FIELD: ClassVar[str] = "Code"
    RESOURCE_NAME: ClassVar[str] = "divisions"

    async def create(self, division: int, data: dict[str, Any]) -> Division:
        """Not supported - Divisions endpoint is read-only."""
        raise NotImplementedError("Divisions endpoint is read-only (GET only)")

    async def update(self, division: int, id: str, data: dict[str, Any]) -> Division:
        """Not supported - Divisions endpoint is read-only."""
        raise NotImplementedError("Divisions endpoint is read-only (GET only)")

    async def delete(self, division: int, id: str) -> None:
        """Not supported - Divisions endpoint is read-only."""
        raise NotImplementedError("Divisions endpoint is read-only (GET only)")
