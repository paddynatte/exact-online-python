# Exact Online Python SDK

Internal SDK for Exact Online API integration with our Litestar + Ariadne GraphQL backend.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           EXACT ONLINE SDK                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  GraphQL (Ariadne)          SDK                      Exact Online API   │
│  ─────────────────          ───                      ─────────────────  │
│                                                                         │
│  camelCase  ──────►  snake_case  ──────►  PascalCase                   │
│  (frontend)     │    (internal)      │    (API)                        │
│                 │                    │                                  │
│           convert_case          auto-convert                            │
│           (Ariadne)            on create/update                         │
│                                                                         │
│  Pydantic models returned with snake_case attributes                    │
│  Ariadne serializes directly + convert_case for GraphQL output          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Setup

### 1. Token Storage Implementation

You **must** implement `TokenStorage` to persist OAuth tokens. Exact Online rotates refresh tokens on every refresh - if you don't persist, you lose access.

For sync support, also implement the optional `get_sync_state` and `save_sync_state` methods.

```python
from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from exact_online import TokenData, SyncState


class DatabaseTokenStorage:
    """TokenStorage implementation with sync state support."""

    def __init__(self, db: AsyncSession, user_id: UUID):
        self.db = db
        self.user_id = user_id

    # Required: Token persistence
    async def get_tokens(self) -> TokenData | None:
        row = await self.db.scalar(
            select(ExactToken).where(ExactToken.user_id == self.user_id)
        )
        if row:
            return TokenData(**row.data)
        return None

    async def save_tokens(self, tokens: TokenData) -> None:
        await self.db.merge(
            ExactToken(user_id=self.user_id, data=tokens.model_dump(mode="json"))
        )
        await self.db.commit()

    # Optional: For sync() support
    async def get_sync_state(self, division: int, resource: str) -> SyncState | None:
        row = await self.db.scalar(
            select(SyncStateTable).where(
                SyncStateTable.user_id == self.user_id,
                SyncStateTable.division == division,
                SyncStateTable.resource == resource,
            )
        )
        return SyncState(**row.data) if row else None

    async def save_sync_state(
        self, division: int, resource: str, state: SyncState
    ) -> None:
        await self.db.merge(
            SyncStateTable(
                user_id=self.user_id,
                division=division,
                resource=resource,
                data=state.model_dump(mode="json"),
            )
        )
        await self.db.commit()
```

### 2. Litestar Lifespan Integration

```python
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from litestar import Litestar
from litestar.datastructures import State

from exact_online import Client, OAuth


@asynccontextmanager
async def lifespan(app: Litestar) -> AsyncGenerator[None, None]:
    # Startup: nothing needed - clients created per-request
    yield
    # Shutdown: cleanup handled by context managers


app = Litestar(
    route_handlers=[...],
    lifespan=[lifespan],
)
```

### 3. GraphQL Context with Exact Client

```python
from litestar import Request
from exact_online import Client, OAuth


async def get_context(request: Request) -> dict:
    """Build GraphQL context with Exact client."""
    db = request.state.db
    user = request.user

    storage = DatabaseTokenStorage(db, user.id)
    oauth = OAuth(
        client_id=settings.EXACT_CLIENT_ID,
        client_secret=settings.EXACT_CLIENT_SECRET,
        redirect_uri=settings.EXACT_REDIRECT_URI,
        token_storage=storage,
    )

    client = Client(oauth=oauth)

    return {
        "db": db,
        "user": user,
        "exact": client,  # Access via info.context["exact"]
    }
```

### 4. OAuth Callback Endpoint

```python
from litestar import get, Request
from litestar.response import Redirect


@get("/auth/exact/callback")
async def exact_callback(request: Request, code: str) -> Redirect:
    """Handle OAuth callback from Exact Online."""
    db = request.state.db
    user = request.user

    storage = DatabaseTokenStorage(db, user.id)
    oauth = OAuth(
        client_id=settings.EXACT_CLIENT_ID,
        client_secret=settings.EXACT_CLIENT_SECRET,
        redirect_uri=settings.EXACT_REDIRECT_URI,
        token_storage=storage,
    )

    # Exchange code for tokens (automatically saved via storage)
    await oauth.exchange(code)

    return Redirect("/dashboard")
```

