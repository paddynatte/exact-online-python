REST API – Business example API Goods delivery
This example can be implemented using the OAuth 2.0 authentication process. See Using OAuth 2.0 to access Exact Online API. You can find examples for setting up each API request in Make the request - REST.

The following scenarios are covered in this example:

Create a goods delivery for a sales order
Edit the created goods delivery
For more information on the Goods Delivery API, see Exact Online REST API - Reference information

Scenario
Your web shop, SportWorld, receives an online sales order from your customer Fittsport. The sales order number is 71, which is for the following items. After the stock check is completed and the sales order is approved, you will deliver all the items to Fittsport with a delivery date of 18 February 2016.

Items	Serial / Batch number	Quantity to be delivered
Sport watch	SW001, SW002	2
Protein Shake	B001	2
Training Shoes	Not applicable	2
For this transaction, a goods delivery note needs to be created and then updated with the correct tracking number.

The goods delivery API supports GET, POST and PUT (read, create and edit) and can be used by all wholesale users. However, assembly items are currently not supported. In this scenario, the JSON response is shown.

Step 1: Create the goods delivery for sales order
Retrieve the item information from sales order 71 and make sure the sales order has approval status 2, which means that it is approved. For the next steps, you need the line IDs and the quantity to be delivered for each line. Partial delivery is possible, but the quantity cannot exceed the remaining quantity (quantity minus quantity delivered) and must be greater than zero.

An unapproved sales order cannot be delivered.
GET REQUEST

../api/v1/{Division}/salesorder/SalesOrders?
$select=ApprovalStatus,ApprovalStatusDescription,
SalesOrderLines/ID,SalesOrderLines/Item, SalesOrderLines/ItemCode,SalesOrderLines/Quantity,SalesOrderLines/QuantityDelivered
&$filter=OrderNumber eq 71 
&$expand=SalesOrderLines
RESPONSE:

{"d": 
{"results": [1]
0:
{
"__metadata": 
{
"uri": "../api/v1/{Division}/salesorder/SalesOrders(guid'60ecbe5d-6e22-4aa4-a3b5-5caf8bf7fb4e')"
"type": "Exact.Web.Api.Models.SalesOrder"
}
"ApprovalStatus": 2
"ApprovalStatusDescription": "Approved"
"SalesOrderLines": 
{
"results": 
[3]
0:
	{
	"__metadata": 
	{
	"uri": 
"../api/v1/{Division}/salesorder/SalesOrderLines(guid'67381901-085b-4d4c-a86d-800a1ae919e8')"
	"type": "Exact.Web.Api.Models.SalesOrderLine"
	}
	"ID": "67381901-085b-4d4c-a86d-800a1ae919e8"
	"Item": "44d70d3a-d176-4a3d-9846-88812daf8bf3"
	"ItemCode": "PROTEINSHAKE"
	"Quantity": 2
	"QuantityDelivered": 0
	}
1:
	{
	"__metadata": 
	{
	"uri": 
"../api/v1/{Division}/salesorder/SalesOrderLines(guid'588d9cec-814c-4c98-bc4f-ab0cc89a27c7')"
	"type": "Exact.Web.Api.Models.SalesOrderLine"
	}
	"ID": "588d9cec-814c-4c98-bc4f-ab0cc89a27c7"
	"Item": "86e33a5f-8360-4a8e-9342-f6beecba0534"
	"ItemCode": "TRAININGSHOES"
	"Quantity": 2
	"QuantityDelivered": 0
	}
2:
	{"__metadata": 
	{
	"uri": 
"../api/v1/{Division}/salesorder/SalesOrderLines(guid'deea18bc-9c50-4d17-9d23-f3022886fe7a')"
	"type": "Exact.Web.Api.Models.SalesOrderLine"
	}
	"ID": "deea18bc-9c50-4d17-9d23-f3022886fe7a"
	"Item": "07247065-c4fb-4310-a3af-5df01d61fbff"
	"ItemCode": "SPORTWATCH"
	"Quantity": 2
	"QuantityDelivered": 0
}}}}}
In sales order 71, there is a batch item PROTEINSHAKE. To deliver this batch item, we need to enter the batch number into the goods delivery for tracking purposes. Let’s find out the batch number for this item.

Batch numbers must be enabled in an administration. For this reason, it is possible that no batch numbers are used.
GET REQUEST

../api/v1/{Division}/inventory/StockBatchNumbers?$select=BatchNumber,Quantity,EndDate&$filter=Item eq guid'44d70d3a-d176-4a3d-9846-88812daf8bf3’
RESPONSE:

{"d":
{"results": [1]
0: {"__metadata":
{"uri": "../api/v1/{Division}/inventory/StockBatchNumbers(guid'37fa3235-1965-40b0-822c-ffdef532b032')"
"type": "Exact.Web.Api.Models.Inventory.StockBatchNumber"
}


"BatchNumber": "B001"
"EndDate": null
"Quantity": 50
}}}
In sales order 71, there is also the serial item SPORTWATCH. Because every serial item has its own serial number, we need to fill in the serial number in the goods delivery for warranty purposes. Let’s find out the serial number for this item. If you know the serial number for the item, you can fill it into the goods delivery directly. Otherwise, we pick it from the response result.

