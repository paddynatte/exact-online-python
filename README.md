# Exact Online SDK Reference

Internal SDK for the Exact Online API. This document serves as a complete reference for integrating with Exact Online in our Litestar + Ariadne GraphQL backend.

---

## Quick Reference

### Available Client Properties

```python
client.me                    # Current user info
client.purchase_orders       # /purchaseorder/PurchaseOrders
client.purchase_order_lines  # /purchaseorder/PurchaseOrderLines
client.sales_orders          # /salesorder/SalesOrders
client.shop_orders           # /manufacturing/ShopOrders
client.warehouse_transfers   # /inventory/WarehouseTransfers
client.goods_receipts        # /purchaseorder/GoodsReceipts
client.goods_receipt_lines   # /purchaseorder/GoodsReceiptLines
client.stock_counts          # /inventory/StockCounts
client.stock_count_lines     # /inventory/StockCountLines
```

### All APIs Support These Methods

```python
# List with pagination (returns ListResult with .items and .next_url)
result = await client.<api>.list(division, odata_filter=None, select=None, top=None)

# Auto-paginate through all results (async generator)
async for item in client.<api>.list_all(division, odata_filter=None, select=None):
    ...

# Get single record by ID
item = await client.<api>.get(division, id="guid-string")

# Create new record (pass snake_case data, auto-converts to PascalCase)
item = await client.<api>.create(division, data={...})

# Update existing record
item = await client.<api>.update(division, id="guid-string", data={...})

# Delete record
await client.<api>.delete(division, id="guid-string")
```

---

## Setup

### 1. Token Storage Implementation

```python
# app/exact/storage.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from exact_online import TokenData


class ExactTokenStorage:
    """Implement this to persist OAuth tokens in your database."""
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_tokens(self) -> TokenData | None:
        result = await self.session.execute(select(ExactToken).limit(1))
        row = result.scalar_one_or_none()
        if row:
            return TokenData(
                access_token=row.access_token,
                refresh_token=row.refresh_token,
                expires_at=row.expires_at,  # MUST be timezone-aware UTC!
            )
        return None

    async def save_tokens(self, tokens: TokenData) -> None:
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
```

### 2. Client Setup

```python
# app/exact/client.py
from exact_online import Client, OAuth
from app.exact.storage import ExactTokenStorage

exact_client: Client | None = None


async def init_exact_client(session):
    """Call in app lifespan startup."""
    global exact_client
    
    storage = ExactTokenStorage(session)
    oauth = OAuth(
        client_id="your-client-id",
        client_secret="your-client-secret",
        redirect_uri="https://yourapp.com/exact/callback",
        token_storage=storage,
    )
    
    exact_client = Client(oauth)
    await exact_client.start()


async def close_exact_client():
    """Call in app lifespan shutdown."""
    global exact_client
    if exact_client:
        await exact_client.stop()
        exact_client = None


def get_exact_client() -> Client:
    """Get client for adding to GraphQL context."""
    if exact_client is None:
        raise RuntimeError("Exact client not initialized")
    return exact_client
```

### 3. Lifespan Integration

```python
# app/main.py
from contextlib import asynccontextmanager
from litestar import Litestar
from app.exact.client import init_exact_client, close_exact_client


@asynccontextmanager
async def lifespan(app: Litestar):
    session = ...  # your database session
    await init_exact_client(session)
    yield
    await close_exact_client()
```

### 4. GraphQL Context Setup

```python
# In your Ariadne/GraphQL setup
from app.exact.client import get_exact_client

def get_context_value(request):
    """Build GraphQL context with Exact client."""
    return {
        "request": request,
        "exact": get_exact_client(),  # Exact Online client in context
    }
```

**Accessing in resolvers:**
```python
# info.context["exact"] gives you the Client instance
client = info.context["exact"]
```

### 5. OAuth Callback Endpoint

```python
# app/routes/exact.py
from litestar import get
from app.exact.client import get_exact_client


@get("/exact/callback")
async def exact_callback(code: str) -> dict:
    """Exact Online redirects here after user authorizes."""
    client = get_exact_client()
    await client.oauth.exchange(code)
    return {"ok": True}
```

