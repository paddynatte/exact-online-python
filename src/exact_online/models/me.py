"""Pydantic models for Me (current user) endpoint."""

from uuid import UUID

from pydantic import Field

from exact_online.models.base import ExactBaseModel


class UserDivision(ExactBaseModel):
    """A division accessible by the current user."""

    code: int = Field(alias="Code")
    customer: UUID | None = Field(default=None, alias="Customer")
    description: str | None = Field(default=None, alias="Description")
    division: int = Field(alias="Division")
    hid: int | None = Field(default=None, alias="HID")


class Me(ExactBaseModel):
    """Current user information from /current/Me endpoint."""

    user_id: UUID = Field(alias="UserID")
    user_name: str | None = Field(default=None, alias="UserName")
    full_name: str | None = Field(default=None, alias="FullName")
    email: str | None = Field(default=None, alias="Email")
    picture_url: str | None = Field(default=None, alias="PictureUrl")
    language_code: str | None = Field(default=None, alias="LanguageCode")
    current_division: int = Field(alias="CurrentDivision")
    division_customer: UUID | None = Field(default=None, alias="DivisionCustomer")
    division_customer_code: str | None = Field(
        default=None, alias="DivisionCustomerCode"
    )
    division_customer_name: str | None = Field(
        default=None, alias="DivisionCustomerName"
    )
    user_divisions: list[UserDivision] | None = Field(
        default=None, alias="UserDivisions"
    )

    def __repr__(self) -> str:
        """Return a readable representation."""
        return f"Me(user={self.full_name!r}, division={self.current_division})"
