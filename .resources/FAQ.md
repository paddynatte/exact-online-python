REST API FAQ's
Use the following frequently asked questions to help clarify your use of the REST API.

When you use the GET or POST request, replace “..” at the beginning of these request examples with the related Exact Online endpoint of your country. For more information see Getting Started.
Where can I find the REST API reference documentation?
Go to Exact Online REST API - Reference information to see the REST API reference documentation.

When I create an API request, how do I know whether the data in the body has been configured correctly, and how can I validate this for JSON and/or XML?
An Exact Online API request supports two data formats: JSON and XML. They are specified in the header as follows:

Content-Type : application/json
Content-Type : application/xml
JSON (JavaScript Object Notation)
JSON is a lightweight data-interchange format and is based on a subset of the JavaScript Programming Language. For more information see JSON.
XML (Extensible Markup Language)
XML is a markup language that defines a set of rules for encoding documents, and is in a format that is both human-readable and machine-readable. For more information see XML.
To validate each format, you can use the following online tools:

jsonlint
xmlvalidation
If you try and pass a request through Exact Online using the wrong format, you will receive the following error: "Error processing request stream. The request should be a valid top-level resource object.”
How can I retrieve my division code for use with the REST API?
To retrieve the code, execute the following GET request to this location: ../api/v1/current/Me?$select=CurrentDivision

{
	"d": {
		"results": [
		{
			"__metadata": {
			"url": "https://start.exactonline.com/api/v1/current/Me(guid'9851e9c5-xxxx-xxxx-xxxx-cef894cccbe4')",
			"type": "Exact.Web.Api.System.Me"
						},
			"CurrentDivision": 7095
		}
		]
	}
}
						
Once you have retrieved the division code, you can access all your divisions by executing a GET request to: ../api/v1/7095/hrm/Divisions

You can directly request information; for example, to retrieve account information, execute a GET request to: ../api/v1/7095/crm/Accounts?$filter=Name eq 'Exact Online'&$select=ID

How can I apply filtering in a REST API request?
The following is an example of how to use filtering in an API request.

Execute the following GET request to retrieve an account ID from the account's list of division 7095. In this case, you are filtering on the name of the account and the account's phone number to retrieve the ID: ../api/v1/7095/crm/Accounts?$filter=Name eq 'Exact Online' and Phone eq '0123456789'&$select=ID

See Tips and Tricks for more filtering examples.

For more information on URI conventions see 4.5. Filter System Query Option ($filter)

What is the format of the datetime properties of the API's?
The value of the datetime properties is represented in UNIX time, also known as Epoch time. This is in the CET time and not GMT.

How can I use the oData $batch operation with REST API's?
The oData $batch operation is not supported for REST API's. The framework accepts all valid oData operations, including $batch operation, but we do not guarantee the outcome. We strongly advise to not use this operation.