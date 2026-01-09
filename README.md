# exact-online-python

A Python SDK for the Exact Online API. Async-first, fully typed, with automatic token refresh, rate limiting, retry logic, and webhook support.

## Installation

```bash
pip install exact-online-python
```

Requires Python 3.13+.

## Quick Start

The SDK requires you to implement token storage yourself—this keeps the SDK lean and lets you use whatever persistence layer you prefer (database, Redis, file, etc.).

```python
from exact_online import ExactOnlineClient, OAuthManager, ExactRegion, TokenData

class MyTokenStorage:
    async def get_tokens(self) -> TokenData | None:
        # Load from your database
        ...
    
    async def save_tokens(self, tokens: TokenData) -> None:
        # Save to your database
        ...

oauth = OAuthManager(
    client_id="your-client-id",
    client_secret="your-client-secret",
    redirect_uri="https://your-app.com/callback",
    region=ExactRegion.NL,
    token_storage=MyTokenStorage(),
)

async with ExactOnlineClient(oauth=oauth) as client:
    orders = await client.purchase_orders.list(division=123)
```

## Authentication

Exact Online uses OAuth 2.0. Access tokens expire after 10 minutes—the SDK handles this automatically by refreshing 30 seconds before expiry to prevent race conditions.

**Important**: Exact Online uses rotating refresh tokens. When you refresh an access token, you also receive a *new* refresh token, and the previous one is immediately invalidated. If you don't persist the new tokens, you lose access and the user must re-authenticate. This is why the SDK requires you to implement `TokenStorage`.