---

## CRUD Operations

### GraphQL Resolver Examples

```python
from ariadne import QueryType, MutationType
from graphql import GraphQLResolveInfo

query = QueryType()
mutation = MutationType()


@query.field("purchaseOrders")
async def resolve_purchase_orders(_, info: GraphQLResolveInfo, division: int):
    """List purchase orders."""
    client = info.context["exact"]

    async with client:
        result = await client.purchase_orders.list(
            division=division,
            odata_filter="Status eq 'Open'",
        )
        return result.items  # Pydantic models serialize directly


@query.field("purchaseOrder")
async def resolve_purchase_order(_, info: GraphQLResolveInfo, division: int, id: str):
    """Get a single purchase order."""
    client = info.context["exact"]

    async with client:
        return await client.purchase_orders.get(division=division, id=id)


@mutation.field("createPurchaseOrder")
async def resolve_create_purchase_order(
    _, info: GraphQLResolveInfo, division: int, input: dict
):
    """Create a purchase order.

    Input uses snake_case (from Ariadne's convert_case).
    SDK auto-converts to PascalCase for Exact API.
    """
    client = info.context["exact"]

    async with client:
        return await client.purchase_orders.create(
            division=division,
            data={
                "supplier": input["supplier"],
                "purchase_order_lines": [
                    {
                        "item": line["item"],
                        "quantity": line["quantity"],
                        "net_price": line["net_price"],
                    }
                    for line in input["lines"]
                ],
            },
        )


@mutation.field("updatePurchaseOrderLine")
async def resolve_update_line(
    _, info: GraphQLResolveInfo, division: int, id: str, input: dict
):
    """Update a specific line on a purchase order."""
    client = info.context["exact"]

    async with client:
        return await client.purchase_order_lines.update(
            division=division,
            id=id,
            data=input,  # snake_case auto-converted
        )
```

### Iterating All Records

```python
@query.field("allPurchaseOrders")
async def resolve_all_purchase_orders(_, info: GraphQLResolveInfo, division: int):
    """Get all purchase orders (handles pagination automatically)."""
    client = info.context["exact"]
    orders = []

    async with client:
        async for order in client.purchase_orders.list_all(division=division):
            orders.append(order)

    return orders
```

---

## Sync API

For background synchronization of Exact Online data to your database.

### How It Works

| Resource | Method | Records/Call |
|----------|--------|--------------|
| PurchaseOrders | Sync API | 1000 |
| PurchaseItemPrices | Sync API | 1000 |
| SalesOrders | Sync API | 1000 |
| ShopOrders | Sync API | 1000 |
| Accounts | Modified filter | 60 |
| Items | Modified filter | 60 |
| WarehouseTransfers | Modified filter | 60 |
| GoodsReceipts | Modified filter | 60 |
| StockCounts | Modified filter | 60 |
| Warehouses | Modified filter | 60 |
| Divisions | Modified filter | 60 |

The SDK automatically:
- Loads last sync timestamp from your `TokenStorage`
- Uses Sync API (efficient) or Modified filter (fallback)
- Handles pagination
- Saves new timestamp after completion

### Background Sync Task

```python
from exact_online import Client, OAuth


async def sync_exact_online(division: int, db: AsyncSession, user_id: UUID):
    """Background task - runs every 5-10 minutes."""
    storage = DatabaseTokenStorage(db, user_id)
    oauth = OAuth(
        client_id=settings.EXACT_CLIENT_ID,
        client_secret=settings.EXACT_CLIENT_SECRET,
        redirect_uri=settings.EXACT_REDIRECT_URI,
        token_storage=storage,
    )

    async with Client(oauth=oauth) as client:
        # Sync API resources (1000 records/call)
        async for order in client.purchase_orders.sync(division):
            await db.merge(PurchaseOrderORM.from_exact(order))

        async for price in client.purchase_item_prices.sync(division):
            await db.merge(PurchaseItemPriceORM.from_exact(price))

        async for order in client.sales_orders.sync(division):
            await db.merge(SalesOrderORM.from_exact(order))

        async for order in client.shop_orders.sync(division):
            await db.merge(ShopOrderORM.from_exact(order))

        # Modified filter resources (60 records/call)
        async for account in client.accounts.sync(division):
            await db.merge(AccountORM.from_exact(account))

        async for item in client.items.sync(division):
            await db.merge(ItemORM.from_exact(item))

        async for transfer in client.warehouse_transfers.sync(division):
            await db.merge(WarehouseTransferORM.from_exact(transfer))

        async for receipt in client.goods_receipts.sync(division):
            await db.merge(GoodsReceiptORM.from_exact(receipt))

        async for count in client.stock_counts.sync(division):
            await db.merge(StockCountORM.from_exact(count))

    await db.commit()
    print(f"Sync complete for division {division}")
```

