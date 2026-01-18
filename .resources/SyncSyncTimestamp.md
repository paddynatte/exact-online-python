Exact Online REST API - Sync/SyncTimestamp
Endpoint
Sync/SyncTimestamp

Good to know
The sync APIs have the goal to keep the data between Exact Online and a 3rd party application the same.
When you use the Sync APIs for the first time, you might not want to sync all data, but you want to start syncing on a particular date.
Via the Modified date filter, you can retrieve a single timestamp and use it in the Sync APIs.
You must provide datetime as 'modified' and name of the endpoint as 'endpoint' to filter on property 'Modified' of each sync endpoint.
The first record found will be return based on the greater than or equal to logical operator.

You can provide the endPoint value based on the following supported endPoints:
    • sync/CRM/QuotationHeaders use QuotationHeaders as endPoint value.
    • sync/CRM/QuotationLines use QuotationLines as endPoint value.
    • sync/Financial/TransactionLines use TransactionLines as endPoint value.
    • sync/Inventory/ItemStorageLocations use ItemStorageLocations as endPoint value.
    • sync/Manufacturing/ShopOrders use ShopOrders as endPoint value.
    • sync/Manufacturing/ShopOrderMaterialPlans use ShopOrderMaterialPlans as endPoint value.
    • sync/Manufacturing/ShopOrderRoutingStepPlans use ShopOrderRoutingStepPlans as endPoint value.
    • sync/Manufacturing/ShopOrderPurchasePlanning use ShopOrderPurchasePlanning as endPoint value.
    • sync/Manufacturing/ShopOrderSubOrders use ShopOrderSubOrders as endPoint value.
    • sync/Manufacturing/MaterialIssues use MaterialIssues as endPoint value.
    • sync/Manufacturing/BillOfMaterialVersions use BillOfMaterialVersions as endPoint value.
    • sync/Manufacturing/BillOfMaterialMaterials use BillOfMaterialMaterials as endPoint value.
    • sync/PurchaseOrder/PurchaseOrders use PurchaseOrders as endPoint value.
    • sync/Project/Projects use Projects as endPoint value.
    • sync/Project/ProjectPlanning use ProjectPlanning as endPoint value.
    • sync/Project/ProjectWBS use ProjectWBS as endPoint value.
    • sync/Project/TimeCostTransactions use TimeCostTransactions as endPoint value.
    • sync/SalesInvoice/SalesInvoices use SalesInvoices as as endPoint value.
    • sync/SalesOrder/GoodsDeliveries use GoodsDeliveries as as endPoint value.
    • sync/SalesOrder/GoodsDeliveryLines use GoodsDeliveryLines as endPoint value.
    • sync/SalesOrder/SalesOrderHeaders use SalesOrderHeaders as endPoint value.
    • sync/SalesOrder/SalesOrderLines use SalesOrderLines as endPoint value.
    • sync/Subscription/Subscriptions use Subscriptions as endPoint value.
    • sync/Subscription/SubscriptionLines use SubscriptionLines as endPoint value.

For example : modified=datetime'2022-01-01'&endPoint='QuotationHeaders'
For this function to work correctly, you must supply all parameters.

Scope
Organization administration

Function URI
/api/v1/{division}/read/sync/Sync/SyncTimestamp?modified={Edm.DateTime}&endPoint={Edm.String}


GET
Example usage
/api/v1/{division}/read/sync/Sync/SyncTimestamp?modified=datetime'2014-01-01'&endPoint='value'&$select=API


Properties
Name ↑↓	Type ↑↓	Description ↑↓
	Modified 	Edm.DateTime	Last modified date
	API	Edm.String	Endpoint name of Sync API.
	TimeStampAsBigInt	Edm.Int64	Timestamp for Sync API