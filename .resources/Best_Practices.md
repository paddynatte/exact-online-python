OData | Best practices
You can apply some best practices to optimize the use of OData with Exact Online APIs. These include creating API requests synchronously and using Webhooks to retrieve data in real-time.

Create synchronous API requests
Requests to the Exact Online REST API can be initiated synchronously or in parallel. With parallel requests you setup multiple threads, each initiating their own set of requests using the $top and $skip options. However, on the server side these requests will be queued in an undetermined sequence order. As such, duplicate data records or even missing data records might be returned as a response.

Messages are queued in a random order if you initiate parallel requests. This means that the data integrity cannot be guaranteed and will decrease the performance of subsequent requests.
The Exact Online REST API should be accessed in a synchronous way in order to guarantee data integrity and performance. By default, the Exact Online REST API response message is limited to 60 records per request. If the result set contains more than 60 records, you can initiate subsequent requests automatically, because the response message will contain a “__next” property. You can validate the size of a result set upfront by using the $count option.

The “__next” property will contain a link to request the next set of records including the $select, $filter, or any other option you passed in the initial request with a $skiptoken option. By using this property you can automatically retrieve all records in one sequence. Because of this, a next request can only be made if the response of the previous request is received (for this reason these requests are synchronous).

See the request example below:

GET: .../api/v1/{division}/financial/GLAccounts?$select=Code,Description,Type,TypeDescription
When the above request contains more than 60 records, the response message will look like this:

{
"d": {
		"results": [
			:
			<<60 records>>
			:
		],
		"__next": "../api/v1/{division}/financial/GLAccounts?$select=Code,Description,Type,TypeDescription&$skiptoken=guid'12345678-aaaa-bbbb-cccc-ddddeeeeffff '"
	}
}
Retrieve real-time updates with Webhooks
Retrieving large amounts of records can be time consuming. The Exact Online REST API is meant to be used to retrieve specific data based on the required view presented to the customer. The amount of transferred data can be kept as small as possible. If you need to get all data upfront, you could do this action once and use webhooks to retrieve real-time updates of the records you already received.

For more information on Webhooks, see Exact Online Webhooks

Related links
Integrate efficiently with OData
OData | Primitive data types
OData | Header types
OData | Query string options