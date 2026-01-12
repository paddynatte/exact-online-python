"""Accounts API resource."""

from typing import ClassVar

from exact_online.api.base import BaseAPI
from exact_online.models.account import Account


class AccountsAPI(BaseAPI[Account]):
    """API resource for Accounts (customers, suppliers, relations).

    Supports full CRUD operations and sync (bulk, up to 1000 records).

    Usage:
        accounts = await client.accounts.list(division=123)

        suppliers = await client.accounts.list(
            division=123,
            odata_filter="IsSupplier eq true",
        )

        customers = await client.accounts.list(
            division=123,
            odata_filter="IsSales eq true",
        )

        result = await client.accounts.sync(division=123, timestamp=0)
    """

    ENDPOINT: ClassVar[str] = "/crm/Accounts"
    SYNC_ENDPOINT: ClassVar[str | None] = "/sync/CRM/Accounts"
    MODEL: ClassVar[type[Account]] = Account
    ID_FIELD: ClassVar[str] = "ID"
