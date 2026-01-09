"""Authentication module for the Exact Online Python SDK."""

import asyncio
import logging
from datetime import UTC, datetime, timedelta
from types import TracebackType
from typing import Any, Protocol
from urllib.parse import urlencode

import httpx
from pydantic import BaseModel

from exact_online.constants import ExactRegion
from exact_online.exceptions import (
    TokenExpiredError,
    TokenRefreshError,
)

logger = logging.getLogger("exact_online.auth")

_REFRESH_BUFFER_SECONDS = 30


class TokenData(BaseModel):
    """OAuth token data."""

    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_at: datetime

    @property
    def is_expired(self) -> bool:
        """Check if the access token is expired."""
        return datetime.now(UTC) >= self.expires_at

    @property
    def should_refresh(self) -> bool:
        """Check if the access token should be refreshed (within buffer time)."""
        buffer = timedelta(seconds=_REFRESH_BUFFER_SECONDS)
        return datetime.now(UTC) >= (self.expires_at - buffer)

    def __repr__(self) -> str:
        """Return a readable representation showing expiry status."""
        status = "expired" if self.is_expired else "valid"
        return f"TokenData({status}, expires_at={self.expires_at.isoformat()})"

    @classmethod
    def from_response(cls, response_data: dict[str, Any]) -> "TokenData":
        """Create TokenData from an OAuth token response.

        Args:
            response_data: The JSON response from the token endpoint.

        Returns:
            TokenData instance with calculated expiry time.
        """
        expires_in = int(response_data.get("expires_in", 600))
        expires_at = datetime.now(UTC) + timedelta(seconds=expires_in)

        return cls(
            access_token=response_data["access_token"],
            refresh_token=response_data["refresh_token"],
            token_type=response_data.get("token_type", "Bearer"),
            expires_at=expires_at,
        )


class TokenStorage(Protocol):
    """Protocol for token storage implementations.

    Users must implement this protocol to persist tokens.
    This is critical because Exact Online rotates refresh tokens
    on every refresh - if you don't persist the new token, you lose access.

    Example:
        class MyTokenStorage:
            async def get_tokens(self) -> TokenData | None:
                # Load from your database
                ...

            async def save_tokens(self, tokens: TokenData) -> None:
                # Save to your database
                ...
    """

    async def get_tokens(self) -> TokenData | None:
        """Retrieve the current tokens."""
        ...

    async def save_tokens(self, tokens: TokenData) -> None:
        """Persist tokens after refresh or initial exchange."""
        ...


class OAuthManager:
    """Manages OAuth authentication for Exact Online.

    Handles:
    - Authorization URL generation
    - Code exchange for tokens
    - Automatic token refresh with rotation handling
    - Thread-safe refresh with async lock
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        region: ExactRegion,
        token_storage: TokenStorage,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        """Initialize the OAuth manager.

        Args:
            client_id: Your Exact Online app client ID.
            client_secret: Your Exact Online app client secret.
            redirect_uri: The redirect URI registered with your app.
            region: The Exact Online region to use.
            token_storage: Implementation of TokenStorage for persisting tokens.
            http_client: Optional httpx client (created if not provided).
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.region = region
        self.token_storage = token_storage

        self._http_client = http_client
        self._owns_http_client = http_client is None
        self._refresh_lock = asyncio.Lock()

    async def _get_http_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(timeout=30.0)
        return self._http_client

    def get_authorization_url(
        self,
        state: str | None = None,
        scope: str | None = None,
    ) -> str:
        """Generate the OAuth authorization URL.

        Args:
            state: Optional state parameter for CSRF protection.
            scope: Optional scope (not typically used by Exact Online).

        Returns:
            The full authorization URL to redirect the user to.
        """
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
        }

        if state:
            params["state"] = state
        if scope:
            params["scope"] = scope

        return f"{self.region.auth_url}?{urlencode(params)}"

    async def exchange_code(self, code: str) -> TokenData:
        """Exchange an authorization code for tokens.

        This is called after the user authorizes your app and is redirected
        back with an authorization code.

        Args:
            code: The authorization code from the callback.

        Returns:
            TokenData containing access and refresh tokens.

        Raises:
            TokenRefreshError: If the code exchange fails.
        """
        http = await self._get_http_client()

        try:
            response = await http.post(
                self.region.token_url,
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": self.redirect_uri,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise TokenRefreshError(
                f"Failed to exchange code: {e.response.status_code}"
            ) from e

        tokens = TokenData.from_response(response.json())
        await self.token_storage.save_tokens(tokens)
        logger.debug("Successfully exchanged authorization code for tokens")
        return tokens

    async def ensure_valid_token(self) -> str:
        """Ensure we have a valid access token, refreshing if needed.

        This method is thread-safe and handles concurrent refresh attempts.

        Returns:
            A valid access token.

        Raises:
            TokenExpiredError: If no tokens exist or refresh token is invalid.
            TokenRefreshError: If token refresh fails.
        """
        tokens = await self.token_storage.get_tokens()

        if tokens is None:
            raise TokenExpiredError("No tokens available - user must authenticate")

        if not tokens.should_refresh:
            return tokens.access_token

        async with self._refresh_lock:
            tokens = await self.token_storage.get_tokens()
            if tokens is None:
                raise TokenExpiredError("No tokens available - user must authenticate")

            if not tokens.should_refresh:
                return tokens.access_token

            tokens = await self._refresh(tokens)
            return tokens.access_token

    async def _refresh(self, current_tokens: TokenData) -> TokenData:
        """Refresh the access token.

        IMPORTANT: Exact Online rotates refresh tokens on every refresh.
        The new tokens are immediately saved via token_storage.

        Args:
            current_tokens: The current tokens containing the refresh token.

        Returns:
            New TokenData with fresh access and refresh tokens.

        Raises:
            TokenExpiredError: If the refresh token has expired.
            TokenRefreshError: If the refresh request fails.
        """
        http = await self._get_http_client()

        try:
            response = await http.post(
                self.region.token_url,
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": current_tokens.refresh_token,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 400:
                raise TokenExpiredError(
                    "Refresh token expired - user must re-authenticate"
                ) from e
            raise TokenRefreshError(
                f"Failed to refresh token: {e.response.status_code}"
            ) from e

        new_tokens = TokenData.from_response(response.json())
        await self.token_storage.save_tokens(new_tokens)
        logger.debug("Successfully refreshed access token")

        return new_tokens

    async def close(self) -> None:
        """Close the HTTP client if we own it."""
        if self._owns_http_client and self._http_client is not None:
            await self._http_client.aclose()
            self._http_client = None

    async def __aenter__(self) -> "OAuthManager":
        """Async context manager entry."""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Async context manager exit."""
        await self.close()
