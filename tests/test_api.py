"""Tests for BaseAPI and API resources."""

from datetime import UTC, datetime

import pytest
from pytest_httpx import HTTPXMock

from exact_online import (
    Client,
    OAuth,
    TokenData,
)
from exact_online.models.base import (
    ListResult,
    SyncResult,
    parse_odata_datetime,
)

from .conftest import MockTokenStorage


@pytest.fixture
def oauth(valid_token_data: TokenData) -> OAuth:
    """OAuth with valid tokens."""
    storage = MockTokenStorage(initial_tokens=valid_token_data)
    return OAuth(
        client_id="test_client_id",
        client_secret="test_client_secret",
        redirect_uri="https://example.com/callback",
        token_storage=storage,
    )


@pytest.fixture
async def client(oauth: OAuth) -> Client:  # type: ignore[misc]
    """Client for testing."""
    async with Client(oauth=oauth) as c:
        yield c


class TestListResult:
    """Tests for ListResult dataclass."""

    def test_iteration(self) -> None:
        """ListResult should be iterable."""
        items = ["a", "b", "c"]
        result: ListResult[str] = ListResult(items=items, next_url=None)

        assert list(result) == items

    def test_len(self) -> None:
        """ListResult should support len()."""
        result: ListResult[int] = ListResult(items=[1, 2, 3], next_url=None)

        assert len(result) == 3

    def test_has_more_false(self) -> None:
        """has_more should be False when next_url is None."""
        result: ListResult[str] = ListResult(items=[], next_url=None)

        assert result.has_more is False

    def test_has_more_true(self) -> None:
        """has_more should be True when next_url exists."""
        result: ListResult[str] = ListResult(
            items=[], next_url="http://example.com/next"
        )

        assert result.has_more is True


class TestSyncResult:
    """Tests for SyncResult dataclass."""

    def test_attributes(self) -> None:
        """SyncResult should have correct attributes."""
        result: SyncResult[int] = SyncResult(
            items=[1, 2], timestamp=12345, has_more=True
        )

        assert result.items == [1, 2]
        assert result.timestamp == 12345
        assert result.has_more is True


class TestBaseAPIList:
    """Tests for BaseAPI.list() method."""

    async def test_list_returns_list_result(
        self, client: Client, httpx_mock: HTTPXMock
    ) -> None:
        """list() should return a ListResult."""
        httpx_mock.add_response(
            json={
                "d": {
                    "results": [
                        {
                            "PurchaseOrderID": "11111111-1111-1111-1111-111111111111",
                            "OrderNumber": 1001,
                            "Supplier": "00000000-0000-0000-0000-000000000001",
                        }
                    ],
                    "__next": None,
                }
            },
        )

        result = await client.purchase_orders.list(division=123)

        assert isinstance(result, ListResult)
        assert len(result) == 1
        assert result.has_more is False

    async def test_list_with_filter(
        self, client: Client, httpx_mock: HTTPXMock
    ) -> None:
        """list() should pass OData filter."""
        httpx_mock.add_response(
            json={"d": {"results": [], "__next": None}},
        )

        await client.purchase_orders.list(
            division=123,
            odata_filter="Status eq 10",
        )

        request = httpx_mock.get_request()
        assert request is not None
        assert "$filter" in str(request.url)

    async def test_list_pagination(
        self, client: Client, httpx_mock: HTTPXMock
    ) -> None:
        """list() should return next_url for pagination."""
        next_url = "https://start.exactonline.nl/api/v1/123/purchaseorder/PurchaseOrders?$skiptoken=guid'abc'"
        httpx_mock.add_response(
            json={
                "d": {
                    "results": [
                        {
                            "PurchaseOrderID": "22222222-2222-2222-2222-222222222222",
                            "Supplier": "00000000-0000-0000-0000-000000000001",
                        }
                    ],
                    "__next": next_url,
                }
            },
        )

        result = await client.purchase_orders.list(division=123)

        assert result.has_more is True
        assert result.next_url == next_url


