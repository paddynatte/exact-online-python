"""Accounts API resource."""

from typing import ClassVar

from exact_online.api.base import BaseAPI
from exact_online.models.account import Account


class AccountsAPI(BaseAPI[Account]):
    """API resource for Accounts (customers, suppliers, relations).

    Supports full CRUD operations and sync.

    Usage:
        # List all accounts
        accounts = await client.accounts.list(division=123)

        # List only suppliers
        suppliers = await client.accounts.list(
            division=123,
            odata_filter="IsSupplier eq true",
        )

        # List only customers
        customers = await client.accounts.list(
            division=123,
            odata_filter="IsSales eq true",
        )

        # Sync (bulk, up to 1000 records)
        result = await client.accounts.sync(division=123, timestamp=0)
    """

    ENDPOINT: ClassVar[str] = "/crm/Accounts"
    SYNC_ENDPOINT: ClassVar[str | None] = "/sync/CRM/Accounts"
    MODEL: ClassVar[type[Account]] = Account
    ID_FIELD: ClassVar[str] = "ID"
