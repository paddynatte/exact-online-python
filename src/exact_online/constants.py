"""Constants for the Exact Online Python SDK."""

from enum import StrEnum


class Region(StrEnum):
    """Exact Online regional endpoints."""

    NL = "nl"
    BE = "be"
    DE = "de"
    UK = "co.uk"
    US = "com"
    ES = "es"
    FR = "fr"

    @property
    def base_url(self) -> str:
        """Base URL for this region."""
        return f"https://start.exactonline.{self.value}"

    @property
    def api_url(self) -> str:
        """REST API base URL for this region."""
        return f"{self.base_url}/api/v1"

    @property
    def auth_url(self) -> str:
        """OAuth authorization endpoint for this region."""
        return f"{self.base_url}/api/oauth2/auth"

    @property
    def token_url(self) -> str:
        """OAuth token endpoint for this region."""
        return f"{self.base_url}/api/oauth2/token"
