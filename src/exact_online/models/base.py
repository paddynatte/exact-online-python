"""Base models and utilities for Exact Online API."""

import re
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Annotated, Any

from pydantic import BaseModel, BeforeValidator, ConfigDict


def parse_odata_datetime(value: Any) -> Any:
    """Parse OData datetime format /Date(milliseconds)/ to datetime.
    
    Exact Online returns dates in OData format like /Date(1704412800000)/
    which is milliseconds since Unix epoch.
    """
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        # Match /Date(1234567890000)/ format
        match = re.match(r"/Date\((\d+)\)/", value)
        if match:
            milliseconds = int(match.group(1))
            return datetime.fromtimestamp(milliseconds / 1000, tz=UTC)
        # Try standard ISO format as fallback
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            pass
    return value


# Custom datetime type that handles OData format
ODataDateTime = Annotated[datetime | None, BeforeValidator(parse_odata_datetime)]


class ExactBaseModel(BaseModel):
    """Base model with common configuration for all Exact Online entities."""

    model_config = ConfigDict(
        populate_by_name=True,  # Allow both alias and field name
        extra="ignore",  # Ignore unknown fields from API
    )


@dataclass
class ListResult[TModel]:
    """Result from a list operation with pagination support.

    Iterable for convenience - can be used directly in for loops.
    Access .next_url to continue pagination with list_next().

    Attributes:
        items: List of records returned from the request.
        next_url: URL to fetch the next page, or None if no more pages.
    """

    items: list[TModel]
    next_url: str | None

    @property
    def has_more(self) -> bool:
        """Check if there are more pages to fetch."""
        return self.next_url is not None

    def __iter__(self) -> Iterator[TModel]:
        """Iterate over the items directly."""
        return iter(self.items)

    def __len__(self) -> int:
        """Return the number of items in this page."""
        return len(self.items)

    def __repr__(self) -> str:
        """Return a readable representation."""
        return f"ListResult(items={len(self.items)}, has_more={self.has_more})"


@dataclass
class SyncResult[TModel]:
    """Result from a sync operation.

    Attributes:
        items: List of records returned from the sync.
        timestamp: The timestamp to use for the next sync call.
        has_more: True if there are more records to fetch.
    """

    items: list[TModel]
    timestamp: int
    has_more: bool

    def __repr__(self) -> str:
        """Return a readable representation."""
        return (
            f"SyncResult(items={len(self.items)}, "
            f"timestamp={self.timestamp}, has_more={self.has_more})"
        )
