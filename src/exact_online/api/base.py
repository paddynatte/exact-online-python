"""Base API resource class with CRUD and sync operations."""

from __future__ import annotations

from collections.abc import AsyncIterator, Sequence
from typing import TYPE_CHECKING, Any, ClassVar, cast
from urllib.parse import parse_qs, urlparse

from pydantic import BaseModel

from exact_online.models.base import ListResult, SyncResult

if TYPE_CHECKING:
    from exact_online.client import Client


class BaseAPI[TModel: BaseModel]:
    """Base class for API resources.

    Provides common CRUD operations and optional sync support.
    Subclasses define ENDPOINT, SYNC_ENDPOINT (optional), and MODEL.
    """

    ENDPOINT: ClassVar[str]
    SYNC_ENDPOINT: ClassVar[str | None] = None
    MODEL: ClassVar[type[BaseModel]]
    ID_FIELD: ClassVar[str] = "ID"

    def __init__(self, client: Client) -> None:
        """Initialize the API resource.

        Args:
            client: The Client instance.
        """
        self._client = client

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

        items = cast(
            list[TModel],
            [self.MODEL.model_validate(item) for item in results],
        )
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
            Individual model instances.
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
            The model instance.
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

        Args:
            division: The division ID.
            data: The record data (use API field names like "Supplier").

        Returns:
            The created model instance.
        """
        response = await self._client.request(
            method="POST",
            endpoint=self.ENDPOINT,
            division=division,
            json=data,
        )

        result = response.get("d", response)
        return cast(TModel, self.MODEL.model_validate(result))

    async def update(
        self, division: int, id: str, data: dict[str, Any]
    ) -> TModel:
        """Update an existing record.

        Args:
            division: The division ID.
            id: The record's unique identifier (GUID).
            data: The fields to update (use API field names).

        Returns:
            The updated model instance.
        """
        endpoint = f"{self.ENDPOINT}(guid'{id}')"

        response = await self._client.request(
            method="PUT",
            endpoint=endpoint,
            division=division,
            json=data,
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

    async def sync(
        self,
        division: int,
        *,
        timestamp: int = 0,
        odata_filter: str | None = None,
        select: Sequence[str] | None = None,
    ) -> SyncResult[TModel]:
        """Bulk sync using the Sync API endpoint.

        Returns up to 1000 records modified since the given timestamp.
        Use the returned timestamp for the next sync call.

        Args:
            division: The division ID.
            timestamp: Sync from this timestamp (0 = get all).
            odata_filter: Optional OData filter expression.
            select: Optional list of fields to return.

        Returns:
            SyncResult containing items, next timestamp, and has_more flag.

        Raises:
            NotImplementedError: If this entity doesn't support sync.
        """
        if self.SYNC_ENDPOINT is None:
            raise NotImplementedError(
                f"{self.__class__.__name__} does not support sync"
            )

        params: dict[str, Any] = {}

        if timestamp > 0:
            params["$filter"] = f"Timestamp gt {timestamp}"
            if odata_filter:
                params["$filter"] += f" and ({odata_filter})"
        elif odata_filter:
            params["$filter"] = odata_filter

        if select:
            params["$select"] = ",".join(select)

        response = await self._client.request(
            method="GET",
            endpoint=self.SYNC_ENDPOINT,
            division=division,
            params=params,
        )

        data = response.get("d", {})
        results = data if isinstance(data, list) else data.get("results", [])

        items = cast(
            list[TModel],
            [self.MODEL.model_validate(item) for item in results],
        )

        next_timestamp = timestamp
        for item in results:
            item_ts = item.get("Timestamp") or 0
            if isinstance(item_ts, str):
                try:
                    item_ts = int(item_ts)
                except ValueError:
                    item_ts = 0
            if item_ts > next_timestamp:
                next_timestamp = item_ts

        has_more = len(results) >= 1000

        return SyncResult(
            items=items,
            timestamp=next_timestamp,
            has_more=has_more,
        )
