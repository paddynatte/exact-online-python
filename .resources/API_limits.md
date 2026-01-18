API limits
We’re building an ecosystem where our customers can expand Exact Online with great integration services. Developers are an important part of that ecosystem. We’re continually inspired by how you use the Exact Online API in innovative ways. As the ecosystem grows, we need to take steps to ensure the reliability and good performance of Exact Online, so our community can use it efficiently.

Rate limits will be applied to API calls to help control this type of behavior. These limits are applied to both types of Exact Online API calls: XML webservice and REST API.

This change allows us to keep our focus and keep commitments to developers. You’re an integral part of the Exact community, and we look forward to seeing what you build next.


To avoid missing out on important announcements that may affect your app's performance, make sure your account data in Exact Online is up to date. To check your account data, log in to Exact Online and go to User name > My Exact Online > My account data.
API rate limits
The rate limits below will limit the number of requests that your app is permitted to send during a time window. Each limit has a specific behaviour when it is exceeded.

Minutely limit - your app can make 60 API calls, per company, per minute.
Daily limit - your app can make 5,000 API calls, per company, per day.
The following limits are effective as of 1 July 2021:

You must not request new access token more than once every 10 minutes. You can only request for a new access token after 570 seconds from the time you successfully received the previous access token.
No more than 10 errors per API key, per user, per company, per endpoint, and per hour. When you exceed this limit, your API key will be temporarily blocked from making further requests. The block will automatically be lifted after one hour and will gradually increase when you continue making these errors. Response code 400, 401, 403, and 404 are counted as errors.
Mandatory filtering on single and bulk endpoints where sync APIs are available.
Based on fair use policy, we will take corrective action by throttling your app if the limit has been exceeded excessively. Some examples of excessive actions are repeated download of unchanged data every day, log in attempts to inactive accounts, and overloading the token endpoint. See section 7.4 of our terms and conditions.

To learn about tips and trick to comply with API rate limits, see Integrate efficiently with OData and API types to make your API calls more efficient.

Minutely limit
If your app exceeds the minutely limit for a company, any additional requests in the same minute will be rejected.

You have a limit of 60 calls per minute. If you make 60 calls between 10:00:00 and 10:00:40, any additional requests will be rejected for the next 20 seconds until 10:01:00. Making many calls in a short period can cause performance issues. To avoid this, spread the API calls over a longer period. When requesting data from Exact Online, using the SYNC APIs reduces the likelihood of exceeding the daily and minutely rate limits.

Unpermitted requests will be rejected with an HTTP 429 (Too Many Requests) response. Each response to an API call with a company code (also known as a division code) in the URL will return with two headers to help you keep track of the minutely limit.

Header name	Description
X-RateLimit-Minutely-Limit	The maximum number of API calls that your app is permitted to make per company, per minute.
X-RateLimit-Minutely-Remaining	The remaining number of API calls that your app is permitted to make for a company, per minute.
Daily limit
Once your app exceeds the daily limit for a company, your app's API calls for that company will be rejected, and you will receive an HTTP 429 (Too Many Requests) response similar to the minutely limit. Your app can still send requests for other companies.

Each response to an API call with a company (also known as division) code in the URL will return with three headers to help you keep track of the daily limit.

Header name	Description
X-RateLimit-Limit	The maximum number of API calls that your app is permitted to make per company, per day.
X-RateLimit-Remaining	The remaining number of API calls that your app is permitted to make for a company, per day.
X-RateLimit-Reset	The time at which the rate limit window resets in UTC epoch milliseconds.

Please don't continue to make API calls if you have reached the daily limit as they will be rejected until the rate limit window is reset at the start of the following day.

Alternatively, you can ask users of your app to upgrade to one of the Exact Online Premium solutions. With a Premium licence, you can make up to a total of 30,000 API calls per day, with no restrictions on the number of calls an app can make. For more information about Exact Online Premium solutions, please contact your Exact Account Manager.

Request URLs that don't have a company code are not counted as the daily limit. For example: .../api/v1/current/Me.

Mandatory filtering
Some properties within several endpoints require mandatory filtering. If you do not add the required $filter parameter in your request, an error message will return. In the REST API reference documentation, click on an endpoint and check which property requires filtering in the Filter column. If you don’t see the Filter column, it means that filtering is not yet mandatory within that endpoint. Keep an eye on our release notes to see updates on which endpoints have mandatory filtering applied.

Tips and tricks to comply with API rate limits
We encourage you to review our developers' documentation, and our API specialists can help you with any questions as well.

We have monitored some of the integration cases and discovered that the Exact Online API is not always used in the optimum way. For example, continuous polling, applying incorrect filters, and infinitely retrying a request when an error occurs. Here are some tips and tricks that might help you:

Log all the API calls you make to the Exact Online API. You can then monitor the traffic from your app and compare your results with ours.
Enhance your app with a counter for the number of requests per company that was sent in the last 60 seconds so you can control the flow of requests and avoid hitting the minutely limit.
Don’t initiate the OAuth flow for each API call. Access tokens are valid for 10 minutes and refresh tokens are valid until the next token refresh.
Cache API responses if you expect a lot of re-use. Don’t try to initiate API calls on every page load, but initiate API calls infrequently and load the response into a local cache.
Polling is needed less, since Exact offers webhooks for a lot of endpoints. See Exact Online Webhooks. Are the endpoints you need unavailable? Please tell us about your requirements through an idea request in our Developer Community Portal (sign in with your App Store partner account).
Prioritise active users, and only request data for users who have recently signed into your app.
Is it necessary to retrieve all data? Or is it possible to retrieve only modified data? Applying a filter and select each API request is great, though validate the filter technique based on your logging results. Make sure your timestamp, status, or any other transactional change is updated correctly within your integration service. Use a Sync API for retrieving data from Exact Online when an API is available.
Is it necessary to retrieve all data? Or is it possible to retrieve only modified data? Applying a filter and select on each API request is great, though validate the filter technique based on your logging results. Make sure your timestamp, status, or any other transactional change is updated correctly within your integration service.
Validate your error process. If the Exact Online API returns an error, the integration service shouldn’t retry the request forever. You can apply a scheme to retry it with exponentially growing intervals and a maximum number of retries. Again, your logging results will help you.
Example
You offer a reporting service to Exact customers, and currently three active users are making use of this service. Based on the Exact company configuration and volume of data sets (master data, transactions etc.) your integration service first needs to retrieve data to configure the service (and keep it up to date), and during operation it needs to retrieve transactional data. As an extra option, you offer a way to correct transactional data within Exact Online. This scenario will cause the following API behaviour:

