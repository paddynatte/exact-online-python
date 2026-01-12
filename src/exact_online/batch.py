"""Batch operations for combining multiple API requests into a single HTTP call."""

from __future__ import annotations

import json
import logging
import uuid
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any
from urllib.parse import quote

from exact_online.exceptions import APIError
from exact_online.retry import RetryableError, with_retry

if TYPE_CHECKING:
    from exact_online.client import Client

logger = logging.getLogger("exact_online.batch")

BATCH_BOUNDARY = "batch_boundary"
CHANGESET_BOUNDARY = "changeset_boundary"


@dataclass
class BatchRequest:
    """A single request within a batch operation.

    Attributes:
        method: HTTP method (GET, POST, PUT, DELETE).
        endpoint: API endpoint path (e.g., "/purchaseorder/PurchaseOrders").
        division: The division ID.
        params: Optional query parameters.
        json: Optional JSON body for POST/PUT requests.
        content_id: Optional content ID for referencing in changesets.
    """

    method: str
    endpoint: str
    division: int
    params: dict[str, Any] | None = None
    json: dict[str, Any] | None = None
    content_id: str | None = None


@dataclass
class BatchResponse:
    """Response for a single request within a batch.

    Attributes:
        status_code: HTTP status code of the response.
        data: Parsed JSON response data (or empty dict for 204).
        error: Error message if the request failed.
        content_id: Content ID if provided in the request.
    """

    status_code: int
    data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    content_id: str | None = None

    @property
    def is_success(self) -> bool:
        """Check if the response indicates success."""
        return 200 <= self.status_code < 300

    @property
    def is_error(self) -> bool:
        """Check if the response indicates an error."""
        return self.status_code >= 400


@dataclass
class BatchResult:
    """Result of a batch operation.

    Attributes:
        responses: List of responses for each request in the batch.
    """

    responses: list[BatchResponse]

    @property
    def all_successful(self) -> bool:
        """Check if all requests in the batch succeeded."""
        return all(r.is_success for r in self.responses)

    @property
    def failed_count(self) -> int:
        """Count of failed requests in the batch."""
        return sum(1 for r in self.responses if r.is_error)

    def __iter__(self) -> Iterator[BatchResponse]:
        """Iterate over responses."""
        return iter(self.responses)

    def __len__(self) -> int:
        """Return number of responses."""
        return len(self.responses)


def _build_request_url(base_url: str, req: BatchRequest) -> str:
    """Build a full URL for a batch request with encoded query parameters.

    Args:
        base_url: Base API URL.
        req: The batch request.

    Returns:
        Full URL with encoded query string.
    """
    url = f"{base_url}/{req.division}{req.endpoint}"
    if req.params:
        query = "&".join(
            f"{k}={quote(str(v), safe='')}" for k, v in req.params.items()
        )
        url = f"{url}?{query}"
    return url


def _build_batch_body(
    requests: list[BatchRequest],
    base_url: str,
) -> tuple[str, str]:
    """Build the multipart batch request body.

    Args:
        requests: List of batch requests.
        base_url: Base API URL.

    Returns:
        Tuple of (content_type, body).
    """
    boundary = f"batch_{uuid.uuid4().hex}"
    changeset_boundary = f"changeset_{uuid.uuid4().hex}"

    parts: list[str] = []

    get_requests = [r for r in requests if r.method.upper() == "GET"]
    write_requests = [r for r in requests if r.method.upper() != "GET"]

    for req in get_requests:
        url = _build_request_url(base_url, req)

        part = [
            f"--{boundary}",
            "Content-Type: application/http",
            "Content-Transfer-Encoding: binary",
            "",
            f"GET {url} HTTP/1.1",
            "Accept: application/json",
            "",
        ]
        parts.append("\r\n".join(part))

    if write_requests:
        changeset_parts: list[str] = []
        for i, req in enumerate(write_requests):
            content_id = req.content_id or str(i + 1)
            url = _build_request_url(base_url, req)

            body = json.dumps(req.json) if req.json else ""

            part = [
                f"--{changeset_boundary}",
                "Content-Type: application/http",
                "Content-Transfer-Encoding: binary",
                f"Content-ID: {content_id}",
                "",
                f"{req.method.upper()} {url} HTTP/1.1",
                "Content-Type: application/json",
                "Accept: application/json",
                "",
                body,
            ]
            changeset_parts.append("\r\n".join(part))

        changeset_parts.append(f"--{changeset_boundary}--")

        changeset = [
            f"--{boundary}",
            f"Content-Type: multipart/mixed; boundary={changeset_boundary}",
            "",
            "\r\n".join(changeset_parts),
        ]
        parts.append("\r\n".join(changeset))

    parts.append(f"--{boundary}--")

    body = "\r\n".join(parts)
    content_type = f"multipart/mixed; boundary={boundary}"

    return content_type, body


