Integrate efficiently with OData
OData offers many ways to identify, select, and filter data in order to build high-performing integrations. The protocol is added on top of the HTTP stack. This allows data services to exchange data via URIs (Uniform Resource Identifiers). For Exact Online, each service is offered as a WCF web service. In some cases, the WCF web service will cause a different behavior in relation to OData.

See OData Version 2.0 for more information on OData.

Refer to the information below to start practicing OData with Exact OnlineAPIs.

Retrieve metadata document
The metadata document lists all available URIs within a service. You can retrieve this document by initiating a request to a data service that includes the $metadata option. For the Exact Online REST API, you must first identify the company in order to access a data service. You must refer to the list of all available data services as listed in the REST API Reference documentation.

See the example below:

GET: .../api/v1/{division}/purchaseentry/$metadata
The $metadata option will return a service document in an XML-format. An Accept header is not needed, however if you pass one, make sure it accepts XML.

Address related entities in Exact Online
Entities are linked to other related entities in the Exact Online database. With OData, the same relation can be exposed. Although it is not supported for all Exact Online entities, some have a mandatory relationship. Think of the header and line structure of a financial transaction. These are indicated as collections within the REST API Reference documentation.

As an example, Transactions exposed as header with TransactionLines as collection of lines. You can access these linked entities directly via the parent URL. For more information, see the use of query string $expand in the OData | Query string options page.

Related links
OData | Primitive data types
OData | Header types
OData | Query string options
OData | Best practices