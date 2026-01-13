# Exact Online Python SDK

A minimal, async Python SDK for syncing with the Exact Online API.

Built for our internal use at [your company]. We focused on what we needed—sync operations for purchase orders, sales orders, shop orders, and warehouse transfers. Contributions welcome!

## Features

- **Async-first** - Built on `httpx` for high-performance async operations
- **Automatic token refresh** - Handles Exact Online's rotating refresh tokens
- **Sync API support** - Efficient bulk sync using Exact Online's native Timestamp approach
- **Batching** - Combine multiple requests into a single HTTP call
- **Rate limiting** - Respects Exact Online's rate limits per division
- **Automatic retries** - Exponential backoff for transient failures
- **Pydantic models** - Type-safe responses with full IDE autocomplete
- **Snake_case conversion** - Write in snake_case, SDK converts to PascalCase for the API

## Installation

```bash
pip install exact-online
# or
uv add exact-online
```

## Quick Start

```python
from exact_online import Client, OAuth, TokenData

# 1. Implement token storage (see below)
storage = MyTokenStorage()

# 2. Create OAuth handler
oauth = OAuth(
    client_id="your-client-id",
    client_secret="your-client-secret",
    redirect_uri="https://yourapp.com/callback",
    token_storage=storage,
)

# 3. Use the client
async with Client(oauth) as client:
    me = await client.me.current()
    print(f"Logged in as {me.full_name}")
    
    # Sync purchase orders
    result = await client.purchase_orders.sync(
        division=me.current_division,
        timestamp=0,  # Start from beginning
    )
    
    for order in result.items:
        print(f"Order {order.order_number}: {order.description}")
```

## Authorization Flow

### Step 1: Redirect to Exact Online

```
https://start.exactonline.nl/api/oauth2/auth?client_id=YOUR_CLIENT_ID&redirect_uri=YOUR_REDIRECT_URI&response_type=code
```

### Step 2: Handle the callback

After the user signs in, Exact Online redirects to your `redirect_uri` with a code:

```
https://yourapp.com/callback?code=XTzM!IAAAACbPTzQJXwFhM...
```

### Step 3: Exchange the code for tokens

```python
await oauth.exchange(code)  # Tokens saved automatically via your storage
```

> **Note**: The authorization code expires after 3 minutes.

## Token Storage

You **must** implement `TokenStorage` to persist tokens. Exact Online rotates the refresh token on every refresh—if you don't save the new tokens, you lose access permanently.

```python
from exact_online import TokenData

class MyTokenStorage:
    """Your token storage implementation."""
    
    async def get_tokens(self) -> TokenData | None:
        """Load tokens from your database."""
        ...
    
    async def save_tokens(self, tokens: TokenData) -> None:
        """Save tokens to your database (called after every refresh!)."""
        ...
```

### SQLAlchemy Example

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from exact_online import TokenData

class SQLAlchemyTokenStorage:
    def __init__(self, session: AsyncSession, user_id: int):
        self.session = session
        self.user_id = user_id

    async def get_tokens(self) -> TokenData | None:
        result = await self.session.execute(
            select(ExactToken).where(ExactToken.user_id == self.user_id)
        )
        row = result.scalar_one_or_none()
        if row:
            return TokenData(
                access_token=row.access_token,
                refresh_token=row.refresh_token,
                expires_at=row.expires_at,  # Must be timezone-aware UTC!
            )
        return None

    async def save_tokens(self, tokens: TokenData) -> None:
        await self.session.merge(ExactToken(
            user_id=self.user_id,
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            expires_at=tokens.expires_at,
        ))
        await self.session.commit()
```

> **Important**: Store `expires_at` as a timezone-aware UTC datetime. Naive or local times will break the refresh logic.

## Sync Operations

The SDK supports Exact Online's native Sync API for efficient bulk synchronization.

### Basic Sync

```python
# Get initial timestamp from a specific date
from datetime import datetime

timestamp = await client.get_sync_timestamp(
    division=division,
    endpoint="PurchaseOrders",
    modified=datetime(2024, 1, 1),
)

# Sync from that timestamp
result = await client.purchase_orders.sync(division, timestamp=timestamp)

print(f"Got {len(result.items)} orders")
print(f"Next timestamp: {result.timestamp}")
print(f"Has more: {result.has_more}")

# Continue syncing while there's more data
while result.has_more:
    result = await client.purchase_orders.sync(division, timestamp=result.timestamp)
    # Process result.items...
```

### Supported Sync Endpoints

| API | Sync Endpoint Name |
|-----|-------------------|
| `client.purchase_orders` | `"PurchaseOrders"` |
| `client.sales_orders` | `"SalesOrderHeaders"` |
| `client.shop_orders` | `"ShopOrders"` |

### Warehouse Transfers (No Sync Endpoint)

Warehouse transfers don't have a sync endpoint. Use `sync_by_modified()` instead:

```python
from datetime import datetime

