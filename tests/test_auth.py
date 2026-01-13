"""Tests for OAuth authentication."""

import pytest
from pytest_httpx import HTTPXMock

from exact_online import OAuth, TokenData
from exact_online.exceptions import TokenExpiredError, TokenRefreshError

from .conftest import MockTokenStorage


@pytest.fixture
def oauth() -> OAuth:
    """OAuth with empty storage."""
    storage = MockTokenStorage()
    return OAuth(
        client_id="test_client_id",
        client_secret="test_client_secret",
        redirect_uri="https://example.com/callback",
        token_storage=storage,
    )


class TestGetToken:
    """Tests for get_token()."""

    async def test_no_tokens_raises_error(self, oauth: OAuth) -> None:
        """Should raise TokenExpiredError when no tokens exist."""
        with pytest.raises(TokenExpiredError, match="No tokens available"):
            await oauth.get_token()

    async def test_valid_token_returned(
        self, oauth: OAuth, valid_token_data: TokenData
    ) -> None:
        """Should return access token when valid."""
        storage = oauth.token_storage
        assert isinstance(storage, MockTokenStorage)
        storage.tokens = valid_token_data

        token = await oauth.get_token()

        assert token == "valid_access_token"

    async def test_expiring_token_refreshed(
        self,
        oauth: OAuth,
        expiring_token_data: TokenData,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Should refresh token when close to expiry."""
        storage = oauth.token_storage
        assert isinstance(storage, MockTokenStorage)
        storage.tokens = expiring_token_data
        httpx_mock.add_response(
            json={
                "access_token": "new_access_token",
                "refresh_token": "new_refresh_token",
                "expires_in": 600,
            }
        )

        token = await oauth.get_token()

        assert token == "new_access_token"
        assert storage.save_count == 1


class TestExchange:
    """Tests for exchange()."""

    async def test_successful_exchange(
        self, oauth: OAuth, httpx_mock: HTTPXMock
    ) -> None:
        """Should exchange code for tokens."""
        httpx_mock.add_response(
            json={
                "access_token": "new_access_token",
                "refresh_token": "new_refresh_token",
                "expires_in": 600,
            }
        )

        tokens = await oauth.exchange("auth_code_123")

        assert tokens.access_token == "new_access_token"
        assert tokens.refresh_token == "new_refresh_token"
        storage = oauth.token_storage
        assert isinstance(storage, MockTokenStorage)
        assert storage.save_count == 1

    async def test_failed_exchange(
        self, oauth: OAuth, httpx_mock: HTTPXMock
    ) -> None:
        """Should raise TokenRefreshError on failure."""
        httpx_mock.add_response(status_code=400, json={"error": "invalid_grant"})

        with pytest.raises(TokenRefreshError):
            await oauth.exchange("bad_code")


class TestTokenRefresh:
    """Tests for token refresh behavior."""

    async def test_refresh_saves_new_tokens(
        self,
        oauth: OAuth,
        expiring_token_data: TokenData,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Refresh should save new tokens immediately (token rotation)."""
        storage = oauth.token_storage
        assert isinstance(storage, MockTokenStorage)
        storage.tokens = expiring_token_data
        httpx_mock.add_response(
            json={
                "access_token": "rotated_access",
                "refresh_token": "rotated_refresh",
                "expires_in": 600,
            }
        )

        await oauth.get_token()

        saved_tokens = storage.tokens
        assert saved_tokens is not None
        assert saved_tokens.refresh_token == "rotated_refresh"

    async def test_expired_refresh_token(
        self,
        oauth: OAuth,
        expiring_token_data: TokenData,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Should raise TokenExpiredError when refresh token is invalid."""
        storage = oauth.token_storage
        assert isinstance(storage, MockTokenStorage)
        storage.tokens = expiring_token_data
        httpx_mock.add_response(status_code=400, json={"error": "invalid_grant"})

        with pytest.raises(TokenExpiredError, match="re-authenticate"):
            await oauth.get_token()
