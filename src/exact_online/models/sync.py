"""Models for Sync API and Deleted API."""

from datetime import datetime
from enum import IntEnum
from uuid import UUID

from pydantic import BaseModel, Field

from exact_online.models.base import ExactBaseModel, ODataDateTime


class EntityType(IntEnum):
    """Exact Online entity types for the Deleted API.

    Maps to the EntityType field returned by /sync/Deleted endpoint.
    Only includes entity types relevant to this SDK.
    """

    TRANSACTION_LINES = 1
    ACCOUNTS = 2
    ADDRESSES = 3
    ATTACHMENTS = 4
    CONTACTS = 5
    DOCUMENTS = 6
    GL_ACCOUNTS = 7
    ITEM_PRICES = 8
    ITEMS = 9
    PAYMENT_TERMS = 10
    SALES_INVOICES = 13
    TIME_COST_TRANSACTIONS = 14
    STOCK_POSITIONS = 15
    GOODS_DELIVERIES = 16
    GOODS_DELIVERY_LINES = 17
    GL_CLASSIFICATIONS = 18
    ITEM_WAREHOUSES = 19
    STORAGE_LOCATION_STOCK_POSITIONS = 20
    PROJECTS = 21
    PURCHASE_ORDERS = 22
    SUBSCRIPTIONS = 23
    SUBSCRIPTION_LINES = 24
    PROJECT_WBS = 25
    PROJECT_PLANNING = 26
    LEAVE_ABSENCE_HOURS_BY_DAY = 27
    SERIAL_BATCH_NUMBERS = 28
    STOCK_SERIAL_BATCH_NUMBERS = 29
    ITEM_ACCOUNTS = 30
    DISCOUNT_TABLES = 31
    SALES_ORDER_HEADERS = 32
    SALES_ORDER_LINES = 33
    QUOTATION_HEADERS = 34
    QUOTATION_LINES = 35
    SHOP_ORDERS = 36
    SHOP_ORDER_MATERIAL_PLANS = 37
    SHOP_ORDER_ROUTING_STEP_PLANS = 38
    SCHEDULES = 39
    SCHEDULE_ENTRIES = 40
    ITEM_STORAGE_LOCATIONS = 41
    EMPLOYEES = 42
    EMPLOYMENTS = 43
    EMPLOYMENT_CONTRACTS = 44
    EMPLOYMENT_ORGANIZATIONS = 45
    EMPLOYMENT_CLAS = 46
    EMPLOYMENT_SALARIES = 47
    BANK_ACCOUNTS = 48
    EMPLOYMENT_TAX_AUTHORITIES_GENERAL = 49
    SHOP_ORDER_PURCHASE_PLANNING = 50
    SHOP_ORDER_SUB_ORDERS = 51
    REQUIREMENT_ISSUES = 53
    BILL_OF_MATERIAL_MATERIALS = 54
    BILL_OF_MATERIAL_VERSIONS = 55
    LEAVE_REGISTRATIONS = 56
    LEAVE_BUILD_UP_REGISTRATIONS = 57
    ABSENCE_REGISTRATION_TRANSACTIONS = 58
    ABSENCE_REGISTRATIONS = 59


class SyncState(BaseModel):
    """Tracks sync progress for a resource.

    Stored via TokenStorage.get_sync_state() / save_sync_state().
    """

    timestamp: int = 1  # Row version for Sync API (start with 1)
    last_sync: datetime  # When the last sync completed


class DeletedRecord(ExactBaseModel):
    """A deleted record from the central /sync/Deleted endpoint.

    Note: Exact Online only keeps deleted records for 2 months.
    """

    id: UUID = Field(alias="ID")
    entity_key: UUID = Field(alias="EntityKey")  # The ID of the deleted record
    entity_type: int = Field(alias="EntityType")  # Maps to EntityType enum
    division: int = Field(alias="Division")
    deleted_by: UUID | None = Field(default=None, alias="DeletedBy")
    deleted_date: ODataDateTime = Field(default=None, alias="DeletedDate")
    timestamp: int = Field(alias="Timestamp")

    def get_entity_type(self) -> EntityType | None:
        """Get the EntityType enum value, or None if unknown."""
        try:
            return EntityType(self.entity_type)
        except ValueError:
            return None