GET REQUEST:

../api/v1/{Division}/inventory/StockSerialNumbers?$select=SerialNumber,EndDate&$filter=Item eq guid'07247065-c4fb-4310-a3af-5df01d61fbff'
RESPONSE:

{"d": 
{"results": [2]
0:
	{"__metadata": 
	{
	"uri": 
"../api/v1/{Division}/inventory/StockSerialNumbers?$select=SerialNumber,EndDate&$filter=Item eq guid'07247065-c4fb-4310-a3af-5df01d61fbff'"
	"type": "Exact.Web.Api.Models.Inventory.StockSerialNumber"
	}
	"EndDate": null
	"SerialNumber": "SW001"
	}
1:
	{"__metadata": 
	{
	"uri": 
"../api/v1/{Division}/inventory/StockSerialNumbers(guid'3a0a8df2-76ae-482f-ad1b-624f66fc84fa')"
	"type": "Exact.Web.Api.Models.Inventory.StockSerialNumber"
	}
	"EndDate": null
	"SerialNumber": "SW002"
	}
2:
	{"__metadata": 
	{
	"uri": 
"../api/v1/{Division}/inventory/StockSerialNumbers(guid'c0a5a9c0-fa7f-4894-8f2a-793383490022')"
	"type": "Exact.Web.Api.Models.Inventory.StockSerialNumber"
	}
	"EndDate": null
	"SerialNumber": "SW003"

}}}
Serial numbers must be enabled in an administration. For this reason, it is possible that no serial numbers are used.
The shipping method can be found in the sales order.
../api/v1/{Division}/ salesorder/SalesOrders
?$select=ShippingMethod, ShippingMethodDescription 
&$filter=OrderNumber eq 71 
If you would like to deliver the items from different warehouse storage locations, you can specify the storage location in the goods delivery lines. Otherwise the default warehouse’s storage location is entered. Exact for Wholesale Premium users can select a different storage location for delivery. You can find the different storage locations for a warehouse as shown below.
GET REQUEST:

../api/v1/{Division}/inventory/StorageLocations?$select=Code,Description,ID&$filter=WarehouseCode eq '1'
RESPONSE:

{"d"
	{"results": [1]
0:  
{"__metadata": 
{
"uri": "../api/v1/{Division}/inventory/StorageLocations(guid'c7684b36-9eac-4a5d-a157-4e3013fc2304')"
"type": "Exact.Web.Api.Models.Inventory.StorageLocation"
}
"Code": "1"
"Description": "Default location"
"ID": "c7684b36-9eac-4a5d-a157-4e3013fc2304"
}}}
Create the goods delivery. The delivery date, sales order IDs, and quantity to be delivered are mandatory in the POST request.
POST REQUEST:

../api/v1/{Division}/salesorder/GoodsDeliveries
RESPONSE:

{"DeliveryDate":"02/18/2016 00:00:00",
"Description":"Sports items delivery to FittSport BV",
"Remarks":"Sport items delivery on 18 Feb 2016 for SO 71",
"ShippingMethod":"b060b786-83cb-43a4-9f06-e21348f67412",
"TrackingNumber":"TR123456",
"GoodsDeliveryLines":
[
{
"Description": "Protein shake",
"Notes":"Batch No B001",
"QuantityDelivered":"2",
"SalesOrderLineID": "67381901-085b-4d4c-a86d-800a1ae919e8",
"TrackingNumber":" TR123456",
"BatchNumbers": [{"BatchNumber": "B001", "Quantity": 2}]
},
{
"Description": "Training shoes",
"Notes":"Shoes",
"QuantityDelivered":"2",
"SalesOrderLineID": "588d9cec-814c-4c98-bc4f-ab0cc89a27c7",
"TrackingNumber":" TR123456"
},
{
"Description": "Sport Watch",
"Notes":"Serial No SW001 & SW002",
"QuantityDelivered":"2",
"SalesOrderLineID": "deea18bc-9c50-4d17-9d23-f3022886fe7a",
"TrackingNumber":" TR123456",
"SerialNumbers": [{"SerialNumber": "SW001"}, {"SerialNumber": "SW002"}]
}]}	
Result: You should receive the response 201 Created. This response contains the URI of the goods delivery:

