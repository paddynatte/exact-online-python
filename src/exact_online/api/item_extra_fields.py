"""Item Extra Fields API resource (function endpoint)."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, cast

from exact_online.models.item_extra_field import ItemExtraField

if TYPE_CHECKING:
    from exact_online.client import ExactOnlineClient


class ItemExtraFieldsAPI:
    """API resource for Item Extra Fields.

    This is a function endpoint - only get_for_item() is available.
    No CRUD or sync operations are supported.

    Usage:
        # Get extra fields for an item
        fields = await client.item_extra_fields.get_for_item(
            division=123,
            item_id="item-guid",
            modified=datetime(2024, 1, 1)
        )

        for field in fields:
            print(f"{field.description}: {field.value}")
    """

    ENDPOINT = "/read/logistics/ItemExtraField"

    def __init__(self, client: ExactOnlineClient) -> None:
        """Initialize the API resource."""
        self._client = client

    async def get_for_item(
        self,
        division: int,
        item_id: str,
        modified: datetime,
    ) -> list[ItemExtraField]:
        """Get extra fields for a specific item.

        Both item_id and modified are required parameters.

        Args:
            division: The division ID.
            item_id: The item's GUID.
            modified: The item's last modified date.

        Returns:
            List of ItemExtraField instances.
        """
        modified_str = modified.strftime("%Y-%m-%dT%H:%M:%S")
        endpoint = f"{self.ENDPOINT}(itemId=guid'{item_id}',modified=datetime'{modified_str}')"

        response = await self._client.request(
            method="GET",
            endpoint=endpoint,
            division=division,
        )

        data = response.get("d", {})
        results = data if isinstance(data, list) else data.get("results", [])

        return cast(
            list[ItemExtraField],
            [ItemExtraField.model_validate(item) for item in results],
        )
