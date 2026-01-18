Exact Online REST API - Inventory/ItemWarehouses
Endpoint
Inventory/ItemWarehouses

Good to know
The sync api's have the goal to keep the data between Exact Online and a 3rd party application the same.

The sync api's are all based on row versioning and because of that it is guaranteed to be unique. Every time an existing record is changed or a new record is inserted, the row versioning value is higher than the highest available value at that time. When retrieving records via these api's also a timestamp value is returned. The highest timestamp value of the records returned should be stored on client side. Next time records are retrieved, the timestamp value stored on client side should be provided as parameter. The api will then return only the new and changed records. Using this method is more reliable than using modified date, since it can happen that multiple records have the same modified date and therefore same record can be returned more than once. This will not happen when using timestamp.

The sync api's are also developed to give best performance when retrieving records. Because of performance and the intended purpose of the api's, only the timestamp field is allowed as parameter.

The single and bulk api’s are designed for a different purpose. They provide ability to retrieve specific record or a set of records which meet certain conditions.

In case the division is moved to another database in Exact Online the timestamp values will be reset. Therefore, after a division is moved all data needs to be synchronized again in order to get the new timestamp values. To see if a division was moved, the /api/v1/{division}/system/Divisions can be used. The property DivisionMoveDate indicated at which date a division was moved and this date can be used to determine if it is needed to synchronize all data again.

The API has two important key fields, the Timestamp and the ID. The ID should be used to uniquely identify the record and will never change . The Timestamp is used to get new or changed records in an efficient way and will change for every change made to the record.

The timestamp value returned has no relation with actual date or time. As such it cannot be converted to a date\time value. The timestamp is a rowversion value.

When you use the sync or delete api for the first time for a particular division, filter on timestamp greater than 1.

Note: This endpoint does not support query { $select=* } since there are a lot of properties in this endpoint.



This endpoint is available for the following packages:

Manufacturing (Plus, Professional & Premium only)
Wholesale & Distribution (Plus, Professional & Premium only)
Scope
Logistics inventory

URI
/api/v1/{division}/sync/Inventory/ItemWarehouses


GET
Example usage
/api/v1/{division}/sync/Inventory/ItemWarehouses?$filter=Timestamp gt 5&$select=CountingCycle


Properties
Name ↑↓	Type ↑↓	Description ↑↓
	Timestamp 	Edm.Int64	Timestamp
	CountingCycle	Edm.Int16	Indicates the number of days for next cycle count.
	Created	Edm.DateTime	Creation date
	Creator	Edm.Guid	User ID of creator
	CreatorFullName	Edm.String	Name of creator
	DefaultStorageLocation	Edm.Guid	This is a default storage location
	DefaultStorageLocationCode	Edm.String	Default storage location's code
	DefaultStorageLocationDescription	Edm.String	Default storage location's description
	Division	Edm.Int32	Division code
	ID	Edm.Guid	A guid that is the unique identifier of the linkage between item and warehouse
	Item	Edm.Guid	Item ID
	ItemCode	Edm.String	Code of item
	ItemDescription	Edm.String	Description of item
	MaximumStock	Edm.Double	Maximum quantity of items that you want in warehouse
	Modified	Edm.DateTime	Last modified date
	Modifier	Edm.Guid	User ID of modifier
	ModifierFullName	Edm.String	Name of modifier
	OrderPolicy	Edm.Int16	Order Policy options: 1-Lot for lot, 2-Fixed order quantity, 3-Min / Max, 4-Order
	Period	Edm.Int16	Period that work together with replenishment in MRP
	ReorderPoint	Edm.Double	Quantity of items as an indication of when you need to reorder more stock for the warehouse
	ReorderQuantity	Edm.Double	Reorder quantity that work together with replenishment in MRP
	ReplenishmentType	Edm.Int16	Replenishment options: 1-Purchase, 2-Assemble, 3-Make, 4-Transfer, 5-No replenishment advice
	ReservedStock	Edm.Double	The quantity in a back to back order process which is already received from the purchase order, but not yet delivered for the sales order.
	SafetyStock	Edm.Double	Minimum quantity of items you must have in stock
	StorageLocationSequenceNumber	Edm.Int32	Sequence number of the item (Premium Only)
	Warehouse	Edm.Guid	Warehouse ID
	WarehouseCode	Edm.String	Code of warehouse
	WarehouseDescription	Edm.String	Description of warehouse