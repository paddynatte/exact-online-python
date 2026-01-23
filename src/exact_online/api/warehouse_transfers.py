"""Warehouse Transfers API resource."""

from typing import ClassVar

from exact_online.api.base import BaseAPI, ReadableMixin, SyncableMixin, WritableMixin
from exact_online.models.warehouse_transfer import WarehouseTransfer


class WarehouseTransfersAPI(
    BaseAPI[WarehouseTransfer],
    ReadableMixin[WarehouseTransfer],
    WritableMixin[WarehouseTransfer],
    SyncableMixin[WarehouseTransfer],
):
    """API resource for Warehouse Transfers.

    Supports:
    - list(), get(), create(), update(), delete()
    - sync() uses Modified filter (no Sync API support)

    Usage:
        transfers = await client.warehouse_transfers.list(division=123)

        transfer = await client.warehouse_transfers.get(division=123, id="guid")

        transfer = await client.warehouse_transfers.create(
            division=123,
            data={
                "warehouse_from": "guid",
                "warehouse_to": "guid",
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