{"d": 
{"__metadata": 
{
"uri": "../api/v1/{Division}/salesorder/GoodsDeliveries(guid'80d81d4c-d57e-490c-9396-48958abca734')"
"type": "Exact.Web.Api.Models.SalesOrders.GoodsDelivery"
}
"DeliveryAccount": "3c86139b-63c1-4a76-bc1b-ea6c324947c9"
"DeliveryAccountCode": " 22"
"DeliveryAccountName": "Fittsport BV"
"DeliveryAddress": "768ef02f-7b14-432a-ba15-1cc25ff3ed61"
"DeliveryContact": "f2aaff33-0f55-43e8-a065-8ecd90578e64"
"DeliveryContactPersonFullName": "Karin Ballegooier"
"DeliveryDate": "/Date(1455753600000)/"
"DeliveryNumber": 104
"Description": "Sports items delivery to FittSport BV"
"Document": null
"DocumentSubject": null
"EntryNumber": 16900011
"EntryID": "80d81d4c-d57e-490c-9396-48958abca734"
"Remarks": "Sport items delivery on 18 Feb 2016 for SO 71"
"ShippingMethod": "b060b786-83cb-43a4-9f06-e21348f67412"
"ShippingMethodCode": "SEA"
"ShippingMethodDescription": "Shipping method A"
"TrackingNumber": "TR123456"
"Warehouse": "18016fa1-e87b-493d-a70d-4f6eb1274706"
"WarehouseCode": "1"
"WarehouseDescription": "Warehouse"
-"GoodsDeliveryLines":
{"__deferred": 
{"uri": "../api/v1/{Division}/salesorder/GoodsDeliveries(guid'80d81d4c-d57e-490c-9396-48958abca734')/GoodsDeliveryLines"
}}}}
Step 2: Edit the Tracking number
Find out the entry ID and goods delivery line IDs of goods deliveries created previously based on the delivery number.
GET REQUEST:

../api/v1/{Division}/salesorder/GoodsDeliveries
?$select=EntryID,GoodsDeliveryLines/ID&$expand=GoodsDeliveryLines
&$filter=DeliveryNumber eq 104
RESPONSE:

{"d"
{"results": [1]
0:  
{"__metadata": 
{
"uri": "../api/v1/{Division}/salesorder/GoodsDeliveries(guid'80d81d4c-d57e-490c-9396-48958abca734')"
"type": "Exact.Web.Api.Models.SalesOrders.GoodsDelivery"
}
"EntryID": "80d81d4c-d57e-490c-9396-48958abca734"
"GoodsDeliveryLines": 
{
"results": 
[3]
0:  
	{"__metadata": 
	{
	"uri": "../api/v1/{Division}/salesorder/GoodsDeliveryLines(guid'69370112-693c-486b-9898-2ae91f98acbe')"
	"type": "Exact.Web.Api.Models.SalesOrders.GoodsDeliveryLine"
	}
	"ID": "69370112-693c-486b-9898-2ae91f98acbe"
	}
1:  
	{"__metadata": 
	{
	"uri": "../api/v1/{Division}/salesorder/GoodsDeliveryLines(guid'c16723d2-6c14-465c-b3a2-5b7140f9624a')"
	"type": "Exact.Web.Api.Models.SalesOrders.GoodsDeliveryLine"
	}
	"ID": "c16723d2-6c14-465c-b3a2-5b7140f9624a"
	}
2:  
	{"__metadata": 
	{
	"uri": "../api/v1/{Division}/salesorder/GoodsDeliveryLines(guid'54d26f43-dc90-432f-8d3a-8c1ef6407ef9')"
	"type": "Exact.Web.Api.Models.SalesOrders.GoodsDeliveryLine"
	}
	"ID": "54d26f43-dc90-432f-8d3a-8c1ef6407ef9"
	}
}}}}
Update the tracking number for goods delivery header information.

PUT REQUEST:

../api/v1/{Division}/salesorder/GoodsDeliveries(guid'80d81d4c-d57e-490c-9396-48958abca734')
{“TrackingNumber”: “TR888999”}
RESPONSE:

You receive the message 204 No Content.

Related information
The following properties are filled with a value that can be retrieved from other resources. The URIs of the related resources are specified below.

Resource	Properties	URI of the related resource
GoodsDeliveries	DeliveryAccount	/api/v1/{division}/crm/Accounts
GoodsDeliveries	DeliveryContact	/api/v1/{division}/crm/Contacts
GoodsDeliveries	DeliveryAddress	/api/v1/{division}/crm/Addresses
GoodsDeliveries	Documents	/api/v1/{division}/documents/Documents
GoodsDeliveries	Warehouses	/api/v1/{division}/inventory/Warehouses
GoodsDeliveryLines	BatchNumbers	/api/v1/{division}/inventory/StockBatchNumbers
GoodsDeliveryLines	Items	/api/v1/{division}/logistics/Items
GoodsDeliveryLines	SalesOrderID	/api/v1/{division}/salesorder/SalesOrderLines
GoodsDeliveryLines	SerialNumbers	/api/v1/{division}/inventory/StockSerialNumbers
GoodsDeliveryLines	StorageLocation	/api/v1/{division}/inventory/StorageLocations
GoodsDeliveryLines	UnitCode	/api/v1/{division}/logistics/Units
Related topics
Exact Online REST API - Reference information
Using OAuth 2.0 to access Exact Online API