"""Divisions API resource."""

from typing import ClassVar

from exact_online.api.base import BaseAPI, ReadableMixin, SyncableMixin
from exact_online.models.division import Division


class DivisionsAPI(
    BaseAPI[Division], ReadableMixin[Division], SyncableMixin[Division]
):
    """API resource for Divisions (read-only with sync).

    Returns only divisions that are accessible to the signed-in user.
    The primary key is `Code` (int), not a UUID like other entities.

    This endpoint supports read operations and sync:
    - list(), get()
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
    ID_IS_GUID: ClassVar[bool] = False  # Code is an integer, not a GUID
    RESOURCE_NAME: ClassVar[str] = "divisions"
