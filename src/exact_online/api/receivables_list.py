"""Receivables List API resource."""

from typing import ClassVar

from exact_online.api.base import BaseAPI
from exact_online.models.receivables_list import ReceivablesListItem


class ReceivablesListAPI(BaseAPI[ReceivablesListItem]):
    """API resource for Receivables List.

    Get customer payment terms information (Outstanding items report data) (bulk, up to 1000 records).

    Usage:
        receivables = await client.receivables_list.list(division=123)

        receivables = await client.receivables_list.list(
            division=123,
            odata_filter="DueDate lt datetime'2024-12-31'"
        )
    """

    ENDPOINT: ClassVar[str] = "/read/financial/ReceivablesList"
    SYNC_ENDPOINT: ClassVar[str | None] = None
    MODEL: ClassVar[type[ReceivablesListItem]] = ReceivablesListItem
    ID_FIELD: ClassVar[str] = "HID"