### Litestar-SAQ Integration

```python
from litestar_saq import SAQPlugin, CronJob


async def sync_job(ctx: dict) -> None:
    """Cron job for Exact Online sync."""
    async with get_db_session() as db:
        for user in await get_users_with_exact_tokens(db):
            for division in user.exact_divisions:
                await sync_exact_online(division, db, user.id)


saq_plugin = SAQPlugin(
    cron_jobs=[
        CronJob(
            function=sync_job,
            cron="*/5 * * * *",  # Every 5 minutes
            unique=True,
        ),
    ],
)
```

### Deleted API (Optional)

For tracking deletions from Exact Online. Uses the central `/sync/Deleted` endpoint.

```python
from exact_online import EntityType


async def handle_deletions(division: int, client: Client, db: AsyncSession):
    """Process deleted records (optional)."""
    async for deleted in client.sync_deleted(division):
        match deleted.entity_type:
            case EntityType.PURCHASE_ORDERS:
                await db.execute(
                    update(PurchaseOrderORM)
                    .where(PurchaseOrderORM.id == deleted.entity_key)
                    .values(status="deleted")
                )
            case EntityType.SALES_ORDER_HEADERS:
                await db.execute(
                    update(SalesOrderORM)
                    .where(SalesOrderORM.id == deleted.entity_key)
                    .values(status="deleted")
                )
```

**Note:** Exact Online only keeps deleted records for 2 months.

---

## Batching

Combine multiple discrete operations into a single HTTP call.

```python
from exact_online import BatchRequest


async def batch_operations(client: Client, division: int):
    """Execute multiple operations in one request."""
    async with client:
        result = await client.batch(
            division=division,
            requests=[
                BatchRequest(
                    method="GET",
                    endpoint="/purchaseorder/PurchaseOrders",
                    params={"$top": "10"},
                ),
                BatchRequest(
                    method="GET",
                    endpoint="/salesorder/SalesOrders",
                    params={"$filter": "Status eq 12"},
                ),
                BatchRequest(
                    method="POST",
                    endpoint="/inventory/WarehouseTransfers",
                    body={
                        "WarehouseFrom": "guid-1",
                        "WarehouseTo": "guid-2",
                        "WarehouseTransferLines": [...],
                    },
                ),
            ],
        )

        for response in result:
            if response.is_success:
                print(f"Success: {response.data}")
            else:
                print(f"Error: {response.status_code}")
```

---

## Working with Units (PurchaseUnitFactor)

When supplier items have different purchase units than base units:

```python
async def get_purchase_unit_description(
    client: Client, division: int, supplier_item_id: str
) -> str:
    """Get the unit description for a supplier item."""
    async with client:
        supplier_item = await client.supplier_items.get(division, supplier_item_id)

        if supplier_item.item_unit:
            unit = await client.units.get(division, str(supplier_item.item_unit))
            return unit.description or unit.code

        return "pc"  # Default
```

Usage in service:

```python
unit_desc = await get_purchase_unit_description(client, division, supplier_item_id)
# Returns: "kg", "pc", "box", etc.
```

---

## API Architecture

The SDK uses a **mixin-based architecture** for API capabilities. Each resource explicitly declares which operations it supports:

| Mixin | Methods | Description |
|-------|---------|-------------|
| `ReadableMixin` | `list()`, `list_all()`, `list_next()`, `get()` | Query and retrieve records |
| `WritableMixin` | `create()`, `update()`, `delete()` | Mutate records |
| `SyncableMixin` | `sync()` | Incremental synchronization |