class TestBaseAPISync:
    """Tests for BaseAPI.sync() method."""

    async def test_sync_returns_sync_result(
        self, client: Client, httpx_mock: HTTPXMock
    ) -> None:
        """sync() should return a SyncResult."""
        httpx_mock.add_response(
            json={
                "d": {
                    "results": [
                        {
                            "PurchaseOrderID": "33333333-3333-3333-3333-333333333333",
                            "Supplier": "00000000-0000-0000-0000-000000000001",
                            "Timestamp": 12345,
                        }
                    ]
                }
            },
        )

        result = await client.purchase_orders.sync(division=123, timestamp=0)

        assert isinstance(result, SyncResult)
        assert result.timestamp == 12345
        assert result.has_more is False

    async def test_sync_handles_null_timestamp(
        self, client: Client, httpx_mock: HTTPXMock
    ) -> None:
        """sync() should handle null Timestamp values without crashing."""
        httpx_mock.add_response(
            json={
                "d": {
                    "results": [
                        {
                            "PurchaseOrderID": "44444444-4444-4444-4444-444444444444",
                            "Supplier": "00000000-0000-0000-0000-000000000001",
                            "Timestamp": None,
                        },
                        {
                            "PurchaseOrderID": "55555555-5555-5555-5555-555555555555",
                            "Supplier": "00000000-0000-0000-0000-000000000001",
                            "Timestamp": 99999,
                        },
                    ]
                }
            },
        )

        result = await client.purchase_orders.sync(division=123, timestamp=0)

        assert result.timestamp == 99999

    async def test_sync_has_more_when_1000_results(
        self, client: Client, httpx_mock: HTTPXMock
    ) -> None:
        """sync() should set has_more=True when 1000 results returned."""
        results = [
            {
                "PurchaseOrderID": f"00000000-0000-0000-0000-{i:012d}",
                "Supplier": "00000000-0000-0000-0000-000000000001",
                "Timestamp": i,
            }
            for i in range(1000)
        ]
        httpx_mock.add_response(json={"d": {"results": results}})

        result = await client.purchase_orders.sync(division=123)

        assert result.has_more is True
        assert result.timestamp == 999


class TestRateLimiter:
    """Tests for rate limiting."""

    async def test_rate_limit_headers_case_insensitive(
        self, client: Client, httpx_mock: HTTPXMock
    ) -> None:
        """Rate limiter should handle lowercase headers."""
        httpx_mock.add_response(
            json={"d": {"results": []}},
            headers={
                "x-ratelimit-minutely-limit": "60",
                "x-ratelimit-minutely-remaining": "45",
            },
        )

        await client.purchase_orders.list(division=123)

        remaining = client._rate_limiter.get_remaining(123)
        assert remaining == 45


class TestODataDateTime:
    """Tests for OData datetime parsing."""

    def test_parse_odata_format(self) -> None:
        """Should parse /Date(milliseconds)/ format."""
        value = "/Date(1704412800000)/"
        result = parse_odata_datetime(value)

        assert isinstance(result, datetime)
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 5

    def test_parse_none(self) -> None:
        """Should return None for None input."""
        result = parse_odata_datetime(None)
        assert result is None

    def test_parse_already_datetime(self) -> None:
        """Should return datetime as-is."""
        dt = datetime.now(UTC)
        result = parse_odata_datetime(dt)
        assert result is dt

    def test_parse_iso_format(self) -> None:
        """Should parse ISO format as fallback."""
        value = "2024-01-05T00:00:00Z"
        result = parse_odata_datetime(value)

        assert isinstance(result, datetime)
        assert result.year == 2024


