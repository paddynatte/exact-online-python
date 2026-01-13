"""Tests for batch operations."""

import pytest
from pytest_httpx import HTTPXMock

from exact_online import (
    Client,
    OAuth,
    TokenData,
)
from exact_online.batch import (
    BatchRequest,
    BatchResponse,
    BatchResult,
    _build_batch_body,
    _parse_batch_response,
    execute_batch,
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
    async with Client(oauth=oauth, retry=False) as c:
        yield c


class TestBatchRequest:
    """Tests for BatchRequest dataclass."""

    def test_create_get_request(self) -> None:
        """Should create a GET request."""
        req = BatchRequest(
            method="GET",
            endpoint="/purchaseorder/PurchaseOrders",
            division=123,
            params={"$top": "5"},
        )

        assert req.method == "GET"
        assert req.endpoint == "/purchaseorder/PurchaseOrders"
        assert req.division == 123
        assert req.params == {"$top": "5"}

    def test_create_post_request(self) -> None:
        """Should create a POST request with JSON body."""
        req = BatchRequest(
            method="POST",
            endpoint="/purchaseorder/PurchaseOrders",
            division=123,
            json={"Supplier": "abc-123"},
        )

        assert req.method == "POST"
        assert req.json == {"Supplier": "abc-123"}

    def test_default_values(self) -> None:
        """Should have None defaults for optional fields."""
        req = BatchRequest(
            method="GET",
            endpoint="/test",
            division=123,
        )

        assert req.params is None
        assert req.json is None
        assert req.content_id is None


class TestBatchResponse:
    """Tests for BatchResponse dataclass."""

    def test_success_response(self) -> None:
        """Should identify success response."""
        response = BatchResponse(
            status_code=200,
            data={"d": {"results": []}},
        )

        assert response.is_success is True
        assert response.is_error is False

    def test_error_response(self) -> None:
        """Should identify error response."""
        response = BatchResponse(
            status_code=400,
            error="Bad Request",
        )

        assert response.is_success is False
        assert response.is_error is True

    def test_204_is_success(self) -> None:
        """204 No Content should be success."""
        response = BatchResponse(status_code=204)

        assert response.is_success is True


class TestBatchResult:
    """Tests for BatchResult dataclass."""

    def test_all_successful(self) -> None:
        """Should detect all successful responses."""
        result = BatchResult(
            responses=[
                BatchResponse(status_code=200),
                BatchResponse(status_code=201),
                BatchResponse(status_code=204),
            ]
        )

        assert result.all_successful is True
        assert result.failed_count == 0

    def test_some_failed(self) -> None:
        """Should detect failed responses."""
        result = BatchResult(
            responses=[
                BatchResponse(status_code=200),
                BatchResponse(status_code=400, error="Bad Request"),
                BatchResponse(status_code=500, error="Server Error"),
            ]
        )

        assert result.all_successful is False
        assert result.failed_count == 2

    def test_iteration(self) -> None:
        """Should be iterable."""
        responses = [
            BatchResponse(status_code=200),
            BatchResponse(status_code=201),
        ]
        result = BatchResult(responses=responses)

        assert list(result) == responses

    def test_len(self) -> None:
        """Should support len()."""
        result = BatchResult(
            responses=[
                BatchResponse(status_code=200),
                BatchResponse(status_code=201),
            ]
        )

        assert len(result) == 2


class TestBuildBatchBody:
    """Tests for _build_batch_body."""

    def test_builds_get_request(self) -> None:
        """Should build body for GET requests."""
        requests = [
            BatchRequest("GET", "/purchaseorder/PurchaseOrders", 123),
        ]

        content_type, body = _build_batch_body(
            requests, "https://start.exactonline.nl/api/v1"
        )

        assert "multipart/mixed" in content_type
        assert "boundary=" in content_type
        assert "GET" in body
        assert "/purchaseorder/PurchaseOrders" in body

    def test_builds_post_in_changeset(self) -> None:
        """Should build POST requests in changeset."""
        requests = [
            BatchRequest(
                "POST",
                "/purchaseorder/PurchaseOrders",
                123,
                json={"Supplier": "test"},
            ),
        ]

        content_type, body = _build_batch_body(
            requests, "https://start.exactonline.nl/api/v1"
        )

        assert "changeset_" in body
        assert "POST" in body
        assert '"Supplier"' in body

    def test_includes_query_params(self) -> None:
        """Should include query parameters in URL."""
        requests = [
            BatchRequest(
                "GET",
                "/purchaseorder/PurchaseOrders",
                123,
                params={"$top": "5", "$filter": "Status eq 10"},
            ),
        ]

        _, body = _build_batch_body(
            requests, "https://start.exactonline.nl/api/v1"
        )

        assert "$top=5" in body
        assert "$filter=Status%20eq%2010" in body


class TestParseBatchResponse:
    """Tests for _parse_batch_response."""

    def test_parse_single_response(self) -> None:
        """Should parse single response."""
        response_text = """--batch_abc123
Content-Type: application/http
Content-Transfer-Encoding: binary

HTTP/1.1 200 OK
Content-Type: application/json

{"d": {"results": []}}
--batch_abc123--"""

        responses = _parse_batch_response(response_text, "batch_abc123")

        assert len(responses) == 1
        assert responses[0].status_code == 200
        assert responses[0].data == {"d": {"results": []}}

    def test_parse_error_response(self) -> None:
        """Should parse error response."""
        response_text = """--batch_abc123
Content-Type: application/http
Content-Transfer-Encoding: binary

HTTP/1.1 400 Bad Request
Content-Type: application/json

{"error": {"message": {"value": "Bad Request"}}}
--batch_abc123--"""

        responses = _parse_batch_response(response_text, "batch_abc123")

        assert len(responses) == 1
        assert responses[0].status_code == 400
        assert responses[0].error == "Bad Request"


class TestExecuteBatch:
    """Tests for execute_batch function."""

    async def test_empty_requests_raises(
        self, client: Client
    ) -> None:
        """Should raise ValueError for empty requests list."""
        with pytest.raises(ValueError, match="cannot be empty"):
            await execute_batch(client, [])

    async def test_execute_get_requests(
        self, client: Client, httpx_mock: HTTPXMock
    ) -> None:
        """Should execute GET requests in batch."""
        httpx_mock.add_response(
            url="https://start.exactonline.nl/api/v1/$batch",
            content=b"""--batch_response
Content-Type: application/http
Content-Transfer-Encoding: binary

HTTP/1.1 200 OK
Content-Type: application/json

{"d": {"results": [{"ID": "1"}]}}
--batch_response--""",
            headers={"Content-Type": "multipart/mixed; boundary=batch_response"},
        )

        result = await execute_batch(
            client,
            [BatchRequest("GET", "/purchaseorder/PurchaseOrders", 123)],
        )

        assert len(result) == 1
        assert result.responses[0].is_success

    async def test_client_batch_method(
        self, client: Client, httpx_mock: HTTPXMock
    ) -> None:
        """Should be callable via client.batch()."""
        httpx_mock.add_response(
            url="https://start.exactonline.nl/api/v1/$batch",
            content=b"""--batch_response
Content-Type: application/http
Content-Transfer-Encoding: binary

HTTP/1.1 200 OK
Content-Type: application/json

{"d": {"results": []}}
--batch_response--""",
            headers={"Content-Type": "multipart/mixed; boundary=batch_response"},
        )

        result = await client.batch([
            BatchRequest("GET", "/purchaseorder/PurchaseOrders", 123),
        ])

        assert isinstance(result, BatchResult)
        assert len(result) == 1
