"""Tests for Sync API functionality."""

from datetime import UTC, datetime

import pytest
from pytest_httpx import HTTPXMock

from exact_online import (
    Client,
    EntityType,
    OAuth,
    SyncState,
    TokenData,
)

from .conftest import MockTokenStorage


@pytest.fixture
def oauth_with_sync(valid_token_data: TokenData) -> OAuth:
    """OAuth with valid tokens and sync state support."""
    storage = MockTokenStorage(initial_tokens=valid_token_data)
    return OAuth(
        client_id="test_client_id",
        client_secret="test_client_secret",
        redirect_uri="https://example.com/callback",
        token_storage=storage,
    )


@pytest.fixture
async def client_with_sync(oauth_with_sync: OAuth) -> Client:  # type: ignore[misc]
    """Client for sync testing."""
    async with Client(oauth=oauth_with_sync) as c:
        yield c


class TestSyncWithSyncAPI:
    """Tests for sync() using Sync API (PurchaseOrders, SalesOrders, ShopOrders)."""

    async def test_sync_first_time_uses_timestamp_1(
        self, client_with_sync: Client, httpx_mock: HTTPXMock
    ) -> None:
        """First sync should use Timestamp gt 1."""
        httpx_mock.add_response(
            json={
                "d": {
                    "results": [
                        {
                            "PurchaseOrderID": "11111111-1111-1111-1111-111111111111",
                            "Supplier": "00000000-0000-0000-0000-000000000001",
                            "Timestamp": 12345,
                        }
                    ],
                    "__next": None,
                }
            },
        )

        items = []
        async for item in client_with_sync.purchase_orders.sync(division=123):
            items.append(item)

        assert len(items) == 1

        # Verify the request used Sync API endpoint and Timestamp gt 1
        request = httpx_mock.get_request()
        assert request is not None
        assert "/sync/PurchaseOrder/PurchaseOrders" in str(request.url)
        assert "Timestamp%20gt%201" in str(request.url)

    async def test_sync_subsequent_uses_stored_timestamp(
        self, oauth_with_sync: OAuth, httpx_mock: HTTPXMock
    ) -> None:
        """Subsequent sync should use stored timestamp."""
        # Pre-populate sync state
        storage = oauth_with_sync.token_storage
        await storage.save_sync_state(
            division=123,
            resource="purchase_orders",
            state=SyncState(timestamp=50000, last_sync=datetime.now(UTC)),
        )

        httpx_mock.add_response(
            json={
                "d": {
                    "results": [
                        {
                            "PurchaseOrderID": "22222222-2222-2222-2222-222222222222",
                            "Supplier": "00000000-0000-0000-0000-000000000001",
                            "Timestamp": 60000,
                        }
                    ],
                    "__next": None,
                }
            },
        )

        async with Client(oauth=oauth_with_sync) as client:
            items = []
            async for item in client.purchase_orders.sync(division=123):
                items.append(item)

        # Verify the request used stored timestamp
        request = httpx_mock.get_request()
        assert request is not None
        assert "Timestamp%20gt%2050000" in str(request.url)

    async def test_sync_saves_highest_timestamp(
        self, client_with_sync: Client, httpx_mock: HTTPXMock
    ) -> None:
        """Sync should save the highest timestamp after completion."""
        httpx_mock.add_response(
            json={
                "d": {
                    "results": [
                        {
                            "PurchaseOrderID": "11111111-1111-1111-1111-111111111111",
                            "Supplier": "00000000-0000-0000-0000-000000000001",
                            "Timestamp": 100,
                        },
                        {
                            "PurchaseOrderID": "22222222-2222-2222-2222-222222222222",
                            "Supplier": "00000000-0000-0000-0000-000000000001",
                            "Timestamp": 500,
                        },
                        {
                            "PurchaseOrderID": "33333333-3333-3333-3333-333333333333",
                            "Supplier": "00000000-0000-0000-0000-000000000001",
                            "Timestamp": 300,
                        },
                    ],
                    "__next": None,
                }
            },
        )

        items = []
        async for item in client_with_sync.purchase_orders.sync(division=123):
            items.append(item)

        # Verify state was saved with highest timestamp
        storage = client_with_sync.oauth.token_storage
        state = await storage.get_sync_state(123, "purchase_orders")
        assert state is not None
        assert state.timestamp == 500

    async def test_sync_pagination(
        self, client_with_sync: Client, httpx_mock: HTTPXMock
    ) -> None:
        """Sync should handle pagination across multiple pages."""
        next_url = "https://start.exactonline.nl/api/v1/123/sync/PurchaseOrder/PurchaseOrders?$skiptoken=abc"

        # First page
        httpx_mock.add_response(
            json={
                "d": {
                    "results": [
                        {
                            "PurchaseOrderID": "11111111-1111-1111-1111-111111111111",
                            "Supplier": "00000000-0000-0000-0000-000000000001",
                            "Timestamp": 100,
                        }
                    ],
                    "__next": next_url,
                }
            },
        )

        # Second page
        httpx_mock.add_response(
            json={
                "d": {
                    "results": [
                        {
                            "PurchaseOrderID": "22222222-2222-2222-2222-222222222222",
                            "Supplier": "00000000-0000-0000-0000-000000000001",
                            "Timestamp": 200,
                        }
                    ],
                    "__next": None,
                }
            },
        )

        items = []
        async for item in client_with_sync.purchase_orders.sync(division=123):
            items.append(item)

        assert len(items) == 2
        assert len(httpx_mock.get_requests()) == 2


