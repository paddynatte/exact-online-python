"""Payables List API resource."""

from typing import ClassVar

from exact_online.api.base import BaseAPI
from exact_online.models.payables_list import PayablesListItem


class PayablesListAPI(BaseAPI[PayablesListItem]):
    """API resource for Payables List.

    Get supplier payment terms information (Outstanding items report data) (bulk, up to 1000 records).

    Usage:
        payables = await client.payables_list.list(division=123)

        payables = await client.payables_list.list(
            division=123,
            odata_filter="DueDate lt datetime'2024-12-31'"
        )
    """

    ENDPOINT: ClassVar[str] = "/read/financial/PayablesList"
    SYNC_ENDPOINT: ClassVar[str | None] = None
    MODEL: ClassVar[type[PayablesListItem]] = PayablesListItem
    ID_FIELD: ClassVar[str] = "HID"