**OAuth Authorization URL:**
```
https://start.exactonline.nl/api/oauth2/auth?client_id=YOUR_CLIENT_ID&redirect_uri=YOUR_REDIRECT_URI&response_type=code
```

---

## Data Conversion Rules

### Writing Data (GraphQL → Exact Online)
- Pass data in **snake_case** (e.g., `purchase_order_lines`, `warehouse_from`)
- SDK automatically converts to **PascalCase** for Exact Online API
- Nested objects are also converted recursively

### Reading Data (Exact Online → GraphQL)
- SDK returns **Pydantic models** with snake_case attributes
- Ariadne serializes these directly
- Use `convert_case` in Ariadne schema for snake_case → camelCase to frontend

### Example
```python
# Writing - pass snake_case
await client.purchase_orders.create(division, data={
    "supplier": "guid",
    "purchase_order_lines": [
        {"item": "guid", "quantity": 10}
    ]
})
# SDK sends: {"Supplier": "guid", "PurchaseOrderLines": [{"Item": "guid", "Quantity": 10}]}

# Reading - receive Pydantic model with snake_case
order = await client.purchase_orders.get(division, id="guid")
print(order.supplier)  # UUID
print(order.purchase_order_lines)  # list[PurchaseOrderLine]
```

---

## Entity Reference

### Me (Current User)

```python
me = await client.me.current()
```

**Fields:**
- `user_id: UUID` - User ID
- `user_name: str` - User name
- `full_name: str` - Full name
- `email: str` - Email address
- `current_division: int` - Active division ID (use this for all API calls)
- `division_customer_name: str` - Company name

---

### Purchase Orders

**Endpoint:** `/purchaseorder/PurchaseOrders`  
**ID Field:** `PurchaseOrderID`

```python
# List
orders = await client.purchase_orders.list(division)

# Get
order = await client.purchase_orders.get(division, id="guid")

# Create
order = await client.purchase_orders.create(division, data={
    "supplier": "supplier-guid",  # Required
    "description": "Order description",
    "order_date": "2024-01-15",
    "receipt_date": "2024-01-20",
    "warehouse": "warehouse-guid",
    "purchase_order_lines": [
        {
            "item": "item-guid",
            "quantity": 10,
            "unit_price": 25.50,
        }
    ]
})

# Update
order = await client.purchase_orders.update(division, id="guid", data={
    "description": "Updated description"
})

# Delete
await client.purchase_orders.delete(division, id="guid")
```

**Key Fields:**
- `purchase_order_id: UUID`
- `order_number: int`
- `supplier: UUID`
- `supplier_name: str`
- `description: str`
- `order_date: datetime`
- `receipt_date: datetime`
- `receipt_status: int` (10=Open, 20=Partial, 50=Complete)
- `approval_status: int`
- `amount_dc: float` (amount in default currency)
- `warehouse: UUID`
- `purchase_order_lines: list[PurchaseOrderLine]`

---

### Purchase Order Lines

**Endpoint:** `/purchaseorder/PurchaseOrderLines`  
**ID Field:** `ID`

```python
# List lines for a specific order
lines = await client.purchase_order_lines.list(
    division,
    odata_filter=f"PurchaseOrderID eq guid'{order_id}'"
)

# Update a specific line
line = await client.purchase_order_lines.update(division, id="line-guid", data={
    "quantity": 20,
    "unit_price": 30.00
})

# Create additional line
line = await client.purchase_order_lines.create(division, data={
    "purchase_order_id": "order-guid",
    "item": "item-guid",
    "quantity": 5,
    "unit_price": 15.00
})

# Delete line
await client.purchase_order_lines.delete(division, id="line-guid")
```

**Key Fields:**
- `id: UUID`
- `purchase_order_id: UUID`
- `line_number: int`
- `item: UUID`
- `item_code: str`
- `item_description: str`
- `quantity: float`
- `unit_price: float`
- `amount_dc: float`
- `receipt_date: datetime`
- `quantity_received: float`

---

### Sales Orders