> **Source**: [Exact Online OAuth Documentation](https://support.exactonline.com/community/s/knowledge-base#All-All-DNO-Content-oauth-eol-oauth-dev-impleovervw)

### Initial Authorization

Your application is responsible for the OAuth redirect flow. The SDK provides helpers to generate the authorization URL and exchange the code for tokens.

Generate the URL and redirect the user:

```python
url = oauth.get_authorization_url(state="csrf-token")
# Redirect user to this URL...
```

After the user authorizes your app, Exact Online redirects them back with a code. Exchange it for tokens:

```python
tokens = await oauth.exchange_code(authorization_code)
# Tokens are automatically saved via your TokenStorage
```

### Automatic Token Refresh

The SDK automatically refreshes tokens when needed—you don't need to handle this manually. If you need direct access to the current token:

```python
access_token = await oauth.ensure_valid_token()
```

## Regions

Exact Online operates separate instances per region, each with its own API endpoint. You must use the correct region for your account.

```python
from exact_online import ExactRegion

ExactRegion.NL  # Netherlands  → start.exactonline.nl
ExactRegion.BE  # Belgium     → start.exactonline.be
ExactRegion.DE  # Germany     → start.exactonline.de
ExactRegion.UK  # UK          → start.exactonline.co.uk
ExactRegion.US  # USA         → start.exactonline.com
ExactRegion.ES  # Spain       → start.exactonline.es
ExactRegion.FR  # France      → start.exactonline.fr
```

## API Usage

All API methods require an explicit `division` parameter. A division represents a company/administration within Exact Online. This explicit approach prevents accidentally querying the wrong division when working with multiple companies.

> **Source**: [Exact Online REST API Documentation](https://support.exactonline.com/community/s/knowledge-base#All-All-DNO-Content-gettingstarted)

### Listing Records

The standard API returns up to 60 records per request. The `list()` method returns a `ListResult` that is iterable—you can use it directly in a for loop.

```python
result = await client.purchase_orders.list(division=123)

for order in result:
    print(order.order_number)

# Also supports len()
print(f"Got {len(result)} orders")
```

You can filter and select specific fields using OData query parameters:

```python
result = await client.purchase_orders.list(
    division=123,
    odata_filter="ReceiptStatus eq 10",  # OData $filter
    select=["PurchaseOrderID", "Supplier", "OrderDate"],  # OData $select
    top=60,   # Max records (capped at 60)
)
```

The `odata_filter` parameter accepts standard OData filter expressions. Common examples:

```python
# Open orders only
odata_filter="ReceiptStatus eq 10"

# Orders from specific supplier
odata_filter="Supplier eq guid'abc-123-def'"

# Orders created after a date
odata_filter="Created gt datetime'2024-01-01'"

# Combining conditions
odata_filter="ReceiptStatus eq 10 and Supplier eq guid'abc-123-def'"
```

### Pagination

When there are more than 60 records, use the `next_url` property to fetch subsequent pages. The SDK uses Exact Online's `__next` / `$skiptoken` mechanism for reliable pagination.

```python
result = await client.purchase_orders.list(division=123)
all_orders = list(result.items)

while result.next_url:
    result = await client.purchase_orders.list_next(result.next_url, division=123)
    all_orders.extend(result.items)

print(f"Total orders: {len(all_orders)}")
```

This approach is more reliable than offset-based pagination (`$skip`) because it handles records being added or removed during pagination.

For convenience, you can also use `list_all()` which handles pagination automatically:

```python
async for order in client.purchase_orders.list_all(division=123):
    print(order.order_number)
```

### Getting a Single Record

Fetch a specific record by its GUID.

```python
order = await client.purchase_orders.get(
    division=123,
    id="abc-123-def-456",
)
```

### Creating Records

Create new records by passing a dictionary with the API field names (PascalCase, as Exact Online expects).

```python
new_order = await client.purchase_orders.create(
    division=123,
    data={
        "Supplier": "supplier-guid",
        "Warehouse": "warehouse-guid",
        "PurchaseOrderLines": [
            {"Item": "item-guid", "Quantity": 10, "UnitPrice": 25.00}
        ],
    },
)
```

### Updating Records

Update existing records by GUID. Only include the fields you want to change.

```python
updated = await client.purchase_orders.update(
    division=123,
    id="order-guid",
    data={"Remarks": "Updated via API"},
)
```

### Deleting Records

Delete a record by GUID.

```python
await client.purchase_orders.delete(
    division=123,
    id="order-guid",
)
```

## Sync API

Some entities support a bulk sync endpoint that returns up to 1000 records per request (compared to 60 for the standard API). The sync API uses timestamps for incremental syncing—you only fetch records that changed since your last sync.

> **Source**: [Exact Online Sync API Documentation](https://start.exactonline.nl/docs/HlpRestAPIResourcesDetails.aspx?name=ReadSyncSyncSyncTimestamp)

### Initial Sync

Start with `timestamp=0` to fetch all records.

```python
result = await client.purchase_orders.sync(division=123, timestamp=0)

print(f"Fetched {len(result.items)} orders")
print(f"Next timestamp: {result.timestamp}")

# Store result.timestamp in your database for next sync
```

### Incremental Sync

Use the timestamp from your last sync to only fetch modified records.

```python
result = await client.purchase_orders.sync(
    division=123,
    timestamp=stored_timestamp,  # From your database
)

for order in result.items:
    # Process changed/new orders
    ...

# Update stored timestamp
stored_timestamp = result.timestamp
```

The `result.has_more` flag indicates if there are more records to fetch. Keep calling with the returned timestamp until `has_more` is `False`.

## Webhooks

Webhooks allow Exact Online to push changes to your application in real-time, rather than polling with `sync()`. When a record is created, updated, or deleted, Exact Online sends an HTTP POST to your endpoint.

> **Note**: The SDK handles webhook validation and parsing. You're responsible for hosting the webhook endpoint (using FastAPI, Flask, etc.) and managing subscriptions via the Exact Online web interface.

### How Webhooks Work

```
┌─────────────┐                    ┌─────────────────┐
│ Exact Online│  ──HTTP POST──►   │ Your Web Server │
│             │   (webhook)        │ (FastAPI/Flask) │
└─────────────┘                    └─────────────────┘
```

1. **You** create a webhook subscription in Exact Online's web interface
2. **Exact Online** sends HTTP POST requests to your URL when changes occur
3. **Your server** validates the signature and processes the payload using the SDK

### Webhook Payload Structure

Exact Online sends webhooks with this structure:

```json
{
  "Content": {
    "Topic": "PurchaseOrders",
    "Action": "Update",
    "Division": 123456,
    "Key": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "Endpoint": "/api/v1/123456/purchaseorder/PurchaseOrders(guid'...')",
    "Timestamp": "2024-01-15T14:30:00Z"
  },
  "HashCode": "..."
}
```

### Validating and Parsing Webhooks

Always validate the signature before processing a webhook to ensure it came from Exact Online:

```python
from exact_online.webhooks import validate_and_parse, WebhookValidationError

async def handle_webhook(request):
    payload = await request.body()
    signature = request.headers.get("X-Exact-Signature", "")
    
    try:
        event = validate_and_parse(payload, signature, webhook_secret)
        
        print(f"Received: {event.topic}.{event.action}")
        print(f"Entity ID: {event.key}")
        print(f"Division: {event.division}")
        
        # Fetch the full entity if needed
        if event.topic == "PurchaseOrders":
            order = await client.purchase_orders.get(
                division=event.division,
                id=event.key,
            )
            # Process the order...
            
        return {"status": "ok"}
        
    except WebhookValidationError:
        # Invalid signature - reject the request
        return {"error": "Invalid signature"}, 401
```

### Parsing Without Validation

If you handle signature validation separately (e.g., in middleware), you can parse the payload directly:

```python
from exact_online.webhooks import parse_webhook

event = parse_webhook(payload)
print(f"{event.topic}.{event.action}: {event.key}")
```

### Computing Signatures

For testing or if you need to verify signatures manually:

```python
from exact_online.webhooks import compute_signature, verify_signature

# Compute what the signature should be
expected = compute_signature(payload_bytes, webhook_secret)

# Or verify directly
is_valid = verify_signature(payload_bytes, received_signature, webhook_secret)
```

### WebhookEvent Properties

The parsed `WebhookEvent` contains:

| Property | Type | Description |
|----------|------|-------------|
| `topic` | `str` | Entity type (e.g., "PurchaseOrders", "Accounts") |
| `action` | `str` | Change type: "Create", "Update", or "Delete" |
| `division` | `int` | Division ID where the change occurred |
| `key` | `str` | GUID of the affected entity |
| `endpoint` | `str \| None` | API endpoint to fetch the entity |
| `timestamp` | `datetime \| None` | When the change occurred |
| `hash_code` | `str \| None` | Exact Online's hash code |

### FastAPI Example

```python
from fastapi import FastAPI, HTTPException, Request
from exact_online.webhooks import validate_and_parse, WebhookValidationError

app = FastAPI()
WEBHOOK_SECRET = "your-secret-from-exact-online"

@app.post("/webhooks/exact")
async def receive_webhook(request: Request):
    payload = await request.body()
    signature = request.headers.get("X-Exact-Signature", "")
    
    try:
        event = validate_and_parse(payload, signature, WEBHOOK_SECRET)
        
        if event.topic == "PurchaseOrders":
            if event.action == "Create":
                # Handle new order
                pass
            elif event.action == "Update":
                # Handle updated order
                pass
            elif event.action == "Delete":
                # Handle deleted order
                pass
        
        return {"status": "ok"}
        
    except WebhookValidationError:
        raise HTTPException(status_code=401, detail="Invalid signature")
```

### Setting Up Webhooks

1. Go to the Exact Online web interface
2. Navigate to your app's settings
3. Create a webhook subscription for the topics you need (e.g., "PurchaseOrders")
4. Set the URL to your publicly accessible endpoint
5. Copy the webhook secret and use it in your application

### Sync vs Webhooks

| Feature | Sync API | Webhooks |
|---------|----------|----------|
| **Direction** | Pull (you request data) | Push (data sent to you) |
| **Timing** | On-demand | Real-time |
| **Use case** | Batch processing, initial sync | Live updates |
| **Setup** | Just code | Code + subscription in Exact Online |

For most applications, use **both**: webhooks for real-time updates and sync for initial data load or recovery.

## Batch Operations

The SDK supports Exact Online's `$batch` endpoint for combining multiple requests into a single HTTP call. This is useful for reducing round-trips when you need to perform multiple operations.

> **Source**: [OData Batch Processing](https://www.odata.org/documentation/odata-version-3-0/batch-processing/)

### Building a Batch Request

Use `BatchRequest` to combine multiple GET, POST, PUT, or DELETE operations:

```python
from exact_online.batch import BatchRequest

batch = BatchRequest(division=123)

# Add multiple operations
batch.add_get("/purchaseorder/PurchaseOrders", params={"$top": "10"})
batch.add_get("/crm/Accounts", params={"$top": "5"})
batch.add_post("/crm/Accounts", {"Name": "New Customer"})

# Execute all at once
results = await client.execute_batch(batch)

for result in results:
    if result.success:
        print(f"Status {result.status_code}: {result.data}")
    else:
        print(f"Failed: {result.error}")
```

### Batch Methods

```python
# GET requests
batch.add_get(endpoint, params={"$filter": "Status eq 'Active'"})

# POST requests (create)
batch.add_post(endpoint, data={"Name": "New Item"})

# PUT requests (update)
batch.add_put(endpoint, data={"Name": "Updated Item"})

# DELETE requests
batch.add_delete(endpoint)
```

### Processing Results

`BatchResult` contains:

| Property | Type | Description |
|----------|------|-------------|
| `status_code` | `int` | HTTP status code (200, 201, 404, etc.) |
| `data` | `dict \| None` | Response data for successful requests |
| `error` | `str \| None` | Error message for failed requests |
| `success` | `bool` | `True` if status_code < 400 |

### When to Use Batch

- **Good for**: Creating/updating multiple related records, fetching data from multiple endpoints
- **Not for**: Large data retrieval (use Sync API instead), operations that need individual error handling

## Working with Lines

Order lines (and similar child entities) are separate API resources. They're linked to their parent by a GUID.

```python
# Get lines for a specific order
result = await client.purchase_order_lines.list(
    division=123,
    odata_filter=f"PurchaseOrderID eq guid'{order.purchase_order_id}'",
)

for line in result:
    print(f"Item: {line.item}, Qty: {line.quantity}")

# Create a line on an existing order
new_line = await client.purchase_order_lines.create(
    division=123,
    data={
        "PurchaseOrderID": "order-guid",
        "Item": "item-guid",
        "Quantity": 5,
    },
)
```

## Rate Limiting

Exact Online enforces rate limits of 60 requests per minute per division. The SDK automatically tracks rate limits from response headers and waits when approaching the limit—you don't need to handle this yourself.

> **Source**: [Exact Online API Limits](https://support.exactonline.com/community/s/knowledge-base#All-All-DNO-Simulation-gen-apilimits)

## Retry Logic

The SDK includes automatic retry logic for transient failures. By default, it retries on:

- Network errors (connection failures, timeouts)
- Server errors (5xx responses)
- Rate limit errors (429)

### Default Behavior

Retry is enabled by default with sensible settings:

```python
async with ExactOnlineClient(oauth=oauth) as client:
    # Automatically retries on transient failures
    orders = await client.purchase_orders.list(division=123)
```

### Custom Retry Configuration

You can customize retry behavior:

```python
from exact_online.retry import RetryConfig

# More aggressive retries
config = RetryConfig(
    max_retries=5,           # Max retry attempts (default: 3)
    base_delay=1.0,          # Initial delay in seconds (default: 0.5)
    max_delay=60.0,          # Maximum delay cap (default: 30.0)
    exponential_base=2.0,    # Exponential backoff multiplier (default: 2.0)
    jitter=True,             # Add randomness to prevent thundering herd (default: True)
)

async with ExactOnlineClient(oauth=oauth, retry_config=config) as client:
    orders = await client.purchase_orders.list(division=123)
```

### Disabling Retries

```python
async with ExactOnlineClient(oauth=oauth, retry_config=None) as client:
    # No automatic retries
    orders = await client.purchase_orders.list(division=123)
```

### What Gets Retried

| Error Type | Retried? |
|------------|----------|
| Network timeout | ✓ |
| Connection error | ✓ |
| 5xx server error | ✓ |
| 429 rate limit | ✓ |
| 4xx client error | ✗ |
| Authentication error | ✗ |

## Connection Pooling

The SDK uses `httpx` for HTTP requests, which maintains a connection pool by default. You can customize the timeout:

```python
async with ExactOnlineClient(oauth=oauth, timeout=60.0) as client:
    # Requests have a 60-second timeout (default is 30)
    orders = await client.purchase_orders.list(division=123)
```

For advanced connection pool configuration, provide your own `httpx.AsyncClient`:

```python
import httpx

http_client = httpx.AsyncClient(
    timeout=60.0,
    limits=httpx.Limits(
        max_connections=100,
        max_keepalive_connections=20,
    ),
)

async with ExactOnlineClient(oauth=oauth, http_client=http_client) as client:
    orders = await client.purchase_orders.list(division=123)

# Remember to close your custom client when done
await http_client.aclose()
```

## API Restrictions

Beyond rate limits, Exact Online enforces several restrictions you should be aware of.

> **Source**: [REST API Restrictions](https://support.exactonline.com/community/s/knowledge-base#All-All-DNO-Content-rest-restrictions)

### Sequential Requests Only

Do not use multi-threaded or parallel requests. Exact Online expects requests to be made sequentially. Attempting to speed up data retrieval with concurrent requests violates their Fair Use Policy and may result in your access being suspended.

### Pagination Limits

Standard CRUD endpoints return a maximum of 60 records per request. For larger datasets, use pagination with `list_next()` or—preferably—the Sync API with timestamps. The Sync API is specifically designed for bulk data retrieval without violating fair use policies.

### Content Length Limits

The maximum request/response size depends on your region:

- **Netherlands & Belgium**: 38 MB
- **All other regions**: 9.5 MB

### URL Length Limits

URLs are limited to 6000 characters. Be careful with complex OData filters, as URL encoding expands special characters (spaces become `%20`, etc.). A filter that looks short may exceed the limit after encoding.

## Error Handling

The SDK raises specific exceptions for different failure modes, allowing you to handle each case appropriately.

```python
from exact_online import (
    ExactOnlineError,      # Base exception for all SDK errors
    AuthenticationError,   # Auth/authorization failures
    TokenExpiredError,     # Refresh token expired, user must re-auth
    TokenRefreshError,     # Token refresh failed for other reasons
    RateLimitError,        # Rate limit exceeded
    APIError,              # API returned an error (has status_code)
)
```

Example error handling:

```python
try:
    orders = await client.purchase_orders.list(division=123)
except TokenExpiredError:
    # Refresh token is invalid/expired
    # Redirect user to re-authenticate
    redirect_to_login()
except RateLimitError:
    # Shouldn't happen often as SDK auto-waits
    # But handle just in case
    await asyncio.sleep(60)
except APIError as e:
    # API returned an error response
    print(f"API error {e.status_code}: {e}")
```

## Important Notes

**Token Expiry Timezone**: The SDK uses UTC for all datetime operations. When implementing `TokenStorage`, store `expires_at` as a timezone-aware datetime in UTC. Using naive datetimes or local times will cause token refresh logic to fail.

**Field Names**: When creating or updating records, use Exact Online's PascalCase field names (e.g., `PurchaseOrderID`, not `purchase_order_id`). The SDK's Pydantic models use snake_case for Python, but the API expects PascalCase.

## Available Resources

| Resource | Endpoint | CRUD | Sync | Documentation |
|----------|----------|------|------|---------------|
| Me (Current User) | `client.me` | — | — | [Docs](https://start.exactonline.nl/docs/HlpRestAPIResourcesDetails.aspx?name=SystemSystemMe) |
| Accounts | `client.accounts` | ✓ | ✓ | [Docs](https://start.exactonline.nl/docs/HlpRestAPIResourcesDetails.aspx?name=CRMAccounts) |
| Bill of Material Materials | `client.bill_of_material_materials` | ✓ | — | [Docs](https://start.exactonline.nl/docs/HlpRestAPIResourcesDetails.aspx?name=ManufacturingBillOfMaterialMaterials) |
| Item Extra Fields | `client.item_extra_fields` | Custom | — | [Docs](https://start.exactonline.nl/docs/HlpRestAPIResourcesDetails.aspx?name=ReadLogisticsItemExtraField) |
| Item Warehouses | `client.item_warehouses` | ✓ | — | [Docs](https://start.exactonline.nl/docs/HlpRestAPIResourcesDetails.aspx?name=InventoryItemWarehouses) |
| Items | `client.items` | ✓ | ✓ | [Docs](https://start.exactonline.nl/docs/HlpRestAPIResourcesDetails.aspx?name=LogisticsItems) |
| Payables List | `client.payables_list` | ✓ | — | [Docs](https://start.exactonline.nl/docs/HlpRestAPIResourcesDetails.aspx?name=ReadFinancialPayablesList) |
| Purchase Invoices | `client.purchase_invoices` | ✓ | — | [Docs](https://start.exactonline.nl/docs/HlpRestAPIResourcesDetails.aspx?name=PurchasePurchaseInvoices) |
| Purchase Item Prices | `client.purchase_item_prices` | — | ✓ | [Docs](https://start.exactonline.nl/docs/HlpRestAPIResourcesDetails.aspx?name=SyncLogisticsPurchaseItemPrices) |
| Purchase Order Lines | `client.purchase_order_lines` | ✓ | — | [Docs](https://start.exactonline.nl/docs/HlpRestAPIResourcesDetails.aspx?name=PurchaseOrderPurchaseOrderLines) |
| Purchase Orders | `client.purchase_orders` | ✓ | ✓ | [Docs](https://start.exactonline.nl/docs/HlpRestAPIResourcesDetails.aspx?name=PurchaseOrderPurchaseOrders) |
| Receivables List | `client.receivables_list` | ✓ | — | [Docs](https://start.exactonline.nl/docs/HlpRestAPIResourcesDetails.aspx?name=ReadFinancialReceivablesList) |
| Reporting Balance | `client.reporting_balance` | ✓ | — | [Docs](https://start.exactonline.nl/docs/HlpRestAPIResourcesDetails.aspx?name=FinancialReportingBalance) |
| Sales Item Prices | `client.sales_item_prices` | ✓ | — | [Docs](https://start.exactonline.nl/docs/HlpRestAPIResourcesDetails.aspx?name=LogisticsSalesItemPrices) |
| Sales Orders | `client.sales_orders` | ✓ | ✓ | [Docs](https://start.exactonline.nl/docs/HlpRestAPIResourcesDetails.aspx?name=SalesOrderSalesOrders) |
| Shop Orders | `client.shop_orders` | ✓ | ✓ | [Docs](https://start.exactonline.nl/docs/HlpRestAPIResourcesDetails.aspx?name=ManufacturingShopOrders) |
| Stock Count Lines | `client.stock_count_lines` | ✓ | — | [Docs](https://start.exactonline.nl/docs/HlpRestAPIResourcesDetails.aspx?name=InventoryStockCountLines) |
| Supplier Items | `client.supplier_items` | ✓ | — | [Docs](https://start.exactonline.nl/docs/HlpRestAPIResourcesDetails.aspx?name=LogisticsSupplierItem) |
| Warehouse Transfers | `client.warehouse_transfers` | ✓ | — | [Docs](https://start.exactonline.nl/docs/HlpRestAPIResourcesDetails.aspx?name=InventoryWarehouseTransfers) |

### Special Endpoints

#### Item Extra Fields (Function Endpoint)

The Item Extra Fields API is a function endpoint that requires specific parameters. Unlike standard CRUD endpoints, it only supports a `get_for_item()` method:

```python
from datetime import datetime

# Get extra fields for a specific item
fields = await client.item_extra_fields.get_for_item(
    division=123,
    item_id="item-guid",
    modified=datetime(2024, 1, 1)  # Item's modified date
)

for field in fields:
    print(f"FreeField{field.number}: {field.value}")
```

#### Purchase Item Prices (Sync-Only)

The Purchase Item Prices API only supports bulk sync operations—no CRUD operations are available. Use `sync()` to retrieve purchase prices:

```python
# Initial sync (get all purchase item prices)
result = await client.purchase_item_prices.sync(division=123, timestamp=1)

# Incremental sync (get changes since last sync)
result = await client.purchase_item_prices.sync(
    division=123,
    timestamp=stored_timestamp
)

for price in result.items:
    print(f"{price.item_code}: {price.price} {price.currency}")
```

> **Note**: Use `timestamp=1` for the first sync (not 0). Only timestamp filtering is supported for optimal performance.

## Development

### Running Tests

The SDK includes a comprehensive test suite using pytest with async support and HTTP mocking.

```bash
# Install dev dependencies
uv sync --group dev

# Run all tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=exact_online
```

### Code Quality

The SDK enforces strict type checking and linting.

```bash
# Run linter
uv run ruff check src/ tests/

# Run type checker
uv run mypy src/ tests/
```

Both should pass with no errors.
