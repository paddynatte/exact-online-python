# exact-online-python

A Python SDK for the Exact Online API. Async-first, fully typed, with automatic token refresh, rate limiting, retry logic, and webhook support.

## Contents

- [Installation](#installation)
- [Development](#development)
- [Quick start](#quick-start)
- [Authentication](#authentication)
- [Regions](#regions)
- [Usage](#usage)
- [Rate limiting](#rate-limiting)
- [Retry logic](#retry-logic)
- [Connection pooling](#connection-pooling)
- [Restrictions](#restrictions)
- [Errors](#errors)
- [Resources](#resources)
- [Notes](#notes)

## Installation

```bash
pip install exact-online-python
```

Requires Python 3.13+.

## Development

Install dev dependencies and run tests:

```bash
uv sync --group dev
uv run pytest tests/ -v
uv run pytest tests/ --cov=exact_online
```

Run linter and type checker:

```bash
uv run ruff check src/ tests/
uv run mypy src/ tests/
```

## Quick start

The SDK requires you to implement token storage yourself. This keeps the SDK lean and lets you use whatever persistence layer you prefer.

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

Exact Online uses OAuth 2.0. Access tokens expire after 10 minutes, and the SDK refreshes them automatically 30 seconds before expiry to prevent race conditions.

Exact Online uses rotating refresh tokens. When you refresh an access token, you also receive a new refresh token, and the previous one is immediately invalidated. If you don't persist the new tokens, you lose access and the user must re-authenticate. This is why the SDK requires you to implement `TokenStorage`. For more details, see the [Exact Online OAuth Documentation](https://support.exactonline.com/community/s/knowledge-base#All-All-DNO-Content-oauth-eol-oauth-dev-impleovervw).

### Initial authorization

Your application handles the OAuth redirect flow. The SDK provides helpers to generate the authorization URL and exchange the code for tokens.

Generate the URL and redirect the user:

```python
url = oauth.get_authorization_url(state="csrf-token")
# Redirect user to this URL
```

After the user authorizes your app, Exact Online redirects them back with a code. Exchange it for tokens:

```python
tokens = await oauth.exchange_code(authorization_code)
# Tokens are automatically saved via your TokenStorage
```

### Token refresh

The SDK refreshes tokens automatically. If you need direct access to the current token:

```python
access_token = await oauth.ensure_valid_token()
```

## Regions

Exact Online operates separate instances per region, each with its own API endpoint. Use the correct region for your account:

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

## Usage

All API methods require an explicit `division` parameter. A division represents a company/administration within Exact Online. This explicit approach prevents accidentally querying the wrong division when working with multiple companies. See the [Exact Online REST API Documentation](https://support.exactonline.com/community/s/knowledge-base#All-All-DNO-Content-gettingstarted) for more details.

### Listing records

The standard API returns up to 60 records per request. The `list()` method returns a `ListResult` that you can iterate directly:

```python
result = await client.purchase_orders.list(division=123)

for order in result:
    print(order.order_number)

print(f"Got {len(result)} orders")
```

Filter and select specific fields using OData query parameters:

```python
result = await client.purchase_orders.list(
    division=123,
    odata_filter="ReceiptStatus eq 10",
    select=["PurchaseOrderID", "Supplier", "OrderDate"],
    top=60,
)
```

The `odata_filter` parameter accepts standard OData filter expressions:

```python
odata_filter="ReceiptStatus eq 10"                              # Open orders only
odata_filter="Supplier eq guid'abc-123-def'"                    # Specific supplier
odata_filter="Created gt datetime'2024-01-01'"                  # After a date
odata_filter="ReceiptStatus eq 10 and Supplier eq guid'...'"    # Combined
```

### Pagination

When there are more than 60 records, use the `next_url` property to fetch subsequent pages. The SDK uses Exact Online's `__next` / `$skiptoken` mechanism for reliable pagination:

```python
result = await client.purchase_orders.list(division=123)
all_orders = list(result.items)

while result.next_url:
    result = await client.purchase_orders.list_next(result.next_url, division=123)
    all_orders.extend(result.items)

print(f"Total orders: {len(all_orders)}")
```

For convenience, use `list_all()` which handles pagination automatically:

```python
async for order in client.purchase_orders.list_all(division=123):
    print(order.order_number)
```

### Single records

Fetch a specific record by its GUID:

```python
order = await client.purchase_orders.get(
    division=123,
    id="abc-123-def-456",
)
```

### Creating records

Create new records by passing a dictionary with API field names (PascalCase, as Exact Online expects):

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

### Updating records

Update existing records by GUID. Only include the fields you want to change:

```python
updated = await client.purchase_orders.update(
    division=123,
    id="order-guid",
    data={"Remarks": "Updated via API"},
)
```

### Deleting records

Delete a record by GUID:

```python
await client.purchase_orders.delete(
    division=123,
    id="order-guid",
)
```

### Order lines

Order lines and similar child entities are separate API resources linked to their parent by a GUID:

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

### Sync API

Some entities support a bulk sync endpoint that returns up to 1000 records per request (compared to 60 for the standard API). The sync API uses timestamps for incremental syncing, so you only fetch records that changed since your last sync. See the [Exact Online Sync API Documentation](https://start.exactonline.nl/docs/HlpRestAPIResourcesDetails.aspx?name=ReadSyncSyncSyncTimestamp) for details.

Start with `timestamp=0` to fetch all records:

```python
result = await client.purchase_orders.sync(division=123, timestamp=0)

print(f"Fetched {len(result.items)} orders")
print(f"Next timestamp: {result.timestamp}")

# Store result.timestamp in your database for next sync
```

Use the timestamp from your last sync to only fetch modified records:

```python
result = await client.purchase_orders.sync(
    division=123,
    timestamp=stored_timestamp,
)

for order in result.items:
    # Process changed/new orders
    ...

stored_timestamp = result.timestamp
```

The `result.has_more` flag indicates if there are more records to fetch. Keep calling with the returned timestamp until `has_more` is `False`.

### Batch requests

The SDK supports Exact Online's `$batch` endpoint for combining multiple requests into a single HTTP call. This reduces round-trips when you need to perform multiple operations. See the [OData Batch Processing](https://www.odata.org/documentation/odata-version-3-0/batch-processing/) documentation for details.

```python
from exact_online.batch import BatchRequest

batch = BatchRequest(division=123)

batch.add_get("/purchaseorder/PurchaseOrders", params={"$top": "10"})
batch.add_get("/crm/Accounts", params={"$top": "5"})
batch.add_post("/crm/Accounts", {"Name": "New Customer"})

results = await client.execute_batch(batch)

for result in results:
    if result.success:
        print(f"Status {result.status_code}: {result.data}")
    else:
        print(f"Failed: {result.error}")
```

Available batch methods:

```python
batch.add_get(endpoint, params={"$filter": "Status eq 'Active'"})
batch.add_post(endpoint, data={"Name": "New Item"})
batch.add_put(endpoint, data={"Name": "Updated Item"})
batch.add_delete(endpoint)
```

`BatchResult` properties:

| Property | Type | Description |
|----------|------|-------------|
| `status_code` | `int` | HTTP status code (200, 201, 404, etc.) |
| `data` | `dict \| None` | Response data for successful requests |
| `error` | `str \| None` | Error message for failed requests |
| `success` | `bool` | `True` if status_code < 400 |

Use batch requests for creating/updating multiple related records or fetching data from multiple endpoints. For large data retrieval, use the Sync API instead.

### Webhooks

Webhooks allow Exact Online to push changes to your application in real-time instead of polling with `sync()`. When a record is created, updated, or deleted, Exact Online sends an HTTP POST to your endpoint. The SDK handles webhook validation and parsing. You are responsible for hosting the webhook endpoint (using FastAPI, Flask, etc.) and managing subscriptions via the Exact Online App Center.

`WebhookEvent` properties:

| Property | Type | Description |
|----------|------|-------------|
| `topic` | `str` | Entity type (e.g., "PurchaseOrders", "Accounts") |
| `action` | `str` | Change type: "Create", "Update", or "Delete" |
| `division` | `int` | Division ID where the change occurred |
| `key` | `str` | GUID of the affected entity |
| `endpoint` | `str \| None` | API endpoint to fetch the entity |
| `timestamp` | `datetime \| None` | When the change occurred |
| `hash_code` | `str \| None` | Exact Online's hash code |

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
        
        if event.topic == "PurchaseOrders":
            order = await client.purchase_orders.get(
                division=event.division,
                id=event.key,
            )
            # Process the order
            
        return {"status": "ok"}
        
    except WebhookValidationError:
        return {"error": "Invalid signature"}, 401
```

If you handle signature validation separately (e.g., in middleware), parse the payload directly:

```python
from exact_online.webhooks import parse_webhook

event = parse_webhook(payload)
```

For testing or manual signature verification:

```python
from exact_online.webhooks import compute_signature, verify_signature

expected = compute_signature(payload_bytes, webhook_secret)
is_valid = verify_signature(payload_bytes, received_signature, webhook_secret)
```

FastAPI example:

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
    except WebhookValidationError:
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    if event.topic == "PurchaseOrders":
        await handle_purchase_order(event)
    elif event.topic == "Accounts":
        await handle_account(event)
    
    return {"status": "ok"}
```

Use webhooks for real-time updates and the sync API for initial data loads or recovery. Most applications benefit from using both: webhooks keep you up-to-date in real-time, while sync provides a reliable way to backfill data or recover from missed webhooks.

## Rate limiting

Exact Online enforces rate limits of 60 requests per minute per division. The SDK tracks rate limits from response headers and waits automatically when approaching the limit. See the [Exact Online API Limits](https://support.exactonline.com/community/s/knowledge-base#All-All-DNO-Simulation-gen-apilimits) documentation for details.

## Retry logic

The SDK retries automatically on transient failures:

- Network errors (connection failures, timeouts)
- Server errors (5xx responses)
- Rate limit errors (429)

Retry is enabled by default:

```python
async with ExactOnlineClient(oauth=oauth) as client:
    orders = await client.purchase_orders.list(division=123)
```

Customize retry behavior:

```python
from exact_online.retry import RetryConfig

config = RetryConfig(
    max_retries=5,
    base_delay=1.0,
    max_delay=60.0,
    exponential_base=2.0,
    jitter=True,
)

async with ExactOnlineClient(oauth=oauth, retry_config=config) as client:
    orders = await client.purchase_orders.list(division=123)
```

| Parameter | Default | Description |
|-----------|---------|-------------|
| `max_retries` | 3 | Maximum retry attempts |
| `base_delay` | 0.5 | Initial delay in seconds |
| `max_delay` | 30.0 | Maximum delay cap |
| `exponential_base` | 2.0 | Backoff multiplier |
| `jitter` | True | Add randomness to prevent thundering herd |

Disable retries:

```python
async with ExactOnlineClient(oauth=oauth, retry_config=None) as client:
    orders = await client.purchase_orders.list(division=123)
```

| Error Type | Retried? |
|------------|----------|
| Network timeout | Yes |
| Connection error | Yes |
| 5xx server error | Yes |
| 429 rate limit | Yes |
| 4xx client error | No |
| Authentication error | No |

## Connection pooling

The SDK uses `httpx` for HTTP requests, which maintains a connection pool by default. Customize the timeout:

```python
async with ExactOnlineClient(oauth=oauth, timeout=60.0) as client:
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

await http_client.aclose()
```

## Restrictions

Beyond rate limits, Exact Online enforces several restrictions. See the [REST API Restrictions](https://support.exactonline.com/community/s/knowledge-base#All-All-DNO-Content-rest-restrictions) documentation for details.

**Sequential requests only**: Do not use multi-threaded or parallel requests. Exact Online expects requests to be made sequentially. Concurrent requests violate their Fair Use Policy and may result in suspended access.

**Pagination limits**: Standard CRUD endpoints return a maximum of 60 records per request. For larger datasets, use pagination with `list_next()` or the Sync API with timestamps.

**Content length limits**:

| Region | Max Size |
|--------|----------|
| Netherlands, Belgium | 38 MB |
| All other regions | 9.5 MB |

**URL length limits**: URLs are limited to 6000 characters. Be careful with complex OData filters, as URL encoding expands special characters (spaces become `%20`, etc.).

## Errors

The SDK raises specific exceptions for different failure modes:

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

Example:

```python
try:
    orders = await client.purchase_orders.list(division=123)
except TokenExpiredError:
    redirect_to_login()
except RateLimitError:
    await asyncio.sleep(60)
except APIError as e:
    print(f"API error {e.status_code}: {e}")
```

## Resources

| Resource | Endpoint | CRUD | Sync | Documentation |
|----------|----------|------|------|---------------|
| Me (Current User) | `client.me` | - | - | [Docs](https://start.exactonline.nl/docs/HlpRestAPIResourcesDetails.aspx?name=SystemSystemMe) |
| Accounts | `client.accounts` | Yes | Yes | [Docs](https://start.exactonline.nl/docs/HlpRestAPIResourcesDetails.aspx?name=CRMAccounts) |
| Bill of Material Materials | `client.bill_of_material_materials` | Yes | - | [Docs](https://start.exactonline.nl/docs/HlpRestAPIResourcesDetails.aspx?name=ManufacturingBillOfMaterialMaterials) |
| Item Extra Fields | `client.item_extra_fields` | Custom | - | [Docs](https://start.exactonline.nl/docs/HlpRestAPIResourcesDetails.aspx?name=ReadLogisticsItemExtraField) |
| Item Warehouses | `client.item_warehouses` | Yes | - | [Docs](https://start.exactonline.nl/docs/HlpRestAPIResourcesDetails.aspx?name=InventoryItemWarehouses) |
| Items | `client.items` | Yes | Yes | [Docs](https://start.exactonline.nl/docs/HlpRestAPIResourcesDetails.aspx?name=LogisticsItems) |
| Payables List | `client.payables_list` | Yes | - | [Docs](https://start.exactonline.nl/docs/HlpRestAPIResourcesDetails.aspx?name=ReadFinancialPayablesList) |
| Purchase Invoices | `client.purchase_invoices` | Yes | - | [Docs](https://start.exactonline.nl/docs/HlpRestAPIResourcesDetails.aspx?name=PurchasePurchaseInvoices) |
| Purchase Item Prices | `client.purchase_item_prices` | - | Yes | [Docs](https://start.exactonline.nl/docs/HlpRestAPIResourcesDetails.aspx?name=SyncLogisticsPurchaseItemPrices) |
| Purchase Order Lines | `client.purchase_order_lines` | Yes | - | [Docs](https://start.exactonline.nl/docs/HlpRestAPIResourcesDetails.aspx?name=PurchaseOrderPurchaseOrderLines) |
| Purchase Orders | `client.purchase_orders` | Yes | Yes | [Docs](https://start.exactonline.nl/docs/HlpRestAPIResourcesDetails.aspx?name=PurchaseOrderPurchaseOrders) |
| Receivables List | `client.receivables_list` | Yes | - | [Docs](https://start.exactonline.nl/docs/HlpRestAPIResourcesDetails.aspx?name=ReadFinancialReceivablesList) |
| Reporting Balance | `client.reporting_balance` | Yes | - | [Docs](https://start.exactonline.nl/docs/HlpRestAPIResourcesDetails.aspx?name=FinancialReportingBalance) |
| Sales Item Prices | `client.sales_item_prices` | Yes | - | [Docs](https://start.exactonline.nl/docs/HlpRestAPIResourcesDetails.aspx?name=LogisticsSalesItemPrices) |
| Sales Orders | `client.sales_orders` | Yes | Yes | [Docs](https://start.exactonline.nl/docs/HlpRestAPIResourcesDetails.aspx?name=SalesOrderSalesOrders) |
| Shop Orders | `client.shop_orders` | Yes | Yes | [Docs](https://start.exactonline.nl/docs/HlpRestAPIResourcesDetails.aspx?name=ManufacturingShopOrders) |
| Stock Count Lines | `client.stock_count_lines` | Yes | - | [Docs](https://start.exactonline.nl/docs/HlpRestAPIResourcesDetails.aspx?name=InventoryStockCountLines) |
| Supplier Items | `client.supplier_items` | Yes | - | [Docs](https://start.exactonline.nl/docs/HlpRestAPIResourcesDetails.aspx?name=LogisticsSupplierItem) |
| Warehouse Transfers | `client.warehouse_transfers` | Yes | - | [Docs](https://start.exactonline.nl/docs/HlpRestAPIResourcesDetails.aspx?name=InventoryWarehouseTransfers) |

### Item extra fields

The Item Extra Fields API is a function endpoint that requires specific parameters. Unlike standard CRUD endpoints, it only supports `get_for_item()`. See the [Item Extra Fields Documentation](https://start.exactonline.nl/docs/HlpRestAPIResourcesDetails.aspx?name=ReadLogisticsItemExtraField) for details.

```python
from datetime import datetime

fields = await client.item_extra_fields.get_for_item(
    division=123,
    item_id="item-guid",
    modified=datetime(2024, 1, 1)
)

for field in fields:
    print(f"FreeField{field.number}: {field.value}")
```

### Purchase item prices

The Purchase Item Prices API only supports bulk sync operations. See the [Purchase Item Prices Documentation](https://start.exactonline.nl/docs/HlpRestAPIResourcesDetails.aspx?name=SyncLogisticsPurchaseItemPrices) for details.

```python
result = await client.purchase_item_prices.sync(division=123, timestamp=0)

result = await client.purchase_item_prices.sync(
    division=123,
    timestamp=stored_timestamp
)

for price in result.items:
    print(f"{price.item_code}: {price.price} {price.currency}")
```

Only timestamp filtering is supported for optimal performance. Do not use `$select=*`.

## Notes

**Token expiry timezone**: The SDK uses UTC for all datetime operations. When implementing `TokenStorage`, store `expires_at` as a timezone-aware datetime in UTC. Using naive datetimes or local times will cause token refresh logic to fail.

**Field names**: When creating or updating records, use Exact Online's PascalCase field names (e.g., `PurchaseOrderID`, not `purchase_order_id`). The SDK's Pydantic models use snake_case for Python, but the API expects PascalCase.
