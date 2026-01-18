REST API | Create an entry with attachment
This example covers a method of creating an entry with an attached document in three steps. To create an entry with an attachment using Exact Online API’s, you must first create a document in which this will be linked to the entry.

In the following tasks, the type purchase entry and sales entry are used as an example. This method can also be applied to create other types of entries in Exact Online.

Refer to the Reference documentation page for the list of available API’s in Exact Online.


The request examples shown on this page are based on mandatory fields. Go to the reference page of each API to see how you can expand the code examples for your own applications.
1. Create document
POST: .../api/v1/{division}/documents/Documents
Make a POST request using the above API. In resource Type, enter “20” for purchase entry, or “10” for sales entry. For more information on other available resources, go to the Documents API reference documentation.

See the JSON request example below:

{
       "Subject":"{Subject of the document}",
       "Type":“20”
}
A successful request returns a 201 - Created status code and a response body that shows the ID of the document. You will need this ID for step 2 and 3.

2. Add the attachment to the document
POST: .../api/v1/{division}/documents/DocumentAttachments
Make a POST request using the above API. Add your PDF attachment in BASE64 format and enter the ID of the document you've retrieved from step 1. For more information on other available resources, go to the DocumentAttachments API reference documentation.

See the JSON request example below:

{
	“Attachment":"{PDF as BASE64 encoded}",
	"Document":"{ID of the document}",
	"FileName":"{Filename of the attachment}"
}
3. Create the entry
POST: .../api/v1/{division}/purchaseentry/PurchaseEntries
OR

POST: .../api/v1/{division}/salesentry/SalesEntries
Make a POST request using one of the APIs above. In the resource Document, enter the document ID you've retrieved from step 1. For more information on other available resources, go to the PurchaseEntries API reference documentation or SalesEntries API reference documentation.

See the JSON request example below:

{
	“Journal":"{Journal code}",
	"Document":"{ID of the document from step 1}",
	"Supplier":"{ID of the account}",
		"PurchaseEntryLines":[
			{
			"AmountFC":"{The amount of the entry line}",
			"GLAccount":"{The ID of the GLAccount}"
			}
	]
}
A successful request returns a 201 - Created status code a response body that contains the URL of the entry linked to the document attachment.