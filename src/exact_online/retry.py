"""Retry logic with exponential backoff for transient errors."""

import asyncio
import logging
import random
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field

import httpx

logger = logging.getLogger("exact_online.retry")

RETRYABLE_STATUS_CODES: tuple[int, ...] = (429, 500, 502, 503, 504)

RETRYABLE_EXCEPTIONS: tuple[type[Exception], ...] = (
    httpx.ConnectError,
    httpx.ConnectTimeout,
    httpx.ReadTimeout,
    httpx.WriteTimeout,
    httpx.PoolTimeout,
)


@dataclass
class RetryConfig:
    """Configuration for retry behavior.

    Attributes:
        max_retries: Maximum number of retry attempts (default: 3).
        base_delay: Initial delay in seconds before first retry (default: 1.0).
        max_delay: Maximum delay in seconds between retries (default: 60.0).
        exponential_base: Base for exponential backoff calculation (default: 2.0).
        jitter: Whether to add random jitter to delays (default: True).
        retry_on_status: HTTP status codes that trigger a retry.
    """

    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    retry_on_status: tuple[int, ...] = field(
        default_factory=lambda: RETRYABLE_STATUS_CODES
    )

    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay for a given retry attempt.

        Uses exponential backoff with optional jitter.

        Args:
            attempt: The retry attempt number (0-indexed).

        Returns:
            Delay in seconds before the next retry.
        """
        delay = self.base_delay * (self.exponential_base**attempt)
        delay = min(delay, self.max_delay)

        if self.jitter:
            delay = delay * (0.5 + random.random())

        return delay


class RetryableError(Exception):
    """Exception indicating a retryable error occurred.

    Attributes:
        status_code: HTTP status code if applicable.
        original_error: The original exception that triggered the retry.
    """

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        original_error: Exception | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.original_error = original_error


def is_retryable_status(status_code: int, config: RetryConfig) -> bool:
    """Check if a status code should trigger a retry.

    Args:
        status_code: The HTTP status code to check.
        config: Retry configuration with allowed status codes.

    Returns:
        True if the status code should trigger a retry.
    """
    return status_code in config.retry_on_status


def is_retryable_exception(exc: Exception) -> bool:
    """Check if an exception should trigger a retry.

    Args:
        exc: The exception to check.

    Returns:
        True if the exception should trigger a retry.
    """
    return isinstance(exc, RETRYABLE_EXCEPTIONS)


async def with_retry[T](
    func: Callable[[], Awaitable[T]],
    config: RetryConfig | None = None,
) -> T:
    """Execute an async function with retry logic.

    Retries on transient errors using exponential backoff with jitter.

    Args:
        func: Async function to execute.
        config: Retry configuration. Uses defaults if None.

    Returns:
        Result of the function call.

    Raises:
        The last exception if all retries are exhausted.

    Example:
        ```python
        result = await with_retry(
            lambda: client.request("GET", "/endpoint", division=123),
            config=RetryConfig(max_retries=5),
        )
        ```
    """
    if config is None:
        config = RetryConfig()

    last_exception: Exception | None = None

    for attempt in range(config.max_retries + 1):
        try:
            return await func()

        except Exception as exc:
            is_retryable = False
            status_code: int | None = None

            if isinstance(exc, RetryableError):
                is_retryable = True
                status_code = exc.status_code
            elif is_retryable_exception(exc):
                is_retryable = True

            if not is_retryable or attempt >= config.max_retries:
                raise

            last_exception = exc
            delay = config.calculate_delay(attempt)

            logger.warning(
                "Retryable error (attempt %d/%d, status=%s): %s. Retrying in %.2fs...",
                attempt + 1,
                config.max_retries,
                status_code,
                str(exc),
                delay,
            )

            await asyncio.sleep(delay)

    if last_exception:
        raise last_exception

    raise RuntimeError("Unexpected state in retry logic")
