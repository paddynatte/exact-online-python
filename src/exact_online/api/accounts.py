"""Accounts API resource."""

from typing import ClassVar

from exact_online.api.base import BaseAPI, ReadableMixin, SyncableMixin, WritableMixin
from exact_online.models.account import Account


class AccountsAPI(
    BaseAPI[Account],
    ReadableMixin[Account],
    WritableMixin[Account],
    SyncableMixin[Account],
):
    """API resource for CRM Accounts (customers/suppliers).

    Accounts represent business relationships in Exact Online.
    Use IsSupplier=true filter for suppliers, IsSales=true for customers.

    Supports:
    - list(), get(), create(), update(), delete()
    - sync() uses Modified filter (no Sync API support)

    Usage:
        # List all accounts
        accounts = await client.accounts.list(division=123)

        # List only suppliers
        suppliers = await client.accounts.list(
            division=123,
            odata_filter="IsSupplier eq true"
        )

        # List only customers
        customers = await client.accounts.list(
            division=123,
            odata_filter="IsSales eq true"
        )

        # Get specific account
        account = await client.accounts.get(division=123, id="guid")

        # Create a supplier account
        account = await client.accounts.create(
            division=123,
            data={
                "name": "Acme Supplies",
                "is_supplier": True,
                "email": "contact@acme.com",
            }
        )

        # Incremental sync (uses Modified filter)
        async for account in client.accounts.sync(division):
            await db.merge(account)
    """

    ENDPOINT: ClassVar[str] = "/crm/Accounts"
    MODEL: ClassVar[type[Account]] = Account
    ID_FIELD: ClassVar[str] = "ID"
    RESOURCE_NAME: ClassVar[str] = "accounts"
