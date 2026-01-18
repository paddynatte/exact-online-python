OData | Query string options
The use of query string options is a powerful feature of OData. They give you control over the order and amount of URI data that a service returns. Some or all query options may be supported by a data service. You can build a request optimised for performance using the majority of these query string options.

For more information on query sting options, see OData.

$select
With $select you can specify the properties you want to receive in the response message of a data service. The value is a comma-separated list of selection clauses. Each selection clause may be a property name or navigation property name. An effective way to retrieve data is to use the $filter option.

You are strongly advised not to use the ‘*’ character for filtering. This character will generate the data of all properties. It is best to limit the properties as you filter. This ensures an improved integration with Exact Online.
See the example below:

GET: .../api/v1/{division}/purchaseentry/PurchaseEntries?$select=EntryID,Description,AmountFC,DueDate
In order to retrieve a navigation property, you need to expand the navigation link first. See the example below:

GET: .../api/v1/{division}/purchaseentry/PurchaseEntries?$expand=PurchaseEntryLines&$select=EntryID,Description,AmountFC,DueDate,PurchaseEntryLines/GLAccountCode,PurchaseEntryLines/Description,PurchaseEntryLines/Type,PurchaseEntryLines/AmountFC
$filter
To add a selection criteria when you retrieve data from the service, use the $filter option. Doing this in combination with the $select option yields better results. The customer can indicate the values to be passed for the $filter and $select options within the user interface of your application. This way, you only transfer the data specified by the customer.

See the example below:

GET: .../api/v1/{division}/purchaseentry/PurchaseEntries?$filter=AmountFC ge -8500&$select=EntryID,Description,AmountFC,DueDate
Filtering on navigation property is currently not possible with Exact Online. This means that the following example is not supported:

?$filter= PurchaseEntryLines/AmountFC ge -8500
$expand
The $expand option causes the collection of an entity, which is part of a main entity, to expand in the response. An example of this would be to expand TransactionLines as part of Transactions. Based on the expanded collection, you can apply a $select option. Please note that the $filter option for an expanded list is not supported.

See the example below:

GET: .../api/v1/{division}/purchaseentry/PurchaseEntries?$expand=PurchaseEntryLines&$select=EntryID,Description,AmountFC,DueDate
The $skip option is no longer supported for new endpoints that are released after March 1st 2017 to prevent parallel requests. As an alternative, you are advised to use the $skiptoken option. For more information, see Tips and Tricks.
$count and $inlinecount
By using the $count and $inlinecount options, you can determine the number of records of a certain data entity. This is very useful in the mobile scenario where pagination is typically used to improve performance. The $count option will only return an integer value without a response body message. In this case, you should not include an Accept header.

See example below:

GET: .../api/v1/{division}/purchaseentry/PurchaseEntries/$count
The $inlinecount option will return a response body that includes a count property called ‘__count’.

GET: .../api/v1/{division}/purchaseentry/PurchaseEntries?$top=5&$inlinecount=allpages&$select=EntryNumber,AmountFC
$orderby
With the $orderby option you can order the results in an ascending order (by default) or descending order (extend with ‘desc’).


The $orderby option will significantly decrease the performance of a request.
See the example below:

GET: .../api/v1/{division}/purchaseentry/PurchaseEntries?$orderby=EntryNumber desc&$select=EntryNumber,AmountFC
This option will add more processing power within a data service. By retrieving a collection of data first, you can order on the client side (integration service). In future API version(s) this option may not be supported.
Related links
Integrate efficiently with OData
OData | Primitive data types
OData | Header types
OData | Best practices