**Endpoint:** `/salesorder/SalesOrders`  
**ID Field:** `OrderID`

```python
# Create
order = await client.sales_orders.create(division, data={
    "ordered_by": "customer-guid",  # Required
    "description": "Sales order",
    "sales_order_lines": [
        {
            "item": "item-guid",
            "quantity": 5,
            "unit_price": 100.00
        }
    ]
})
```

**Status Values:**
- 12 = Open
- 20 = Partial
- 21 = Complete
- 45 = Cancelled

**Key Fields:**
- `order_id: UUID`
- `order_number: int`
- `ordered_by: UUID` (customer)
- `ordered_by_name: str`
- `order_date: datetime`
- `delivery_date: datetime`
- `status: int`
- `amount_dc: float`
- `sales_order_lines: list[SalesOrderLine]`

---

### Shop Orders

**Endpoint:** `/manufacturing/ShopOrders`  
**ID Field:** `ID`

```python
# Create
order = await client.shop_orders.create(division, data={
    "item": "item-guid",  # Required - item to manufacture
    "planned_quantity": 100,
    "planned_start_date": "2024-01-15",
})
```

**Status Values:**
- 10 = Open
- 20 = In process
- 30 = Finished
- 40 = Completed

**Key Fields:**
- `id: UUID`
- `shop_order_number: int`
- `item: UUID`
- `item_code: str`
- `item_description: str`
- `planned_quantity: float`
- `produced_quantity: float`
- `status: int`
- `planned_start_date: datetime`
- `planned_end_date: datetime`

---

### Warehouse Transfers

**Endpoint:** `/inventory/WarehouseTransfers`  
**ID Field:** `TransferID`

```python
# Create warehouse transfer
transfer = await client.warehouse_transfers.create(division, data={
    "warehouse_from": "from-warehouse-guid",
    "warehouse_to": "to-warehouse-guid",
    "description": "Transfer description",
    "warehouse_transfer_lines": [
        {
            "item": "item-guid",
            "quantity": 50
        }
    ]
})

# Location transfer (same warehouse, different locations)
transfer = await client.warehouse_transfers.create(division, data={
    "warehouse_from": "warehouse-guid",
    "warehouse_to": "warehouse-guid",  # Same warehouse
    "storage_location_from": "location-a-guid",
    "storage_location_to": "location-b-guid",
    "warehouse_transfer_lines": [...]
})
```

**Key Fields:**
- `transfer_id: UUID`
- `transfer_number: int`
- `warehouse_from: UUID`
- `warehouse_to: UUID`
- `storage_location_from: UUID`
- `storage_location_to: UUID`
- `transfer_date: datetime`
- `description: str`
- `warehouse_transfer_lines: list[WarehouseTransferLine]`

---

### Goods Receipts

**Endpoint:** `/purchaseorder/GoodsReceipts`  
**ID Field:** `ID`

Records receipt of goods from purchase orders.

```python
# Create goods receipt (required: receipt_date + goods_receipt_lines)
receipt = await client.goods_receipts.create(division, data={
    "receipt_date": "2024-01-15",  # Required
    "supplier": "supplier-guid",
    "warehouse": "warehouse-guid",
    "description": "Goods receipt for PO 12345",
    "goods_receipt_lines": [  # Required
        {
            "item": "item-guid",
            "quantity_received": 10,
            "purchase_order_id": "po-guid",
            "purchase_order_line_id": "po-line-guid"
        }
    ]
})

# List receipts for a supplier
receipts = await client.goods_receipts.list(
    division,
    odata_filter=f"Supplier eq guid'{supplier_id}'"
)
```

**Key Fields:**
- `id: UUID`
- `receipt_number: int`
- `receipt_date: datetime` (required for create)
- `supplier: UUID`
- `supplier_name: str`
- `warehouse: UUID`
- `warehouse_code: str`
- `description: str`
- `remarks: str`
- `goods_receipt_lines: list[GoodsReceiptLine]` (required for create)
- `created: datetime`
- `modified: datetime`

---

### Goods Receipt Lines

**Endpoint:** `/purchaseorder/GoodsReceiptLines`  
**ID Field:** `ID`