**Benefits:**
- **Type-safe**: IDE autocomplete only shows available methods
- **Discoverable**: `hasattr(client.units, 'create')` returns `False`
- **Explicit**: No `NotImplementedError` surprises at runtime

### Checking Capabilities

```python
from exact_online.api.base import ReadableMixin, WritableMixin, SyncableMixin

# Type checking
if isinstance(client.purchase_orders, SyncableMixin):
    async for order in client.purchase_orders.sync(division):
        ...

# Runtime check
if hasattr(client.units, 'create'):
    # This won't execute - Units is read-only
    await client.units.create(...)
```

---

## Available API Resources

| Resource | Property | list | get | create | update | delete | sync |
|----------|----------|:----:|:---:|:------:|:------:|:------:|:----:|
| **Accounts** | `client.accounts` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ Modified |
| **Items** | `client.items` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ Modified |
| **Purchase Item Prices** | `client.purchase_item_prices` | - | - | - | - | - | ✓ Sync API |
| **Purchase Orders** | `client.purchase_orders` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ Sync API |
| **Purchase Order Lines** | `client.purchase_order_lines` | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| **Sales Orders** | `client.sales_orders` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ Sync API |
| **Shop Orders** | `client.shop_orders` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ Sync API |
| **Warehouse Transfers** | `client.warehouse_transfers` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ Modified |
| **Goods Receipts** | `client.goods_receipts` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ Modified |
| **Goods Receipt Lines** | `client.goods_receipt_lines` | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| **Stock Counts** | `client.stock_counts` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ Modified |
| **Stock Count Lines** | `client.stock_count_lines` | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| **Supplier Items** | `client.supplier_items` | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| **Units** | `client.units` | ✓ | ✓ | - | - | - | - |
| **Warehouses** | `client.warehouses` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ Modified |
| **Divisions** | `client.divisions` | ✓ | ✓ | - | - | - | ✓ Modified |
| **Me** | `client.me` | - | ✓ | - | - | - | - |

**Sync Methods:**
- **Sync API** = 1000 records/call (fast, timestamp-based)
- **Modified** = 60 records/call (uses `Modified ge datetime'...'` filter)

### Common Operations

```python
# List with OData filter
result = await client.purchase_orders.list(
    division=123,
    odata_filter="Status eq 'Open'",
    select=["PurchaseOrderID", "Supplier", "OrderDate"],
    top=60,  # Max 60 per call
)

# Pagination
while result.has_more:
    result = await client.purchase_orders.list_next(result.next_url, division=123)

# Get by ID
order = await client.purchase_orders.get(division=123, id="guid")

# Create (snake_case auto-converted)
order = await client.purchase_orders.create(
    division=123,
    data={"supplier": "guid", "purchase_order_lines": [...]},
)

# Update
order = await client.purchase_orders.update(
    division=123,
    id="guid",
    data={"description": "Updated"},
)

# Delete
await client.purchase_orders.delete(division=123, id="guid")

# Sync (incremental)
async for order in client.purchase_orders.sync(division=123):
    await db.merge(order)
```

---

## Rate Limiting

The SDK automatically handles Exact Online's rate limits:
- **60 requests/minute** per division
- **5000 requests/day** per division

Rate limit headers are parsed and the SDK waits when approaching limits.

---

## Error Handling

```python
from exact_online import (
    APIError,
    RateLimitError,
    TokenExpiredError,
    AuthenticationError,
)


async def safe_operation(client: Client, division: int):
    try:
        async with client:
            return await client.purchase_orders.list(division=division)
    except TokenExpiredError:
        # User needs to re-authenticate
        raise HTTPException(401, "Please reconnect to Exact Online")
    except RateLimitError:
        # Retry later
        raise HTTPException(429, "Rate limit exceeded")
    except APIError as e:
        # General API error
        raise HTTPException(e.status_code, str(e))
```

---

## Retry Configuration

```python
from exact_online import Client, RetryConfig


async with Client(
    oauth=oauth,
    retry=RetryConfig(
        max_retries=3,
        base_delay=1.0,
        max_delay=30.0,
        jitter=True,
    ),
) as client:
    # Automatic retries on 429, 500, 502, 503, 504
    ...
```
