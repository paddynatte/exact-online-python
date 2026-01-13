"""Main client for Exact Online API."""

from __future__ import annotations

import logging
from datetime import datetime
from types import TracebackType
from typing import TYPE_CHECKING, Any
from urllib.parse import quote

import httpx

from exact_online.auth import OAuth
from exact_online.exceptions import APIError, RateLimitError
from exact_online.rate_limiter import RateLimiter
from exact_online.retry import RetryableError, RetryConfig, with_retry

logger = logging.getLogger("exact_online.client")

if TYPE_CHECKING:
    from exact_online.api.me import MeAPI
    from exact_online.api.purchase_order_lines import PurchaseOrderLinesAPI
    from exact_online.api.purchase_orders import PurchaseOrdersAPI
    from exact_online.api.sales_orders import SalesOrdersAPI
    from exact_online.api.shop_orders import ShopOrdersAPI
    from exact_online.api.warehouse_transfers import WarehouseTransfersAPI
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

        self._me: MeAPI | None = None
        self._purchase_orders: PurchaseOrdersAPI | None = None
        self._purchase_order_lines: PurchaseOrderLinesAPI | None = None
        self._sales_orders: SalesOrdersAPI | None = None
        self._shop_orders: ShopOrdersAPI | None = None
        self._warehouse_transfers: WarehouseTransfersAPI | None = None

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
    def me(self) -> MeAPI:
        """Access the Me (current user) API."""
        if self._me is None:
            from exact_online.api.me import MeAPI

            self._me = MeAPI(self)
        return self._me

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

    async def get_sync_timestamp(
        self,
        division: int,
        endpoint: str,
        modified: datetime,
    ) -> int:
        """Get a sync timestamp starting from a specific Modified date.

        This is Exact Online's recommended way to initialize sync operations.
        Use the returned timestamp with sync() to start syncing from that date.

        Args:
            division: The division ID.
            endpoint: The sync endpoint name. Supported values:
                - "PurchaseOrders" for purchase_orders.sync()
                - "SalesOrderHeaders" for sales_orders.sync()
                - "ShopOrders" for shop_orders.sync()
            modified: Start syncing from records modified on/after this date.

        Returns:
            Timestamp to use with sync() calls.

        Example:
            ```python
            from datetime import datetime

            # Get timestamp for syncing from Jan 1, 2024
            ts = await client.get_sync_timestamp(
                division=123,
                endpoint="PurchaseOrders",
                modified=datetime(2024, 1, 1),
            )

            # Use it for syncing
            result = await client.purchase_orders.sync(division=123, timestamp=ts)
            ```
        """
        modified_str = modified.strftime("%Y-%m-%dT%H:%M:%S")

        response = await self.request(
            method="GET",
            endpoint="/read/sync/Sync/SyncTimestamp",
            division=division,
            params={
                "modified": f"datetime'{modified_str}'",
                "endPoint": f"'{endpoint}'",
            },
        )

        data = response.get("d", {})
        if isinstance(data, list) and len(data) > 0:
            return data[0].get("TimeStampAsBigInt", 0)
        return data.get("TimeStampAsBigInt", 0)

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
