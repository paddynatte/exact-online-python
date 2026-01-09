"""Exceptions for the Exact Online Python SDK."""


class ExactOnlineError(Exception):
    """Base exception for all SDK errors."""


class AuthenticationError(ExactOnlineError):
    """Authentication or authorization failure."""


class TokenExpiredError(AuthenticationError):
    """Refresh token expired - user must re-authenticate."""


class TokenRefreshError(AuthenticationError):
    """Token refresh failed."""


class RateLimitError(ExactOnlineError):
    """API rate limit exceeded."""


class APIError(ExactOnlineError):
    """General API error with status code and message."""

    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        super().__init__(f"[{status_code}] {message}")
