"""Main client for Exact Online API."""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from types import TracebackType
from typing import TYPE_CHECKING, Any
from urllib.parse import parse_qs, quote, urlparse

import httpx

from exact_online.auth import OAuth, SyncState
from exact_online.exceptions import APIError, RateLimitError
from exact_online.models.sync import DeletedRecord, EntityType
from exact_online.rate_limiter import RateLimiter
from exact_online.retry import RetryableError, RetryConfig, with_retry

logger = logging.getLogger("exact_online.client")

if TYPE_CHECKING:
    from exact_online.api.accounts import AccountsAPI
    from exact_online.api.divisions import DivisionsAPI
    from exact_online.api.goods_receipt_lines import GoodsReceiptLinesAPI
    from exact_online.api.goods_receipts import GoodsReceiptsAPI
    from exact_online.api.me import MeAPI
    from exact_online.api.purchase_order_lines import PurchaseOrderLinesAPI
    from exact_online.api.purchase_orders import PurchaseOrdersAPI
    from exact_online.api.sales_orders import SalesOrdersAPI
    from exact_online.api.shop_orders import ShopOrdersAPI
    from exact_online.api.stock_count_lines import StockCountLinesAPI
    from exact_online.api.stock_counts import StockCountsAPI
    from exact_online.api.supplier_items import SupplierItemsAPI
    from exact_online.api.units import UnitsAPI
    from exact_online.api.warehouse_transfers import WarehouseTransfersAPI
    from exact_online.api.warehouses import WarehousesAPI
    from exact_online.batch import BatchRequest, BatchResult


