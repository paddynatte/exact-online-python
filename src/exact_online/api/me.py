"""Me (current user) API resource."""

from __future__ import annotations

from typing import TYPE_CHECKING

from exact_online.models.me import Me

if TYPE_CHECKING:
    from exact_online.client import Client


class MeAPI:
    """API resource for the current user.

    Provides access to user info and division list without requiring
    a division ID (unlike other endpoints).

    Usage:
        me = await client.me.current()
        print(f"Logged in as {me.full_name}")
        print(f"Current division: {me.current_division}")

        for div in me.user_divisions or []:
            print(f"  Division {div.division}: {div.description}")
    """

    def __init__(self, client: Client) -> None:
        """Initialize the API resource.

        Args:
            client: The Client instance.
        """
        self._client = client

    async def current(self) -> Me:
        """Get the current user's information.

        Returns:
            Me object containing user info and accessible divisions.
        """
        response = await self._client.request_without_division(
            method="GET",
            endpoint="/current/Me",
            params={"$expand": "UserDivisions"},
        )

        data = response.get("d", response)
        return Me.model_validate(data)