class TestSyncWithModifiedFilter:
    """Tests for sync() using Modified filter fallback (WarehouseTransfers, etc.)."""

    async def test_sync_first_time_gets_all(
        self, client_with_sync: Client, httpx_mock: HTTPXMock
    ) -> None:
        """First sync without state should get all records."""
        httpx_mock.add_response(
            json={
                "d": {
                    "results": [
                        {
                            "TransferID": "11111111-1111-1111-1111-111111111111",
                            "WarehouseFrom": "00000000-0000-0000-0000-000000000001",
                            "WarehouseTo": "00000000-0000-0000-0000-000000000002",
                        }
                    ],
                    "__next": None,
                }
            },
        )

        items = []
        async for item in client_with_sync.warehouse_transfers.sync(division=123):
            items.append(item)

        assert len(items) == 1

        # Verify the request used regular endpoint (not sync endpoint)
        request = httpx_mock.get_request()
        assert request is not None
        assert "/inventory/WarehouseTransfers" in str(request.url)
        # No Modified filter on first sync
        assert "Modified" not in str(request.url)

    async def test_sync_subsequent_uses_modified_filter(
        self, oauth_with_sync: OAuth, httpx_mock: HTTPXMock
    ) -> None:
        """Subsequent sync should use Modified filter."""
        # Pre-populate sync state
        storage = oauth_with_sync.token_storage
        last_sync = datetime(2024, 1, 15, 10, 30, 0, tzinfo=UTC)
        await storage.save_sync_state(
            division=123,
            resource="warehouse_transfers",
            state=SyncState(timestamp=1, last_sync=last_sync),
        )

        httpx_mock.add_response(
            json={
                "d": {
                    "results": [
                        {
                            "TransferID": "22222222-2222-2222-2222-222222222222",
                            "WarehouseFrom": "00000000-0000-0000-0000-000000000001",
                            "WarehouseTo": "00000000-0000-0000-0000-000000000002",
                        }
                    ],
                    "__next": None,
                }
            },
        )

        async with Client(oauth=oauth_with_sync) as client:
            items = []
            async for item in client.warehouse_transfers.sync(division=123):
                items.append(item)

        # Verify the request used Modified filter
        request = httpx_mock.get_request()
        assert request is not None
        assert "Modified%20ge%20datetime" in str(request.url)
        assert "2024-01-15" in str(request.url)