result = await client.warehouse_transfers.sync_by_modified(
    division=division,
    modified_since=datetime(2024, 1, 1),
)

# Use result.last_modified for the next sync
next_sync_from = result.last_modified
```

## Batching

Combine multiple requests into a single HTTP call for better efficiency:

```python
from exact_online import BatchRequest

result = await client.batch([
    BatchRequest("GET", "/sync/PurchaseOrder/PurchaseOrders", division),
    BatchRequest("GET", "/sync/SalesOrder/SalesOrderHeaders", division),
    BatchRequest("GET", "/sync/Manufacturing/ShopOrders", division),
])

for response in result:
    if response.is_success:
        items = response.data.get("d", {}).get("results", [])
        print(f"Got {len(items)} items")
    else:
        print(f"Error: {response.error}")

print(f"Success: {result.success_count}, Failed: {result.error_count}")
```

## CRUD Operations

### Create

```python
# Pass snake_case - SDK converts to PascalCase automatically
order = await client.purchase_orders.create(division, {
    "supplier": "supplier-guid",
    "description": "New order",
    "warehouse": "warehouse-guid",
})
print(f"Created: {order.id}")
```

### Read

```python
# Get single record
order = await client.purchase_orders.get(division, order_id)

# List with filters
result = await client.purchase_orders.list(
    division,
    odata_filter="OrderStatus eq 'Open'",
    top=60,
)

# Iterate all (handles pagination)
async for order in client.purchase_orders.list_all(division):
    print(order.order_number)
```

### Update

```python
order = await client.purchase_orders.update(division, order_id, {
    "description": "Updated description",
})
```

### Delete

```python
await client.purchase_orders.delete(division, order_id)
```

## Litestar + Ariadne GraphQL Integration

Here's a complete example for a Litestar backend with Ariadne GraphQL:

### Project Structure

```
your_app/
├── app.py              # Litestar app with lifespan
├── graphql/
│   ├── schema.py       # GraphQL schema
│   └── resolvers.py    # Resolvers
└── exact/
    ├── client.py       # Exact Online client setup
    └── storage.py      # Token storage implementation
```

### app.py

```python
from contextlib import asynccontextmanager
from litestar import Litestar
from litestar.contrib.sqlalchemy.plugins import SQLAlchemyAsyncConfig
from ariadne.asgi import GraphQL

from your_app.exact.client import exact_client, init_exact_client, close_exact_client
from your_app.graphql.schema import schema


@asynccontextmanager
async def lifespan(app: Litestar):
    """Manage application lifecycle."""
    await init_exact_client()
    yield
    await close_exact_client()


graphql_app = GraphQL(schema)

app = Litestar(
    route_handlers=[],
    lifespan=[lifespan],
    middleware=[],
)

# Mount GraphQL
app.asgi_router.routes.append(("/graphql", graphql_app))
```

### exact/client.py

```python
from exact_online import Client, OAuth

from your_app.exact.storage import get_token_storage

# Global client instance
exact_client: Client | None = None


async def init_exact_client():
    """Initialize Exact Online client."""
    global exact_client
    
    storage = await get_token_storage()
    oauth = OAuth(
        client_id="your-client-id",
        client_secret="your-client-secret",
        redirect_uri="https://yourapp.com/callback",
        token_storage=storage,
    )
    
    exact_client = Client(oauth)
    await exact_client.start()


async def close_exact_client():
    """Close Exact Online client."""
    global exact_client
    if exact_client:
        await exact_client.stop()
        exact_client = None


def get_exact_client() -> Client:
    """Get the Exact Online client."""
    if exact_client is None:
        raise RuntimeError("Exact Online client not initialized")
    return exact_client
```

### exact/storage.py

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from exact_online import TokenData
from your_app.db import get_session
from your_app.models import ExactToken


class TokenStorage:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_tokens(self) -> TokenData | None:
        result = await self.session.execute(select(ExactToken).limit(1))
        row = result.scalar_one_or_none()
        if row:
            return TokenData(
                access_token=row.access_token,
                refresh_token=row.refresh_token,
                expires_at=row.expires_at,
            )
        return None

    async def save_tokens(self, tokens: TokenData) -> None:
        # Upsert token record
        existing = await self.session.execute(select(ExactToken).limit(1))
        row = existing.scalar_one_or_none()
        
        if row:
            row.access_token = tokens.access_token
            row.refresh_token = tokens.refresh_token
            row.expires_at = tokens.expires_at
        else:
            self.session.add(ExactToken(
                access_token=tokens.access_token,
                refresh_token=tokens.refresh_token,
                expires_at=tokens.expires_at,
            ))
        
        await self.session.commit()


async def get_token_storage() -> TokenStorage:
    session = await get_session()
    return TokenStorage(session)
```

