"""Warehouse Transfers API resource."""

from typing import ClassVar

from exact_online.api.base import BaseAPI
from exact_online.models.warehouse_transfer import WarehouseTransfer


class WarehouseTransfersAPI(BaseAPI[WarehouseTransfer]):
    """API resource for Warehouse Transfers.

    Manage warehouse and location transfers.

    When WarehouseFrom equals WarehouseTo, it's a location transfer.

    Usage:
        # List transfers
        transfers = await client.warehouse_transfers.list(division=123)

        # Get specific transfer
        transfer = await client.warehouse_transfers.get(division=123, id="guid")

        # Create warehouse transfer
        transfer = await client.warehouse_transfers.create(
            division=123,
            data={
                "WarehouseFrom": "from-guid",
                "WarehouseTo": "to-guid",
                "WarehouseTransferLines": [...]
            }
        )
    """

    ENDPOINT: ClassVar[str] = "/inventory/WarehouseTransfers"
    SYNC_ENDPOINT: ClassVar[str | None] = None
    MODEL: ClassVar[type[WarehouseTransfer]] = WarehouseTransfer
    ID_FIELD: ClassVar[str] = "TransferID"
