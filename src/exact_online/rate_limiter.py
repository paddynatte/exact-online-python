"""Rate limiter for Exact Online API requests."""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime

logger = logging.getLogger("exact_online.rate_limiter")


@dataclass
class RateLimitInfo:
    """Rate limit information for a division."""

    limit: int = 60
    remaining: int = 60
    reset_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __repr__(self) -> str:
        """Return a readable representation."""
        return f"RateLimitInfo(remaining={self.remaining}/{self.limit})"


class RateLimiter:
    """Tracks and enforces rate limits per division.

    Exact Online rate limits:
    - 60 requests per minute per division
    - Headers: X-RateLimit-Minutely-Limit, X-RateLimit-Minutely-Remaining,
      X-RateLimit-Minutely-Reset
    """

    WAIT_THRESHOLD = 5

    def __init__(self) -> None:
        self._limits: dict[int, RateLimitInfo] = {}
        self._lock = asyncio.Lock()

    def _get_info(self, division: int) -> RateLimitInfo:
        """Get or create rate limit info for a division."""
        if division not in self._limits:
            self._limits[division] = RateLimitInfo()
        return self._limits[division]

    async def check_and_wait(self, division: int) -> None:
        """Wait if we're close to hitting the rate limit.

        Args:
            division: The division ID to check limits for.
        """
        async with self._lock:
            info = self._get_info(division)

            if info.remaining <= self.WAIT_THRESHOLD:
                now = datetime.now(UTC)
                if info.reset_at > now:
                    wait_seconds = (info.reset_at - now).total_seconds()
                    if wait_seconds > 0:
                        logger.debug(
                            "Rate limit approaching for division %d, waiting %.1fs",
                            division,
                            wait_seconds,
                        )
                        await asyncio.sleep(wait_seconds)
                        info.remaining = info.limit

    def update_from_headers(self, division: int, headers: dict[str, str]) -> None:
        """Update rate limit info from response headers.

        Args:
            division: The division ID.
            headers: Response headers from Exact Online API.
        """
        info = self._get_info(division)
        lower_headers = {k.lower(): v for k, v in headers.items()}

        if "x-ratelimit-minutely-limit" in lower_headers:
            info.limit = int(lower_headers["x-ratelimit-minutely-limit"])

        if "x-ratelimit-minutely-remaining" in lower_headers:
            info.remaining = int(lower_headers["x-ratelimit-minutely-remaining"])

        if "x-ratelimit-minutely-reset" in lower_headers:
            reset_timestamp = int(lower_headers["x-ratelimit-minutely-reset"])
            if reset_timestamp > 10**12:
                reset_timestamp = reset_timestamp // 1000
            info.reset_at = datetime.fromtimestamp(reset_timestamp, tz=UTC)

    def get_remaining(self, division: int) -> int:
        """Get remaining requests for a division.

        Args:
            division: The division ID.

        Returns:
            Number of remaining requests.
        """
        return self._get_info(division).remaining
