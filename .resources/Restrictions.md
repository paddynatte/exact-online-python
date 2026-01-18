Exact Online REST API - Restrictions
Number of requests
The REST API has a daily limit and a minutely limit. Both are per app and per division. For more information about this, please look at the documentation on API Limits.

Requests to the REST API should be made in a way that only a specific amount of data is gathered for a specific user in time. Don't use the REST API to implement intensive synchronization processes.

We also have a Fair Use Policy in place. See Overview Exact terms and conditions.

Tips:

Don't use multi-threaded requests (pipelining) to get or post your results quicker.
Don't try to fetch lists you already retrieved. When available, use webhooks instead. In case webhooks are not available, use the timestamp to proceed where you stopped the last time.

Retries on errors
Don't retry failing messages unlimited times. Implement retry logic on transient errors in your client, but don't retry on functional errors. We strongly recommend that you log what your app is doing. Use the activity and error logs to monitor your app activities, errors etc. How many requests is my app generating? Do I have errors?

Fair Use Policy
In case you are violating the fair use policy of Exact Online, Exact has the right to suspend the Exact Online services in the event of persistent excessive load. See the Terms and conditions regarding fair use policy.

Paging on CRUD APIs
The REST API is divided into CRUD and READ APIs. All CRUD APIs have a limitation of maximum 60 records within one API request. Most READ services don't have such limitations.

The REST API has a limitation of maximum 60 records within one API request. If there are records to follow, the response will have property with the name __next. The value of this property will be the URL to the endpoint that needs to be called for the next set of records.

Example: ../crm/Accounts?$skiptoken=guid'5b3debef-9b1c-4bcd-b7ae-003e8d4139df'

REST API content length
For The Netherlands and Belgium, the length of the REST API message is limited to 38 MB. For all other countries, the length of the REST API message is limited to 9.5 MB.

URL length
The REST API supports Uniform Resource Locators (URLs) with a length of up to 6000 characters. To avoid exceeding this limit, it is important to be aware of URL encoding.

Some frameworks and HTTP clients automatically encode URLs. This means that they replace unsafe characters with safe characters to comply with specification for URLs defined by The Internet Engineering Task Force (IETF). See RFC1738: Uniform Resource Locators.

For example, if you tell your HTTP client to request some documents using the following URL:

.../Documents?$filter=HID eq 108 or HID eq 211

The HTTP client applies URL encoding and replaces each space with ‘%20’. The resulting URL is longer by 12 characters:

.../Documents?$filter=HID%20eq%20108%20or%20HID%20eq%20211

If you use a URL that has unsafe characters with a length close to the 6000-character limit, the encoding may result in a URL length that is longer than the character limit, which will cause the request to be rejected. Please take care to avoid this scenario when your app uses long URLs.

Related topics
Use safe characters in URLs
The Internet Engineering Task Force