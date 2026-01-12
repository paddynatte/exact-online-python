"""Reporting Balance API resource."""

from typing import ClassVar

from exact_online.api.base import BaseAPI
from exact_online.models.reporting_balance import ReportingBalance


class ReportingBalanceAPI(BaseAPI[ReportingBalance]):
    """API resource for Reporting Balance.

    Returns summarized financial transaction data grouped by various dimensions.

    Note: For optimal performance, only include reporting year in filters.

    Usage:
        balances = await client.reporting_balance.list(
            division=123,
            odata_filter="ReportingYear eq 2024"
        )
    """

    ENDPOINT: ClassVar[str] = "/financial/ReportingBalance"
    SYNC_ENDPOINT: ClassVar[str | None] = None
    MODEL: ClassVar[type[ReportingBalance]] = ReportingBalance
    ID_FIELD: ClassVar[str] = "ID"