### graphql/schema.py

```python
from ariadne import make_executable_schema, QueryType, MutationType
from ariadne.contrib.federation.utils import convert_case

type_defs = """
    type Query {
        me: Me!
        purchaseOrders(timestamp: Int): SyncResult!
    }
    
    type Mutation {
        createPurchaseOrder(input: PurchaseOrderInput!): PurchaseOrder!
    }
    
    type Me {
        fullName: String!
        currentDivision: Int!
    }
    
    type PurchaseOrder {
        id: ID!
        orderNumber: Int
        description: String
        supplierName: String
    }
    
    type SyncResult {
        items: [PurchaseOrder!]!
        timestamp: Int!
        hasMore: Boolean!
    }
    
    input PurchaseOrderInput {
        supplier: ID!
        description: String
        warehouse: ID
    }
"""

query = QueryType()
mutation = MutationType()

# Enable snake_case to camelCase conversion
query.set_alias("me", convert_case)
mutation.set_alias("createPurchaseOrder", convert_case)

schema = make_executable_schema(type_defs, query, mutation)
```

### graphql/resolvers.py

```python
from your_app.exact.client import get_exact_client
from your_app.graphql.schema import query, mutation


@query.field("me")
async def resolve_me(_, info):
    """Get current user info."""
    client = get_exact_client()
    me = await client.me.current()
    return me  # Pydantic model - Ariadne handles serialization!


@query.field("purchaseOrders")
async def resolve_purchase_orders(_, info, timestamp: int = 0):
    """Sync purchase orders."""
    client = get_exact_client()
    me = await client.me.current()
    
    result = await client.purchase_orders.sync(
        division=me.current_division,
        timestamp=timestamp,
    )
    
    return {
        "items": result.items,  # Pydantic models
        "timestamp": result.timestamp,
        "has_more": result.has_more,
    }


@mutation.field("createPurchaseOrder")
async def resolve_create_purchase_order(_, info, input: dict):
    """Create a new purchase order."""
    client = get_exact_client()
    me = await client.me.current()
    
    # Input comes as snake_case from Ariadne's convert_case
    # SDK converts to PascalCase automatically
    order = await client.purchase_orders.create(
        division=me.current_division,
        data=input,
    )
    
    return order  # Pydantic model
```

## Background Sync Job

For periodic syncing, run a background task:

```python
import asyncio
from datetime import datetime

from your_app.exact.client import get_exact_client
from your_app.db import save_to_database


async def sync_job():
    """Run every 5 minutes via scheduler."""
    client = get_exact_client()
    me = await client.me.current()
    division = me.current_division
    
    # Load last timestamps from your database
    timestamps = await load_timestamps()
    
    # Sync purchase orders
    result = await client.purchase_orders.sync(
        division, 
        timestamp=timestamps.get("purchase_orders", 0),
    )
    await save_to_database("purchase_orders", result.items)
    await save_timestamp("purchase_orders", result.timestamp)
    
    # Sync sales orders
    result = await client.sales_orders.sync(
        division,
        timestamp=timestamps.get("sales_orders", 0),
    )
    await save_to_database("sales_orders", result.items)
    await save_timestamp("sales_orders", result.timestamp)
    
    # Sync shop orders
    result = await client.shop_orders.sync(
        division,
        timestamp=timestamps.get("shop_orders", 0),
    )
    await save_to_database("shop_orders", result.items)
    await save_timestamp("shop_orders", result.timestamp)
    
    # Warehouse transfers (no sync endpoint)
    result = await client.warehouse_transfers.sync_by_modified(
        division,
        modified_since=timestamps.get("warehouse_transfers_modified"),
    )
    await save_to_database("warehouse_transfers", result.items)
    if result.last_modified:
        await save_timestamp("warehouse_transfers_modified", result.last_modified)
```

## Available APIs

| Property | Model | Sync Support |
|----------|-------|--------------|
| `client.me` | `Me` | - |
| `client.purchase_orders` | `PurchaseOrder` | ✅ |
| `client.purchase_order_lines` | `PurchaseOrderLine` | ❌ |
| `client.sales_orders` | `SalesOrder` | ✅ |
| `client.shop_orders` | `ShopOrder` | ✅ |
| `client.warehouse_transfers` | `WarehouseTransfer` | ❌ (use `sync_by_modified`) |

## Error Handling

```python
from exact_online import APIError, RateLimitError, AuthenticationError

try:
    result = await client.purchase_orders.sync(division, timestamp=0)
except RateLimitError:
    # Wait and retry - SDK handles this automatically with retries
    pass
except AuthenticationError:
    # User needs to re-authenticate
    pass
except APIError as e:
    print(f"API error {e.status_code}: {e.message}")
```

## License

MIT
