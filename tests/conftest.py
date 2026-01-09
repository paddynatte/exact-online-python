"""Pytest configuration and fixtures."""

from datetime import UTC, datetime, timedelta

import pytest

from exact_online import ExactRegion, TokenData


@pytest.fixture
def region() -> ExactRegion:
    """Default region for tests."""
    return ExactRegion.NL


@pytest.fixture
def valid_token_data() -> TokenData:
    """Token data that is not expired."""
    return TokenData(
        access_token="valid_access_token",
        refresh_token="valid_refresh_token",
        token_type="Bearer",
        expires_at=datetime.now(UTC) + timedelta(hours=1),
    )


@pytest.fixture
def expiring_token_data() -> TokenData:
    """Token data that should be refreshed (within buffer)."""
    return TokenData(
        access_token="expiring_access_token",
        refresh_token="expiring_refresh_token",
        token_type="Bearer",
        expires_at=datetime.now(UTC) + timedelta(seconds=10),
    )


@pytest.fixture
def expired_token_data() -> TokenData:
    """Token data that is already expired."""
    return TokenData(
        access_token="expired_access_token",
        refresh_token="expired_refresh_token",
        token_type="Bearer",
        expires_at=datetime.now(UTC) - timedelta(minutes=5),
    )


class MockTokenStorage:
    """In-memory token storage for testing."""

    def __init__(self, initial_tokens: TokenData | None = None) -> None:
        self.tokens = initial_tokens
        self.save_count = 0

    async def get_tokens(self) -> TokenData | None:
        return self.tokens

    async def save_tokens(self, tokens: TokenData) -> None:
        self.tokens = tokens
        self.save_count += 1


@pytest.fixture
def mock_token_storage() -> MockTokenStorage:
    """Empty mock token storage."""
    return MockTokenStorage()


@pytest.fixture
def mock_token_storage_with_tokens(valid_token_data: TokenData) -> MockTokenStorage:
    """Mock token storage pre-populated with valid tokens."""
    return MockTokenStorage(initial_tokens=valid_token_data)