```python
# List lines for a specific receipt
lines = await client.goods_receipt_lines.list(
    division,
    odata_filter=f"GoodsReceiptID eq guid'{receipt_id}'"
)
```

**Key Fields:**
- `id: UUID`
- `goods_receipt_id: UUID`
- `item: UUID`
- `item_code: str`
- `item_description: str`
- `quantity_ordered: float`
- `quantity_received: float`
- `purchase_order_id: UUID`
- `purchase_order_line_id: UUID`
- `purchase_order_number: int`
- `location: UUID`
- `location_code: str`

---

### Stock Counts

**Endpoint:** `/inventory/StockCounts`  
**ID Field:** `StockCountID`

Used for inventory counting/adjustments.

```python
# Create stock count (required: warehouse, stock_count_date, stock_count_lines)
count = await client.stock_counts.create(division, data={
    "warehouse": "warehouse-guid",  # Required
    "stock_count_date": "2024-01-15",  # Required
    "status": 12,  # 12 = Open (draft), 21 = Processed
    "description": "Monthly inventory count",
    "stock_count_lines": [  # Required
        {
            "item": "item-guid",
            "quantity_new": 100,  # The counted quantity
            "storage_location": "location-guid"
        }
    ]
})

# List draft counts
counts = await client.stock_counts.list(
    division,
    odata_filter="Status eq 12"
)
```

**Status Values:**
- 12 = Open (draft) - can still be edited
- 21 = Processed - inventory updated, cannot edit

**Key Fields:**
- `stock_count_id: UUID`
- `stock_count_number: int`
- `stock_count_date: datetime` (required)
- `warehouse: UUID` (required)
- `warehouse_code: str`
- `status: int`
- `description: str`
- `counted_by: UUID`
- `stock_count_lines: list[StockCountLine]` (required for create)
- `created: datetime`
- `modified: datetime`

---

### Stock Count Lines

**Endpoint:** `/inventory/StockCountLines`  
**ID Field:** `ID`

```python
# List lines for a specific count
lines = await client.stock_count_lines.list(
    division,
    odata_filter=f"StockCountID eq guid'{count_id}'"
)

# Update a counted quantity
line = await client.stock_count_lines.update(division, id="line-guid", data={
    "quantity_new": 150
})
```

**Key Fields:**
- `id: UUID`
- `stock_count_id: UUID`
- `item: UUID`
- `item_code: str`
- `item_description: str`
- `quantity_in_stock: float` - System quantity before count
- `quantity_new: float` - Counted quantity
- `quantity_difference: float` - Calculated difference
- `storage_location: UUID`
- `storage_location_code: str`
- `batch_number: str`
- `serial_number: str`
- `cost_price: float`

---

## Filtering with OData

Use `odata_filter` parameter for filtering:

```python
# Exact match
odata_filter="Status eq 12"

# GUID comparison
odata_filter=f"Supplier eq guid'{supplier_id}'"

# String comparison
odata_filter="SupplierName eq 'Acme Corp'"

# Numeric comparison
odata_filter="Quantity gt 100"

# Date comparison
odata_filter="OrderDate ge datetime'2024-01-01'"

# Combine with and/or
odata_filter="Status eq 12 and Quantity gt 0"

# String contains (substringof)
odata_filter="substringof('keyword', Description)"
```

---

## Batching Multiple Requests

Combine multiple GET requests into a single HTTP call:

```python
from exact_online import BatchRequest

result = await client.batch([
    BatchRequest("GET", "/purchaseorder/PurchaseOrders", division),
    BatchRequest("GET", "/salesorder/SalesOrders", division),
    BatchRequest("GET", "/manufacturing/ShopOrders", division),
])

for response in result:
    if response.is_success:
        print(response.data)  # Response JSON
    else:
        print(f"Error {response.status_code}: {response.error}")
```

---

## Error Handling

