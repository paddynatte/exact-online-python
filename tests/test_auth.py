"""Tests for OAuth authentication."""

import pytest
from pytest_httpx import HTTPXMock

from exact_online import ExactRegion, OAuthManager, TokenData
from exact_online.exceptions import TokenExpiredError, TokenRefreshError

from .conftest import MockTokenStorage


@pytest.fixture
def oauth_manager(region: ExactRegion) -> OAuthManager:
    """OAuthManager with empty storage."""
    storage = MockTokenStorage()
    return OAuthManager(
        client_id="test_client_id",
        client_secret="test_client_secret",
        redirect_uri="https://example.com/callback",
        region=region,
        token_storage=storage,
    )


class TestGetAuthorizationUrl:
    """Tests for get_authorization_url()."""

    def test_basic_url(self, oauth_manager: OAuthManager) -> None:
        """Should generate correct authorization URL."""
        url = oauth_manager.get_authorization_url()

        assert url.startswith("https://start.exactonline.nl/api/oauth2/auth?")
        assert "client_id=test_client_id" in url
        assert "response_type=code" in url

    def test_with_state(self, oauth_manager: OAuthManager) -> None:
        """Should include state parameter."""
        url = oauth_manager.get_authorization_url(state="csrf-token")

        assert "state=csrf-token" in url


class TestEnsureValidToken:
    """Tests for ensure_valid_token()."""

    async def test_no_tokens_raises_error(self, oauth_manager: OAuthManager) -> None:
        """Should raise TokenExpiredError when no tokens exist."""
        with pytest.raises(TokenExpiredError, match="No tokens available"):
            await oauth_manager.ensure_valid_token()

    async def test_valid_token_returned(
        self, oauth_manager: OAuthManager, valid_token_data: TokenData
    ) -> None:
        """Should return access token when valid."""
        storage = oauth_manager.token_storage
        assert isinstance(storage, MockTokenStorage)
        storage.tokens = valid_token_data

        token = await oauth_manager.ensure_valid_token()

        assert token == "valid_access_token"

    async def test_expiring_token_refreshed(
        self,
        oauth_manager: OAuthManager,
        expiring_token_data: TokenData,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Should refresh token when close to expiry."""
        storage = oauth_manager.token_storage
        assert isinstance(storage, MockTokenStorage)
        storage.tokens = expiring_token_data
        httpx_mock.add_response(
            json={
                "access_token": "new_access_token",
                "refresh_token": "new_refresh_token",
                "expires_in": 600,
            }
        )

        token = await oauth_manager.ensure_valid_token()

        assert token == "new_access_token"
        assert storage.save_count == 1


class TestExchangeCode:
    """Tests for exchange_code()."""

    async def test_successful_exchange(
        self, oauth_manager: OAuthManager, httpx_mock: HTTPXMock
    ) -> None:
        """Should exchange code for tokens."""
        httpx_mock.add_response(
            json={
                "access_token": "new_access_token",
                "refresh_token": "new_refresh_token",
                "expires_in": 600,
            }
        )

        tokens = await oauth_manager.exchange_code("auth_code_123")

        assert tokens.access_token == "new_access_token"
        assert tokens.refresh_token == "new_refresh_token"
        storage = oauth_manager.token_storage
        assert isinstance(storage, MockTokenStorage)
        assert storage.save_count == 1

    async def test_failed_exchange(
        self, oauth_manager: OAuthManager, httpx_mock: HTTPXMock
    ) -> None:
        """Should raise TokenRefreshError on failure."""
        httpx_mock.add_response(status_code=400, json={"error": "invalid_grant"})

        with pytest.raises(TokenRefreshError):
            await oauth_manager.exchange_code("bad_code")


class TestTokenRefresh:
    """Tests for token refresh behavior."""

    async def test_refresh_saves_new_tokens(
        self,
        oauth_manager: OAuthManager,
        expiring_token_data: TokenData,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Refresh should save new tokens immediately (token rotation)."""
        storage = oauth_manager.token_storage
        assert isinstance(storage, MockTokenStorage)
        storage.tokens = expiring_token_data
        httpx_mock.add_response(
            json={
                "access_token": "rotated_access",
                "refresh_token": "rotated_refresh",
                "expires_in": 600,
            }
        )

        await oauth_manager.ensure_valid_token()

        # Verify new refresh token was saved
        saved_tokens = storage.tokens
        assert saved_tokens is not None
        assert saved_tokens.refresh_token == "rotated_refresh"

    async def test_expired_refresh_token(
        self,
        oauth_manager: OAuthManager,
        expiring_token_data: TokenData,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Should raise TokenExpiredError when refresh token is invalid."""
        storage = oauth_manager.token_storage
        assert isinstance(storage, MockTokenStorage)
        storage.tokens = expiring_token_data
        httpx_mock.add_response(status_code=400, json={"error": "invalid_grant"})

        with pytest.raises(TokenExpiredError, match="re-authenticate"):
            await oauth_manager.ensure_valid_token()