class TestSyncDeleted:
    """Tests for sync_deleted() method."""

    async def test_sync_deleted_yields_records(
        self, client_with_sync: Client, httpx_mock: HTTPXMock
    ) -> None:
        """sync_deleted() should yield DeletedRecord instances."""
        httpx_mock.add_response(
            json={
                "d": {
                    "results": [
                        {
                            "ID": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                            "EntityKey": "11111111-1111-1111-1111-111111111111",
                            "EntityType": 22,  # PurchaseOrders
                            "Division": 123,
                            "DeletedBy": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
                            "DeletedDate": "/Date(1704412800000)/",
                            "Timestamp": 99999,
                        }
                    ],
                    "__next": None,
                }
            },
        )

        items = []
        async for item in client_with_sync.sync_deleted(division=123):
            items.append(item)

        assert len(items) == 1
        assert items[0].entity_type == EntityType.PURCHASE_ORDERS
        assert str(items[0].entity_key) == "11111111-1111-1111-1111-111111111111"

        # Verify endpoint
        request = httpx_mock.get_request()
        assert request is not None
        assert "/sync/Deleted" in str(request.url)

    async def test_sync_deleted_filter_by_entity_type(
        self, client_with_sync: Client, httpx_mock: HTTPXMock
    ) -> None:
        """sync_deleted() should filter by entity type when specified."""
        httpx_mock.add_response(
            json={
                "d": {
                    "results": [
                        {
                            "ID": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                            "EntityKey": "11111111-1111-1111-1111-111111111111",
                            "EntityType": 22,  # PurchaseOrders
                            "Division": 123,
                            "Timestamp": 100,
                        },
                        {
                            "ID": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
                            "EntityKey": "22222222-2222-2222-2222-222222222222",
                            "EntityType": 32,  # SalesOrderHeaders
                            "Division": 123,
                            "Timestamp": 200,
                        },
                        {
                            "ID": "cccccccc-cccc-cccc-cccc-cccccccccccc",
                            "EntityKey": "33333333-3333-3333-3333-333333333333",
                            "EntityType": 36,  # ShopOrders
                            "Division": 123,
                            "Timestamp": 300,
                        },
                    ],
                    "__next": None,
                }
            },
        )

        # Filter to only PurchaseOrders and ShopOrders
        items = []
        async for item in client_with_sync.sync_deleted(
            division=123,
            entity_types=[EntityType.PURCHASE_ORDERS, EntityType.SHOP_ORDERS],
        ):
            items.append(item)

        assert len(items) == 2
        assert items[0].entity_type == EntityType.PURCHASE_ORDERS
        assert items[1].entity_type == EntityType.SHOP_ORDERS

    async def test_sync_deleted_saves_state(
        self, client_with_sync: Client, httpx_mock: HTTPXMock
    ) -> None:
        """sync_deleted() should save sync state after completion."""
        httpx_mock.add_response(
            json={
                "d": {
                    "results": [
                        {
                            "ID": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                            "EntityKey": "11111111-1111-1111-1111-111111111111",
                            "EntityType": 22,
                            "Division": 123,
                            "Timestamp": 12345,
                        }
                    ],
                    "__next": None,
                }
            },
        )

        items = []
        async for item in client_with_sync.sync_deleted(division=123):
            items.append(item)

        # Verify state was saved
        storage = client_with_sync.oauth.token_storage
        state = await storage.get_sync_state(123, "_deleted")
        assert state is not None
        assert state.timestamp == 12345

    async def test_sync_deleted_pagination(
        self, client_with_sync: Client, httpx_mock: HTTPXMock
    ) -> None:
        """sync_deleted() should handle pagination."""
        next_url = "https://start.exactonline.nl/api/v1/123/sync/Deleted?$skiptoken=abc"

        # First page
        httpx_mock.add_response(
            json={
                "d": {
                    "results": [
                        {
                            "ID": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                            "EntityKey": "11111111-1111-1111-1111-111111111111",
                            "EntityType": 22,
                            "Division": 123,
                            "Timestamp": 100,
                        }
                    ],
                    "__next": next_url,
                }
            },
        )

        # Second page
        httpx_mock.add_response(
            json={
                "d": {
                    "results": [
                        {
                            "ID": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
                            "EntityKey": "22222222-2222-2222-2222-222222222222",
                            "EntityType": 32,
                            "Division": 123,
                            "Timestamp": 200,
                        }
                    ],
                    "__next": None,
                }
            },
        )

        items = []
        async for item in client_with_sync.sync_deleted(division=123):
            items.append(item)

        assert len(items) == 2
        assert len(httpx_mock.get_requests()) == 2


class TestSyncStateModel:
    """Tests for SyncState model."""

    def test_sync_state_defaults(self) -> None:
        """SyncState should have correct defaults."""
        state = SyncState(last_sync=datetime.now(UTC))
        assert state.timestamp == 1

    def test_sync_state_serialization(self) -> None:
        """SyncState should serialize correctly."""
        now = datetime.now(UTC)
        state = SyncState(timestamp=12345, last_sync=now)

        data = state.model_dump()
        assert data["timestamp"] == 12345
        assert data["last_sync"] == now


class TestEntityType:
    """Tests for EntityType enum."""

    def test_entity_type_values(self) -> None:
        """EntityType enum should have correct values."""
        assert EntityType.PURCHASE_ORDERS == 22
        assert EntityType.SALES_ORDER_HEADERS == 32
        assert EntityType.SALES_ORDER_LINES == 33
        assert EntityType.SHOP_ORDERS == 36
        assert EntityType.GOODS_DELIVERIES == 16

    def test_deleted_record_get_entity_type(
        self,
    ) -> None:
        """DeletedRecord.get_entity_type() should return enum or None."""
        from exact_online.models.sync import DeletedRecord

        record = DeletedRecord(
            ID="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
            EntityKey="11111111-1111-1111-1111-111111111111",
            EntityType=22,
            Division=123,
            Timestamp=100,
        )

        assert record.get_entity_type() == EntityType.PURCHASE_ORDERS

        # Unknown entity type
        record2 = DeletedRecord(
            ID="bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
            EntityKey="22222222-2222-2222-2222-222222222222",
            EntityType=99999,  # Unknown
            Division=123,
            Timestamp=100,
        )

        assert record2.get_entity_type() is None
