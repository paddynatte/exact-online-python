"""Base API resource class with CRUD operations."""

from __future__ import annotations

from collections.abc import AsyncIterator, Sequence
from typing import TYPE_CHECKING, Any, ClassVar, cast
from urllib.parse import parse_qs, urlparse

from pydantic import BaseModel

from exact_online.models.base import ListResult

if TYPE_CHECKING:
    from exact_online.client import Client


def _to_pascal(key: str) -> str:
    """Convert snake_case to PascalCase (e.g., supplier_id -> SupplierId)."""
    return "".join(word.capitalize() for word in key.split("_"))


def _convert_to_api(data: Any) -> Any:
    """Recursively convert snake_case dict keys to PascalCase for Exact Online API."""
    if isinstance(data, dict):
        return {_to_pascal(k): _convert_to_api(v) for k, v in data.items()}
    if isinstance(data, list):
        return [_convert_to_api(item) for item in data]
    return data


def _has_snake_keys(data: dict[str, Any]) -> bool:
    """Check if any dict keys contain underscores (snake_case)."""
    return any("_" in key for key in data)


class BaseAPI[TModel: BaseModel]:
    """Base class for API resources.

    Provides common CRUD operations: list, get, create, update, delete.
    Subclasses define ENDPOINT and MODEL.

    Data passed to create() and update() can use either:
    - snake_case keys (e.g., "warehouse_from") - auto-converted to PascalCase
    - PascalCase keys (e.g., "WarehouseFrom") - used as-is
    """

    ENDPOINT: ClassVar[str]
    MODEL: ClassVar[type[BaseModel]]
    ID_FIELD: ClassVar[str] = "ID"

    def __init__(self, client: Client) -> None:
        """Initialize the API resource."""
        self._client = client

    def _prepare_data(self, data: dict[str, Any]) -> dict[str, Any]:
        """Prepare data for API request, converting snake_case to PascalCase if needed."""
        if _has_snake_keys(data):
            return _convert_to_api(data)
        return data

    def _parse_list_response(
        self, response: dict[str, Any]
    ) -> tuple[list[TModel], str | None]:
        """Parse a list API response into items and next_url.

        Handles both formats returned by Exact Online:
        - {"d": {"results": [...], "__next": "..."}}
        - {"d": [...]}

        Args:
            response: Raw API response.

        Returns:
            Tuple of (items, next_url).
        """
        data = response.get("d", {})
        if isinstance(data, list):
            results, next_url = data, None
        else:
            results, next_url = data.get("results", []), data.get("__next")

        items = cast(list[TModel], [self.MODEL.model_validate(item) for item in results])
        return items, next_url

    async def list(
        self,
        division: int,
        *,
        odata_filter: str | None = None,
        select: Sequence[str] | None = None,
        top: int = 60,
    ) -> ListResult[TModel]:
        """List records with optional filtering.

        Returns a ListResult that is iterable. Use .next_url with list_next()
        for pagination.

        Args:
            division: The division ID.
            odata_filter: OData filter expression (e.g., "Status eq 'Open'").
            select: List of fields to return.
            top: Maximum number of records to return (max 60).

        Returns:
            ListResult containing items and next_url for pagination.
        """
        params: dict[str, Any] = {"$top": min(top, 60)}

        if odata_filter:
            params["$filter"] = odata_filter
        if select:
            params["$select"] = ",".join(select)

        response = await self._client.request(
            method="GET",
            endpoint=self.ENDPOINT,
            division=division,
            params=params,
        )

        items, next_url = self._parse_list_response(response)
        return ListResult(items=items, next_url=next_url)

    async def list_next(
        self,
        next_url: str,
        division: int,
    ) -> ListResult[TModel]:
        """Continue pagination using the __next URL from a previous response.

        Args:
            next_url: The __next URL from ListResult.next_url.
            division: The division ID (for rate limiting).

        Returns:
            Next page of results with pagination info.
        """
        parsed = urlparse(next_url)
        path_parts = parsed.path.split("/api/v1/")
        if len(path_parts) > 1:
            remaining = path_parts[1]
            parts = remaining.split("/", 1)
            endpoint = "/" + parts[1] if len(parts) > 1 else ""
        else:
            endpoint = parsed.path

        params: dict[str, Any] = {}
        if parsed.query:
            for key, values in parse_qs(parsed.query).items():
                params[key] = values[0] if values else ""

        response = await self._client.request(
            method="GET",
            endpoint=endpoint,
            division=division,
            params=params,
        )

        items, new_next_url = self._parse_list_response(response)
        return ListResult(items=items, next_url=new_next_url)

    async def list_all(
        self,
        division: int,
        *,
        odata_filter: str | None = None,
        select: Sequence[str] | None = None,
    ) -> AsyncIterator[TModel]:
        """Iterate over all records, handling pagination automatically.

        This is a convenience method that yields items one by one,
        fetching additional pages as needed.

        Args:
            division: The division ID.
            odata_filter: OData filter expression (e.g., "Status eq 'Open'").
            select: List of fields to return.

        Yields:
            Individual Pydantic model instances.
        """
        result = await self.list(
            division=division,
            odata_filter=odata_filter,
            select=select,
        )

        for item in result.items:
            yield item

        while result.next_url:
            result = await self.list_next(result.next_url, division=division)
            for item in result.items:
                yield item

    async def get(self, division: int, id: str) -> TModel:
        """Get a single record by ID.

        Args:
            division: The division ID.
            id: The record's unique identifier (GUID).

        Returns:
            The Pydantic model instance.
        """
        endpoint = f"{self.ENDPOINT}(guid'{id}')"

        response = await self._client.request(
            method="GET",
            endpoint=endpoint,
            division=division,
        )

        data = response.get("d", response)
        return cast(TModel, self.MODEL.model_validate(data))

    async def create(self, division: int, data: dict[str, Any]) -> TModel:
        """Create a new record.

        Data can use either snake_case or PascalCase keys:
        - snake_case: {"warehouse_from": "guid", "description": "Test"}
        - PascalCase: {"WarehouseFrom": "guid", "Description": "Test"}

        Args:
            division: The division ID.
            data: The record data (snake_case auto-converted to PascalCase).

        Returns:
            The created Pydantic model instance.
        """
        api_data = self._prepare_data(data)

        response = await self._client.request(
            method="POST",
            endpoint=self.ENDPOINT,
            division=division,
            json=api_data,
        )

        result = response.get("d", response)
        return cast(TModel, self.MODEL.model_validate(result))

    async def update(self, division: int, id: str, data: dict[str, Any]) -> TModel:
        """Update an existing record.

        Data can use either snake_case or PascalCase keys:
        - snake_case: {"description": "Updated", "status": 50}
        - PascalCase: {"Description": "Updated", "Status": 50}

        Args:
            division: The division ID.
            id: The record's unique identifier (GUID).
            data: The fields to update (snake_case auto-converted to PascalCase).

        Returns:
            The updated Pydantic model instance.
        """
        endpoint = f"{self.ENDPOINT}(guid'{id}')"
        api_data = self._prepare_data(data)

        response = await self._client.request(
            method="PUT",
            endpoint=endpoint,
            division=division,
            json=api_data,
        )

        result = response.get("d", response)
        return cast(TModel, self.MODEL.model_validate(result))

    async def delete(self, division: int, id: str) -> None:
        """Delete a record.

        Args:
            division: The division ID.
            id: The record's unique identifier (GUID).
        """
        endpoint = f"{self.ENDPOINT}(guid'{id}')"

        await self._client.request(
            method="DELETE",
            endpoint=endpoint,
            division=division,
        )