class TestListNextWithListFormat:
    """Tests for list_next handling list response format."""

    async def test_list_next_handles_list_format(
        self, client: Client, httpx_mock: HTTPXMock
    ) -> None:
        """list_next() should handle when d is a list."""
        next_url = "https://start.exactonline.nl/api/v1/123/purchaseorder/PurchaseOrders?$skiptoken=guid'abc'"
        httpx_mock.add_response(
            json={
                "d": {
                    "results": [
                        {
                            "PurchaseOrderID": "11111111-1111-1111-1111-111111111111",
                            "Supplier": "00000000-0000-0000-0000-000000000001",
                        }
                    ],
                    "__next": next_url,
                }
            },
        )
        httpx_mock.add_response(
            json={
                "d": [
                    {
                        "PurchaseOrderID": "22222222-2222-2222-2222-222222222222",
                        "Supplier": "00000000-0000-0000-0000-000000000001",
                    }
                ]
            },
        )

        result = await client.purchase_orders.list(division=123)
        assert result.has_more is True
        assert result.next_url is not None

        result2 = await client.purchase_orders.list_next(result.next_url, division=123)
        assert len(result2) == 1
        assert result2.has_more is False


class TestReprMethods:
    """Tests for __repr__ methods."""

    def test_list_result_repr(self) -> None:
        """ListResult should have readable repr."""
        result: ListResult[str] = ListResult(items=["a", "b"], next_url="http://next")
        repr_str = repr(result)

        assert "ListResult" in repr_str
        assert "items=2" in repr_str
        assert "has_more=True" in repr_str

    def test_sync_result_repr(self) -> None:
        """SyncResult should have readable repr."""
        result: SyncResult[int] = SyncResult(
            items=[1, 2, 3], timestamp=999, has_more=True
        )
        repr_str = repr(result)

        assert "SyncResult" in repr_str
        assert "items=3" in repr_str
        assert "timestamp=999" in repr_str


class TestTimeoutConfig:
    """Tests for timeout configuration."""

    async def test_default_timeout(
        self, oauth: OAuth
    ) -> None:
        """Client should use default timeout."""
        async with Client(oauth=oauth) as client:
            assert client._timeout == 30.0

    async def test_custom_timeout(
        self, oauth: OAuth
    ) -> None:
        """Client should use custom timeout."""
        async with Client(oauth=oauth, timeout=60.0) as client:
            assert client._timeout == 60.0


class TestListAll:
    """Tests for list_all() auto-pagination."""

    async def test_list_all_single_page(
        self, client: Client, httpx_mock: HTTPXMock
    ) -> None:
        """list_all() should yield all items from single page."""
        httpx_mock.add_response(
            json={
                "d": {
                    "results": [
                        {
                            "PurchaseOrderID": "11111111-1111-1111-1111-111111111111",
                            "Supplier": "00000000-0000-0000-0000-000000000001",
                        },
                        {
                            "PurchaseOrderID": "22222222-2222-2222-2222-222222222222",
                            "Supplier": "00000000-0000-0000-0000-000000000001",
                        },
                    ],
                    "__next": None,
                }
            },
        )

        items = []
        async for item in client.purchase_orders.list_all(division=123):
            items.append(item)

        assert len(items) == 2

    async def test_list_all_multiple_pages(
        self, client: Client, httpx_mock: HTTPXMock
    ) -> None:
        """list_all() should auto-paginate through multiple pages."""
        next_url = "https://start.exactonline.nl/api/v1/123/purchaseorder/PurchaseOrders?$skiptoken=guid'abc'"
        httpx_mock.add_response(
            json={
                "d": {
                    "results": [
                        {
                            "PurchaseOrderID": "11111111-1111-1111-1111-111111111111",
                            "Supplier": "00000000-0000-0000-0000-000000000001",
                        },
                    ],
                    "__next": next_url,
                }
            },
        )
        httpx_mock.add_response(
            json={
                "d": {
                    "results": [
                        {
                            "PurchaseOrderID": "22222222-2222-2222-2222-222222222222",
                            "Supplier": "00000000-0000-0000-0000-000000000001",
                        },
                    ],
                    "__next": None,
                }
            },
        )

        items = []
        async for item in client.purchase_orders.list_all(division=123):
            items.append(item)

        assert len(items) == 2
