"""Exceptions for the Exact Online Python SDK."""


class BaseError(Exception):
    """Base exception for all SDK errors."""


class AuthenticationError(BaseError):
    """Authentication or authorization failure."""


class TokenExpiredError(AuthenticationError):
    """Refresh token expired - user must re-authenticate."""


class TokenRefreshError(AuthenticationError):
    """Token refresh failed."""


class RateLimitError(BaseError):
    """API rate limit exceeded."""


class APIError(BaseError):
    """General API error with status code and message."""

    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        super().__init__(f"[{status_code}] {message}")