def _parse_batch_response(response_text: str, boundary: str) -> list[BatchResponse]:
    """Parse a multipart batch response.

    Args:
        response_text: Raw response body.
        boundary: Boundary string from Content-Type header.

    Returns:
        List of parsed BatchResponse objects.
    """
    responses: list[BatchResponse] = []

    boundary = boundary.strip('"')
    parts = response_text.split(f"--{boundary}")

    for part in parts:
        part = part.strip()
        if not part or part == "--":
            continue

        if "multipart/mixed" in part:
            nested_boundary_start = part.find("boundary=")
            if nested_boundary_start != -1:
                nested_boundary_end = part.find("\r\n", nested_boundary_start)
                if nested_boundary_end == -1:
                    nested_boundary_end = part.find("\n", nested_boundary_start)
                nested_boundary = part[nested_boundary_start + 9 : nested_boundary_end]
                nested_boundary = nested_boundary.strip().strip('"')
                nested_responses = _parse_batch_response(part, nested_boundary)
                responses.extend(nested_responses)
            continue

        content_id = None
        content_id_start = part.find("Content-ID:")
        if content_id_start != -1:
            content_id_end = part.find("\r\n", content_id_start)
            if content_id_end == -1:
                content_id_end = part.find("\n", content_id_start)
            content_id = part[content_id_start + 11 : content_id_end].strip()

        http_start = part.find("HTTP/1.1")
        if http_start == -1:
            continue

        status_line_end = part.find("\r\n", http_start)
        if status_line_end == -1:
            status_line_end = part.find("\n", http_start)
        status_line = part[http_start:status_line_end]

        try:
            status_parts = status_line.split(" ", 2)
            status_code = int(status_parts[1])
        except (IndexError, ValueError):
            continue

        body_start = part.find("\r\n\r\n", http_start)
        if body_start == -1:
            body_start = part.find("\n\n", http_start)
        body = "" if body_start == -1 else part[body_start:].strip()

        data: dict[str, Any] = {}
        error: str | None = None

        if body:
            try:
                data = json.loads(body)
                if status_code >= 400:
                    error_info = data.get("error", {})
                    if isinstance(error_info, dict):
                        msg = error_info.get("message", {})
                        error = msg.get("value") if isinstance(msg, dict) else str(msg)
                    else:
                        error = str(error_info)
            except json.JSONDecodeError:
                if status_code >= 400:
                    error = body

        responses.append(
            BatchResponse(
                status_code=status_code,
                data=data,
                error=error,
                content_id=content_id,
            )
        )

    return responses


async def execute_batch(
    client: Client,
    requests: list[BatchRequest],
) -> BatchResult:
    """Execute multiple requests in a single HTTP call using OData $batch.

    This combines multiple API requests into a single HTTP request, reducing
    network overhead. GET requests are executed in parallel, while write
    operations (POST, PUT, DELETE) are grouped in a changeset for atomicity.

    Args:
        client: Client instance.
        requests: List of BatchRequest objects to execute.

    Returns:
        BatchResult containing responses for each request.

    Raises:
        APIError: If the batch request itself fails.
        ValueError: If requests list is empty.

    Example:
        ```python
        result = await execute_batch(client, [
            BatchRequest("GET", "/purchaseorder/PurchaseOrders", 123),
            BatchRequest("GET", "/crm/Accounts", 123),
            BatchRequest("POST", "/purchaseorder/PurchaseOrders", 123, json={...}),
        ])
        for response in result.responses:
            if response.is_success:
                print(response.data)
            else:
                print(f"Error: {response.error}")
        ```
    """
    if not requests:
        raise ValueError("Batch requests list cannot be empty")

    base_url = client.oauth.region.api_url

    async def do_batch() -> BatchResult:
        access_token = await client.oauth.get_token()
        content_type, body = _build_batch_body(requests, base_url)

        http = await client._get_http_client()
        response = await http.post(
            f"{base_url}/$batch",
            content=body.encode("utf-8"),
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": content_type,
                "Accept": "multipart/mixed",
            },
        )

        if response.status_code >= 500:
            raise RetryableError(
                f"Server error: {response.status_code}",
                status_code=response.status_code,
            )

        if response.status_code >= 400:
            raise APIError(response.status_code, response.text)

        response_content_type = response.headers.get("Content-Type", "")
        boundary_start = response_content_type.find("boundary=")
        if boundary_start == -1:
            raise APIError(500, "Invalid batch response: missing boundary")

        boundary = response_content_type[boundary_start + 9 :].split(";")[0].strip()
        parsed_responses = _parse_batch_response(response.text, boundary)

        return BatchResult(responses=parsed_responses)

    if client._retry_config:
        try:
            return await with_retry(do_batch, client._retry_config)
        except RetryableError as e:
            raise APIError(e.status_code or 500, str(e)) from e

    return await do_batch()
