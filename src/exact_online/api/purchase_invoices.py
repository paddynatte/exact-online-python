"""Purchase Invoices API resource."""

from typing import ClassVar

from exact_online.api.base import BaseAPI
from exact_online.models.purchase_invoice import PurchaseInvoice


class PurchaseInvoicesAPI(BaseAPI[PurchaseInvoice]):
    """API resource for Purchase Invoices.

    Manage purchase invoices and direct purchase invoices (bulk, up to 1000 records).

    Direct purchase invoices combine invoice and receipt - no purchase order needed.
    To create a direct purchase invoice, specify the receiving warehouse.

    Usage:
        invoices = await client.purchase_invoices.list(division=123)

        invoices = await client.purchase_invoices.list(
            division=123,
            odata_filter="Warehouse ne null"
        )

        invoice = await client.purchase_invoices.create(
            division=123,
            data={
                "Supplier": "guid",
                "Warehouse": "guid",
                "PurchaseInvoiceLines": [...]
            }
        )
    """

    ENDPOINT: ClassVar[str] = "/purchase/PurchaseInvoices"
    SYNC_ENDPOINT: ClassVar[str | None] = None
    MODEL: ClassVar[type[PurchaseInvoice]] = PurchaseInvoice
    ID_FIELD: ClassVar[str] = "ID"