```python
from exact_online import APIError, RateLimitError, AuthenticationError

try:
    orders = await client.purchase_orders.list(division)
except AuthenticationError:
    # Token expired/invalid - redirect user to OAuth
    pass
except RateLimitError:
    # Rate limit exceeded (SDK retries automatically, this means retries exhausted)
    pass
except APIError as e:
    # Other API errors
    print(f"Error {e.status_code}: {e.message}")
```

---

## GraphQL Resolver Examples

All resolvers access the Exact client via `info.context["exact"]`.

### Query - List with Filter

```python
@query.field("purchaseOrders")
async def resolve_purchase_orders(_, info, status: int | None = None):
    client = info.context["exact"]
    me = await client.me.current()
    
    odata_filter = f"ReceiptStatus eq {status}" if status else None
    
    result = await client.purchase_orders.list(
        division=me.current_division,
        odata_filter=odata_filter,
    )
    
    return result.items
```

### Query - Get Single

```python
@query.field("purchaseOrder")
async def resolve_purchase_order(_, info, id: str):
    client = info.context["exact"]
    me = await client.me.current()
    
    return await client.purchase_orders.get(
        division=me.current_division,
        id=id,
    )
```

### Mutation - Create

```python
@mutation.field("createPurchaseOrder")
async def resolve_create_purchase_order(_, info, input: dict):
    client = info.context["exact"]
    me = await client.me.current()
    
    return await client.purchase_orders.create(
        division=me.current_division,
        data=input,  # Pass snake_case from GraphQL input
    )
```

### Mutation - Update

```python
@mutation.field("updatePurchaseOrderLine")
async def resolve_update_line(_, info, id: str, input: dict):
    client = info.context["exact"]
    me = await client.me.current()
    
    return await client.purchase_order_lines.update(
        division=me.current_division,
        id=id,
        data=input,
    )
```

### Mutation - Delete

```python
@mutation.field("deletePurchaseOrder")
async def resolve_delete(_, info, id: str):
    client = info.context["exact"]
    me = await client.me.current()
    
    await client.purchase_orders.delete(
        division=me.current_division,
        id=id,
    )
    
    return True
```

### Mutation - Create Goods Receipt

```python
@mutation.field("createGoodsReceipt")
async def resolve_create_receipt(_, info, input: dict):
    client = info.context["exact"]
    me = await client.me.current()
    
    return await client.goods_receipts.create(
        division=me.current_division,
        data={
            "receipt_date": input["receiptDate"],
            "supplier": input.get("supplierId"),
            "warehouse": input.get("warehouseId"),
            "goods_receipt_lines": [
                {
                    "item": line["itemId"],
                    "quantity_received": line["quantity"],
                    "purchase_order_id": line.get("purchaseOrderId"),
                    "purchase_order_line_id": line.get("purchaseOrderLineId"),
                }
                for line in input["lines"]
            ]
        }
    )
```

### Mutation - Create Stock Count

```python
@mutation.field("createStockCount")
async def resolve_create_stock_count(_, info, input: dict):
    client = info.context["exact"]
    me = await client.me.current()
    
    return await client.stock_counts.create(
        division=me.current_division,
        data={
            "warehouse": input["warehouseId"],
            "stock_count_date": input["date"],
            "status": 12,  # Draft
            "description": input.get("description"),
            "stock_count_lines": [
                {
                    "item": line["itemId"],
                    "quantity_new": line["countedQuantity"],
                    "storage_location": line.get("locationId"),
                }
                for line in input["lines"]
            ]
        }
    )
```

---

## Important Notes

1. **Token Storage is Critical** - Exact Online rotates refresh tokens on every use. If you don't save the new token after each refresh, you permanently lose access and must re-authorize.

2. **expires_at Must Be UTC** - Store as timezone-aware UTC datetime, never naive datetime.

3. **Division is Required** - Every API call needs a division ID. Get it from `client.me.current().current_division`.

4. **Pydantic Models Work with Ariadne** - Return models directly from resolvers. Use `convert_case` in your Ariadne schema for automatic snake_case → camelCase conversion.

5. **Exact Online is Source of Truth** - We read/write directly to Exact's API. Only OAuth tokens are stored locally.

6. **Rate Limits** - SDK handles rate limiting automatically with retries. 60 requests/minute per division.
