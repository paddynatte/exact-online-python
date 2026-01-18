Tips and Tricks
Use the following tips and tricks to get more use out of the REST API.

Paging

To guarantee quick response times each GET request will return only a limited number of records. Usually this limit, also known as page size, is 60 records but it may vary per end point. When there a more records you will see a node with a __next tag in the response. There a hyperlink is provided to the next page of records. Execute a GET request with that hyperlink. The response contains the next page and again a __next tag if there are still more records. When you need the full set of records keep repeating these steps until the response doesn’t have a __next tag anymore.

Example:

GET https://start.exactonline.nl/api/v1/{division}/financial/ReportingBalance?$select=GLAccountCode,Amount

Then the response is:
{

"d": {

"results": [

...

],

"__next": "https://start.exactonline.nl/api/v1/{division}/financial/ReportingBalance?$select=GLAccountCode,Amount&$skiptoken=493115L"

}

}

Efficient table synchronization

There are two ways to synchronize data from to a client app. The most efficient way to do so is by using webhooks.

If your app needs to know about deleted records, this can only be done when you use webhooks.
The other way to synchronize data is to periodically check what has been changed since the previous synchronization. This is done by filtering on the ‘Modified’ property. This method will show you both new and updated records, but not the deleted ones.

Example: GET https://start.exactonline.nl/api/v1/{division}/crm/Accounts?$select=ID,Code,Name&$filter=Modified ge datetime'2017-05-31T00:00:00'

The result set may be bigger than the page size (usually 60 records) so you may have to do multiple calls using the paging mechanism to get all the records.
Combine POST with GET

In the REST API, the POST command is used to create a new entity. Once the POST command has successfully completed, the entity will contain all properties with the NULL value. Use the following header to get the entity with all the properties filled containing the current values:

Prefer: return=representation.

This way you won't need to use GET to get the filled in properties.

For some endpoints the only property that is filled will be the Guid of the created record. For these endpoints you can use GET command to retrieve all the data.
Check rights before use

You can make sure the user has sufficient rights for all API calls during the provisioning or subscription phase. With the UserHasRights API, you can check per endpoint and action whether the user is able to use the selected endpoints and actions.

For example, when you have a webshop app, you want to retrieve items from . You can use the GET Logistics/Items call. When the user has insufficient rights, an empty list will be displayed. This can happen because there are no items in available or the user doesn’t have the correct rights to see the items. To make sure the user has the correct rights, you can use the Users/UserHasRights?endpoint='Logistics/Items'&action='GET' call. The response will show if the user has the correct rights by displaying the True or False variable.

The other benefit for Partners is that these calls to the UserHasRights API are excluded from the Commercial Model. If you use this function and the user decides not to subscribe because of insufficient rights, the company will not appear in the App Usage Overview, and this usage is excluded from billing.

Filter on Account Code

In the Code property of the accounts service is a string field with a fixed length of 18 characters, which contains a number with leading spaces. If you do the following the numerical digits will be displayed in ascending order, sorted by code.

When a new account is created the value of the highest used code is incremented by 1.

To find an account with a specific code you must use the value including leading spaces:

GET REQUEST

https://start.exactonline.nl/api/v1/{division}/CRM/Accounts/?$top=1&$filter=Code eg,'                25'

When you don’t want to use the leading spaces you can also use the “trim” function, but this is less efficient.

GET REQUEST

https://start.exactonline.nl/api/v1/{division}/CRM/Accounts/?$top=1&$filter=trim(Code) eg,'25'

