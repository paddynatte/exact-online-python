"""Tests for retry logic."""

import pytest

from exact_online.retry import (
    RetryableError,
    RetryConfig,
    is_retryable_exception,
    is_retryable_status,
    with_retry,
)


class TestRetryConfig:
    """Tests for RetryConfig."""

    def test_default_values(self) -> None:
        """Should have sensible defaults."""
        config = RetryConfig()

        assert config.max_retries == 3
        assert config.base_delay == 1.0
        assert config.max_delay == 60.0
        assert config.exponential_base == 2.0
        assert config.jitter is True
        assert 429 in config.retry_on_status
        assert 500 in config.retry_on_status

    def test_calculate_delay_exponential(self) -> None:
        """Should calculate exponential backoff delays."""
        config = RetryConfig(base_delay=1.0, exponential_base=2.0, jitter=False)

        assert config.calculate_delay(0) == 1.0
        assert config.calculate_delay(1) == 2.0
        assert config.calculate_delay(2) == 4.0
        assert config.calculate_delay(3) == 8.0

    def test_calculate_delay_max_cap(self) -> None:
        """Should cap delay at max_delay."""
        config = RetryConfig(base_delay=1.0, max_delay=5.0, jitter=False)

        assert config.calculate_delay(10) == 5.0

    def test_calculate_delay_with_jitter(self) -> None:
        """Should add jitter to delay."""
        config = RetryConfig(base_delay=10.0, jitter=True)

        delays = [config.calculate_delay(0) for _ in range(10)]
        assert len(set(delays)) > 1


class TestIsRetryableStatus:
    """Tests for is_retryable_status."""

    def test_429_is_retryable(self) -> None:
        """429 Too Many Requests should be retryable."""
        config = RetryConfig()
        assert is_retryable_status(429, config) is True

    def test_500_is_retryable(self) -> None:
        """500 Internal Server Error should be retryable."""
        config = RetryConfig()
        assert is_retryable_status(500, config) is True

    def test_400_not_retryable(self) -> None:
        """400 Bad Request should not be retryable."""
        config = RetryConfig()
        assert is_retryable_status(400, config) is False

    def test_custom_status_codes(self) -> None:
        """Should respect custom retry status codes."""
        config = RetryConfig(retry_on_status=(418,))
        assert is_retryable_status(418, config) is True
        assert is_retryable_status(429, config) is False


class TestIsRetryableException:
    """Tests for is_retryable_exception."""

    def test_retryable_error_is_retryable(self) -> None:
        """RetryableError should be retryable."""
        exc = RetryableError("test")
        assert is_retryable_exception(exc) is False

    def test_value_error_not_retryable(self) -> None:
        """ValueError should not be retryable."""
        exc = ValueError("test")
        assert is_retryable_exception(exc) is False


class TestWithRetry:
    """Tests for with_retry function."""

    async def test_success_no_retry(self) -> None:
        """Should return result on success without retry."""
        call_count = 0

        async def func() -> str:
            nonlocal call_count
            call_count += 1
            return "success"

        result = await with_retry(func, RetryConfig())

        assert result == "success"
        assert call_count == 1

    async def test_retry_on_retryable_error(self) -> None:
        """Should retry on RetryableError."""
        call_count = 0

        async def func() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise RetryableError("transient error", status_code=500)
            return "success"

        config = RetryConfig(max_retries=3, base_delay=0.01, jitter=False)
        result = await with_retry(func, config)

        assert result == "success"
        assert call_count == 3

    async def test_max_retries_exhausted(self) -> None:
        """Should raise after max retries exhausted."""
        call_count = 0

        async def func() -> str:
            nonlocal call_count
            call_count += 1
            raise RetryableError("always fails", status_code=500)

        config = RetryConfig(max_retries=2, base_delay=0.01, jitter=False)

        with pytest.raises(RetryableError, match="always fails"):
            await with_retry(func, config)

        assert call_count == 3

    async def test_non_retryable_error_not_retried(self) -> None:
        """Should not retry on non-retryable errors."""
        call_count = 0

        async def func() -> str:
            nonlocal call_count
            call_count += 1
            raise ValueError("not retryable")

        config = RetryConfig(max_retries=3, base_delay=0.01)

        with pytest.raises(ValueError, match="not retryable"):
            await with_retry(func, config)

        assert call_count == 1

    async def test_default_config(self) -> None:
        """Should use default config when None is passed."""
        async def func() -> str:
            return "success"

        result = await with_retry(func, None)
        assert result == "success"


class TestRetryableError:
    """Tests for RetryableError."""

    def test_with_status_code(self) -> None:
        """Should store status code."""
        error = RetryableError("test", status_code=429)

        assert error.status_code == 429
        assert str(error) == "test"

    def test_with_original_error(self) -> None:
        """Should store original error."""
        original = ValueError("original")
        error = RetryableError("wrapped", original_error=original)

        assert error.original_error is original
