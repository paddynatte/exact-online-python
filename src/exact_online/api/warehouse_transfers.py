"""Warehouse Transfers API resource."""

from typing import ClassVar

from exact_online.api.base import BaseAPI
from exact_online.models.warehouse_transfer import WarehouseTransfer


class WarehouseTransfersAPI(BaseAPI[WarehouseTransfer]):
    """API resource for Warehouse Transfers.

    Supports full CRUD operations and sync():
    - list, get, create, update, delete
    - sync() uses Modified filter (no Sync API support)

    When WarehouseFrom equals WarehouseTo, it's a location transfer.

    Usage:
        transfers = await client.warehouse_transfers.list(division=123)

        transfer = await client.warehouse_transfers.get(division=123, id="guid")

        transfer = await client.warehouse_transfers.create(
            division=123,
            data={
                "warehouse_from": "from-guid",
                "warehouse_to": "to-guid",
                "warehouse_transfer_lines": [...]
            }
        )

        # Incremental sync (uses Modified filter)
        async for transfer in client.warehouse_transfers.sync(division):
            await db.merge(transfer)
    """

    ENDPOINT: ClassVar[str] = "/inventory/WarehouseTransfers"
    MODEL: ClassVar[type[WarehouseTransfer]] = WarehouseTransfer
    ID_FIELD: ClassVar[str] = "TransferID"
    RESOURCE_NAME: ClassVar[str] = "warehouse_transfers"