User 1 (2 companies: A and B)
synchronise configuration data – 2,000 API calls per company, per day
retrieve (latest) transactional data – 500 API calls per company, per day

TOTAL: 5,000 API calls per day
User 2 (2 companies: B and C)
synchronise configuration data – 400 API calls per company, per day
retrieve (latest) transactional data – 700 API calls per company, per day
apply corrections to transactional data – 400 API calls per company, per day

TOTAL: 3,000 API calls per day
User 3 (4 companies: A, B, C, and D)
initial synchronisation of configuration data – 500 API calls per company, per day
retrieve all transactional data based on a certain start date/time – 1,000 API calls per company, per day

TOTAL: 6,000 API calls per day

So, in total your integration service initiates 14,000 API calls per day, though on a company level the number of API calls will be different. Let’s take a look whether this is within the daily quota limit of 5,000 calls per company.
On a daily basis the integration service generates:
4,000 API calls for company A (users 1 and 3)
5,500 API calls for company B (users 1, 2, and 3)
3,000 API calls for company C (users 2 and 3)
1,500 API calls for company D (user 3)
The number of calls for company A, C, and D are within the daily limit. However, in the future they will exceed the daily limit as the limit is gradually being reduced to 5,000 requests per company per day.
The daily limit is exceeded for company B.
After 5,000 API calls to company B, your app will receive HTTP 429 (Too Many Requests) responses to further requests for that company.
A fair use of 20,000 API calls in total per Exact Online contract per day is applicable. With a Exact Online Premium licence, you can make up to a total of 30,000 API calls per day, with no restrictions on the number of calls a single app can make. For more information about upgrading to a Exact Online Premium licence, please contact your Exact Account Manager.

Request size limit
A single HTTP POST request to the Exact Online API has a size limit of 10.0 MB. There is no limit to the number of records within a request if the total request size does not exceed 10.0 MB. In the case of binaries, the size limit only applies to the actual binary size (instead of the base64-encoded string size).

App registration limits
There is currently no limit on the number of app registrations, but we strongly advise that you create a maximum of four app registrations per app to support a development, testing, acceptance, and deployment (DTAP).

Rate limit FAQ
Can't Exact handle more than 5,000 API calls?
Yes, we can. However, 97,5% of our customers never reach this limit. We constantly look for the best limit so we can ensure the best performance. If you need more than 5,000 API calls, please contact us.

What if I need more than 5,000 API calls per app, per company, per day?
We have validated that this limit only affects a small number of integration services. You can optimise your integration service by applying best practices on API designs. You can use Sync APIs to retrieve only updated data from Exact Online.

Exact Online Premium solutions offer options to increase the number of API calls to up to 30,000 calls per day, with no restrictions on the number of calls a single app can make. For more information about Exact Online Premium solutions, please contact your Exact Account Manager.

What is the best way to handle API calls within my app?
It is recommended that apps are able to control API request queueing. This will ensure that your app will behave within our supported limits and will also allow your app to continue operating even when the Exact Online API might be temporarily unavailable.

What if I need to retrieve large amounts of data from Exact Online?
The API limits might be exceeded when, for example, retrieving an initial data set from Exact Online of all transactions. Most API endpoints support pagination, though only per 60 records (for the REST API). Therefore, we provide API endpoints that support bulk or sync operations for GET, with which you can request a maximum of 1,000 records per API call. When no bulk or sync operation is supported, it can take some time to retrieve all the required data. We recommend you design your app in such a way (schedule or queue) that there is no user expectation of an immediate response. Sync APIs are preferred for retrieving data from Exact Online. When retrieving an initial set of data through Sync APIs, you might not want to sync all data, but to start syncing on a particular date. For these scenarios, we offer a Sync/SyncTimestamp API. Using the Modified date filter, you can retrieve a single timestamp and use it in the Sync APIs.

The API limits might be exceeded when retrieving an initial data set from Exact Online by retrieving all transactions, for example. Most API endpoints support pagination, though only per 60 records (for REST API). Therefore, we provide some API endpoints that support bulk operations for GET, with which you can request a maximum of 1,000 records per API call. When no bulk operation is supported, it can take some time to retrieve all the required data. We recommend you design your app in such a way (schedule or queue) that there is no user expectation of an immediate response.

Do the API rate limits apply for all customers that use my app?
The number of calls of your app is limited per company. If multiple users are accessing a company through your app all those HTTP requests are counted for the quota and bursting limits on that company.

What if my app still can't operate correctly within the Exact Online API limits?
While the current API limits cannot be adjusted by default, we can provide advice to API users on making their integration service more efficient. Please reach out to our API specialists through our Developer Community Portal (sign in with your App Store partner account).

As an alternative, you can ask users of your app to upgrade to one of the Exact Online Premium solutions so that their API limit is up to a total of 30,000 calls per day, with no restrictions on the number of calls a single app can make. For more information about Exact Online Premium solutions, please contact your Exact Account Manager.