class Client:
    """Main client for interacting with the Exact Online API.

    Handles:
    - HTTP requests with authentication
    - Rate limiting per division
    - Automatic retries with exponential backoff
    - Connection pooling
    - Response parsing and error handling

    Usage:
        async with Client(oauth=oauth) as client:
            orders = await client.purchase_orders.list(division=123)

    With custom configuration:
        async with Client(
            oauth=oauth,
            timeout=60.0,
            max_connections=50,
            retry=RetryConfig(max_retries=5),
        ) as client:
            orders = await client.purchase_orders.list(division=123)
    """

    def __init__(
        self,
        oauth: OAuth,
        http_client: httpx.AsyncClient | None = None,
        timeout: float = 30.0,
        max_connections: int = 100,
        max_keepalive_connections: int = 20,
        keepalive_expiry: float = 5.0,
        retry: RetryConfig | bool | None = None,
    ) -> None:
        """Initialize the client.

        Args:
            oauth: OAuth instance for authentication.
            http_client: Optional httpx client (created if not provided).
            timeout: Request timeout in seconds (default 30.0).
            max_connections: Maximum number of concurrent connections (default 100).
            max_keepalive_connections: Max connections to keep alive (default 20).
            keepalive_expiry: Seconds before idle connections expire (default 5.0).
            retry: Retry configuration. None or True = use defaults, False = disable.
        """
        self.oauth = oauth
        self._http_client = http_client
        self._owns_http_client = http_client is None
        self._timeout = timeout
        self._max_connections = max_connections
        self._max_keepalive_connections = max_keepalive_connections
        self._keepalive_expiry = keepalive_expiry
        self._rate_limiter = RateLimiter()

        if retry is False:
            self._retry_config: RetryConfig | None = None
        elif retry is None or retry is True:
            self._retry_config = RetryConfig()
        else:
            self._retry_config = retry

        self._accounts: AccountsAPI | None = None
        self._me: MeAPI | None = None
        self._divisions: DivisionsAPI | None = None
        self._purchase_orders: PurchaseOrdersAPI | None = None
        self._purchase_order_lines: PurchaseOrderLinesAPI | None = None
        self._sales_orders: SalesOrdersAPI | None = None
        self._shop_orders: ShopOrdersAPI | None = None
        self._warehouse_transfers: WarehouseTransfersAPI | None = None
        self._goods_receipts: GoodsReceiptsAPI | None = None
        self._goods_receipt_lines: GoodsReceiptLinesAPI | None = None
        self._stock_counts: StockCountsAPI | None = None
        self._stock_count_lines: StockCountLinesAPI | None = None
        self._supplier_items: SupplierItemsAPI | None = None
        self._units: UnitsAPI | None = None
        self._warehouses: WarehousesAPI | None = None

    async def _get_http_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client.

        Creates client with configured connection pool limits.
        Also shares the client with OAuth to avoid creating
        multiple clients and ensure proper cleanup.
        """
        if self._http_client is None:
            limits = httpx.Limits(
                max_connections=self._max_connections,
                max_keepalive_connections=self._max_keepalive_connections,
                keepalive_expiry=self._keepalive_expiry,
            )
            self._http_client = httpx.AsyncClient(timeout=self._timeout, limits=limits)
        if self.oauth._http_client is None:
            self.oauth._http_client = self._http_client
            self.oauth._owns_http_client = False
        return self._http_client

    def _build_url(
        self,
        endpoint: str,
        division: int | None,
        params: dict[str, Any] | None,
    ) -> str:
        """Build the full URL with query parameters.

        Args:
            endpoint: API endpoint path.
            division: Division ID (None for division-less endpoints).
            params: Optional query parameters.

        Returns:
            Full URL with encoded query string.
        """
        if division is not None:
            base_url = f"{self.oauth.api_url}/{division}{endpoint}"
        else:
            base_url = f"{self.oauth.api_url}{endpoint}"

        if params:
            query_parts = [f"{k}={quote(str(v), safe='')}" for k, v in params.items()]
            return f"{base_url}?{'&'.join(query_parts)}"
        return base_url

    def _parse_error_message(self, response: httpx.Response) -> str:
        """Extract error message from API response.

        Args:
            response: The HTTP response.

        Returns:
            Error message string.
        """
        try:
            error_data = response.json()
            message = error_data.get("error", {}).get(
                "message", {"value": response.text}
            )
            if isinstance(message, dict):
                message = message.get("value", response.text)
            return str(message)
        except Exception:
            return response.text

    async def _execute_request(
        self,
        method: str,
        url: str,
        json_body: dict[str, Any] | None,
        access_token: str,
    ) -> httpx.Response:
        """Execute an HTTP request with authentication headers.

        Args:
            method: HTTP method.
            url: Full URL to request.
            json_body: Optional JSON body.
            access_token: Bearer token for authentication.

        Returns:
            The HTTP response.
        """
        http = await self._get_http_client()
        return await http.request(
            method=method,
            url=url,
            json=json_body,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
        )

    def _handle_error_response(self, response: httpx.Response) -> None:
        """Handle error responses, raising appropriate exceptions.

        Args:
            response: The HTTP response.

        Raises:
            RetryableError: For 5xx errors.
            APIError: For 4xx errors.
        """
        if response.status_code >= 500:
            raise RetryableError(
                f"Server error: {response.status_code}",
                status_code=response.status_code,
            )

        if response.status_code >= 400:
            message = self._parse_error_message(response)
            logger.error("API error %d: %s", response.status_code, message)
            raise APIError(response.status_code, message)

    @property
    def accounts(self) -> AccountsAPI:
        """Access the CRM Accounts API (customers/suppliers)."""
        if self._accounts is None:
            from exact_online.api.accounts import AccountsAPI

            self._accounts = AccountsAPI(self)
        return self._accounts

    @property
    def me(self) -> MeAPI:
        """Access the Me (current user) API."""
        if self._me is None:
            from exact_online.api.me import MeAPI

            self._me = MeAPI(self)
        return self._me

    @property
    def divisions(self) -> DivisionsAPI:
        """Access the Divisions API (read-only)."""
        if self._divisions is None:
            from exact_online.api.divisions import DivisionsAPI

            self._divisions = DivisionsAPI(self)
        return self._divisions

    @property
    def purchase_orders(self) -> PurchaseOrdersAPI:
        """Access the Purchase Orders API."""
        if self._purchase_orders is None:
            from exact_online.api.purchase_orders import PurchaseOrdersAPI

            self._purchase_orders = PurchaseOrdersAPI(self)
        return self._purchase_orders

    @property
    def purchase_order_lines(self) -> PurchaseOrderLinesAPI:
        """Access the Purchase Order Lines API."""
        if self._purchase_order_lines is None:
            from exact_online.api.purchase_order_lines import (
                PurchaseOrderLinesAPI,
            )

            self._purchase_order_lines = PurchaseOrderLinesAPI(self)
        return self._purchase_order_lines

    @property
    def sales_orders(self) -> SalesOrdersAPI:
        """Access the Sales Orders API."""
        if self._sales_orders is None:
            from exact_online.api.sales_orders import SalesOrdersAPI

            self._sales_orders = SalesOrdersAPI(self)
        return self._sales_orders

    @property
    def shop_orders(self) -> ShopOrdersAPI:
        """Access the Shop Orders API."""
        if self._shop_orders is None:
            from exact_online.api.shop_orders import ShopOrdersAPI

            self._shop_orders = ShopOrdersAPI(self)
        return self._shop_orders

    @property
    def warehouse_transfers(self) -> WarehouseTransfersAPI:
        """Access the Warehouse Transfers API."""
        if self._warehouse_transfers is None:
            from exact_online.api.warehouse_transfers import WarehouseTransfersAPI

            self._warehouse_transfers = WarehouseTransfersAPI(self)
        return self._warehouse_transfers

    @property
    def goods_receipts(self) -> GoodsReceiptsAPI:
        """Access the Goods Receipts API."""
        if self._goods_receipts is None:
            from exact_online.api.goods_receipts import GoodsReceiptsAPI

            self._goods_receipts = GoodsReceiptsAPI(self)
        return self._goods_receipts

    @property
    def goods_receipt_lines(self) -> GoodsReceiptLinesAPI:
        """Access the Goods Receipt Lines API."""
        if self._goods_receipt_lines is None:
            from exact_online.api.goods_receipt_lines import GoodsReceiptLinesAPI

            self._goods_receipt_lines = GoodsReceiptLinesAPI(self)
        return self._goods_receipt_lines

    @property
    def stock_counts(self) -> StockCountsAPI:
        """Access the Stock Counts API."""
        if self._stock_counts is None:
            from exact_online.api.stock_counts import StockCountsAPI

            self._stock_counts = StockCountsAPI(self)
        return self._stock_counts

    @property
    def stock_count_lines(self) -> StockCountLinesAPI:
        """Access the Stock Count Lines API."""
        if self._stock_count_lines is None:
            from exact_online.api.stock_count_lines import StockCountLinesAPI

            self._stock_count_lines = StockCountLinesAPI(self)
        return self._stock_count_lines

    @property
    def supplier_items(self) -> SupplierItemsAPI:
        """Access the Supplier Items API."""
        if self._supplier_items is None:
            from exact_online.api.supplier_items import SupplierItemsAPI

            self._supplier_items = SupplierItemsAPI(self)
        return self._supplier_items

    @property
    def units(self) -> UnitsAPI:
        """Access the Units API (read-only)."""
        if self._units is None:
            from exact_online.api.units import UnitsAPI

            self._units = UnitsAPI(self)
        return self._units

    @property
    def warehouses(self) -> WarehousesAPI:
        """Access the Warehouses API."""
        if self._warehouses is None:
            from exact_online.api.warehouses import WarehousesAPI

            self._warehouses = WarehousesAPI(self)
        return self._warehouses

    async def sync_deleted(
        self,
        division: int,
        entity_types: list[EntityType] | None = None,
    ) -> AsyncIterator[DeletedRecord]:
        """Yield deleted records from Exact Online.

        Fetches records from the central /sync/Deleted endpoint.
        Automatically manages sync state via TokenStorage.

        Args:
            division: The division ID.
            entity_types: Optional filter to specific entity types.
                If None, returns all deleted records.

        Yields:
            DeletedRecord instances with entity_key (the deleted record's ID)
            and entity_type (which resource was deleted).

        Example:
            async for deleted in client.sync_deleted(division):
                match deleted.entity_type:
                    case EntityType.PURCHASE_ORDERS:
                        await db.execute(delete(PurchaseOrder).where(id=deleted.entity_key))
                    case EntityType.SALES_ORDER_HEADERS:
                        await db.execute(delete(SalesOrder).where(id=deleted.entity_key))

        Note:
            Exact Online only keeps deleted records for 2 months.
            If you don't sync for 2+ months, you may miss deletions.
        """
        storage = self.oauth.token_storage
        state = await storage.get_sync_state(division, "_deleted")
        timestamp = state.timestamp if state else 1

        params: dict[str, Any] = {"$filter": f"Timestamp gt {timestamp}"}
        endpoint = "/sync/Deleted"

        highest_timestamp = timestamp

        while True:
            response = await self.request(
                method="GET",
                endpoint=endpoint,
                division=division,
                params=params,
            )

            # Parse response
            data = response.get("d", {})
            if isinstance(data, list):
                results, next_url = data, None
            else:
                results, next_url = data.get("results", []), data.get("__next")

            for item in results:
                record = DeletedRecord.model_validate(item)

                # Filter by entity type if specified
                if entity_types is None or record.entity_type in [e.value for e in entity_types]:
                    yield record

                # Track highest timestamp
                if record.timestamp > highest_timestamp:
                    highest_timestamp = record.timestamp

            if not next_url:
                break

            # Parse next_url for pagination
            parsed = urlparse(next_url)
            params = {}
            if parsed.query:
                for key, values in parse_qs(parsed.query).items():
                    params[key] = values[0] if values else ""

        # Save new sync state
        new_state = SyncState(
            timestamp=highest_timestamp,
            last_sync=datetime.now(UTC),
        )
        await storage.save_sync_state(division, "_deleted", new_state)

    async def request(
        self,
        method: str,
        endpoint: str,
        division: int,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make an authenticated request to the Exact Online API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE).
            endpoint: API endpoint path (e.g., "/purchaseorder/PurchaseOrders").
            division: The division ID.
            params: Optional query parameters.
            json: Optional JSON body for POST/PUT requests.

        Returns:
            Parsed JSON response data.

        Raises:
            RateLimitError: If rate limit is exceeded.
            APIError: If the API returns an error response.
            AuthenticationError: If token refresh fails.
        """

        async def do_request() -> dict[str, Any]:
            await self._rate_limiter.check_and_wait(division)
            access_token = await self.oauth.get_token()
            url = self._build_url(endpoint, division, params)

            logger.debug("API request: %s %s (division=%d)", method, endpoint, division)

            response = await self._execute_request(method, url, json, access_token)

            self._rate_limiter.update_from_headers(
                division, dict(response.headers.items())
            )

            if response.status_code == 429:
                logger.warning("Rate limit exceeded for division %d", division)
                raise RetryableError("Rate limit exceeded", status_code=429)

            self._handle_error_response(response)

            return {} if response.status_code == 204 else response.json()

        if self._retry_config:
            try:
                return await with_retry(do_request, self._retry_config)
            except RetryableError as e:
                if e.status_code == 429:
                    raise RateLimitError("Rate limit exceeded") from e
                raise APIError(e.status_code or 500, str(e)) from e
        return await do_request()

    async def request_without_division(
        self,
        method: str,
        endpoint: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make an authenticated request without a division in the path.

        Used for endpoints like /current/Me that don't require a division.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE).
            endpoint: API endpoint path (e.g., "/current/Me").
            params: Optional query parameters.
            json: Optional JSON body for POST/PUT requests.

        Returns:
            Parsed JSON response data.

        Raises:
            APIError: If the API returns an error response.
            AuthenticationError: If token refresh fails.
        """

        async def do_request() -> dict[str, Any]:
            access_token = await self.oauth.get_token()
            url = self._build_url(endpoint, None, params)

            logger.debug("API request: %s %s", method, endpoint)

            response = await self._execute_request(method, url, json, access_token)

            if response.status_code == 429:
                logger.warning("Rate limit exceeded for endpoint %s", endpoint)
                raise RetryableError("Rate limit exceeded", status_code=429)

            self._handle_error_response(response)

            return {} if response.status_code == 204 else response.json()

        if self._retry_config:
            try:
                return await with_retry(do_request, self._retry_config)
            except RetryableError as e:
                if e.status_code == 429:
                    raise RateLimitError("Rate limit exceeded") from e
                raise APIError(e.status_code or 500, str(e)) from e
        return await do_request()

    async def batch(
        self,
        requests: list[BatchRequest],
    ) -> BatchResult:
        """Execute multiple requests in a single HTTP call.

        Combines multiple API requests into one HTTP request using OData $batch,
        reducing network overhead. GET requests run in parallel; write operations
        are grouped in a changeset for atomicity.

        Args:
            requests: List of BatchRequest objects to execute.

        Returns:
            BatchResult containing responses for each request.

        Example:
            ```python
            from exact_online import BatchRequest

            result = await client.batch([
                BatchRequest("GET", "/purchaseorder/PurchaseOrders", 123),
                BatchRequest("GET", "/crm/Accounts", 123),
            ])
            for response in result:
                if response.is_success:
                    print(response.data)
            ```
        """
        from exact_online.batch import execute_batch

        return await execute_batch(self, requests)

    async def close(self) -> None:
        """Close the HTTP client if we own it."""
        if self._owns_http_client and self._http_client is not None:
            await self._http_client.aclose()
            self._http_client = None

    async def start(self) -> Client:
        """Start the client (alternative to context manager).

        Useful for long-running applications with lifespan management.

        Example:
            ```python
            @asynccontextmanager
            async def lifespan(app):
                await client.start()
                yield
                await client.stop()
            ```
        """
        return self

    async def stop(self) -> None:
        """Stop the client (alternative to context manager).

        Closes the HTTP client and releases resources.
        """
        await self.close()

    async def __aenter__(self) -> Client:
        """Async context manager entry."""
        return await self.start()

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Async context manager exit."""
        await self.stop()
