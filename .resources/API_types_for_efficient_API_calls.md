API types to make your API calls more efficient
Exact Online offers different types of APIs to help you synchronise your data without having to make large amounts of API calls. When interacting with the Accounts endpoint for example, there are five different types of APIs you can choose from. This article illustrates the differences between those five APIs, so you can use the one that's best for you in the context of this example.

You can check if these API types are available for other resource endpoints in the Reference documentation.

Regular
The regular API allows you to create a GET, POST, PUT, and DELETE request. The regular API is the only API you can use to create or adjust an account. See Create accounts to learn more.

Webhooks
Webhooks are the best way to work with nearly real-time data in your app. They allow you to subscribe to one or more topics and receive notification when the topics are modified or deleted. For example, as soon as a new account is created by your client, your app would know about it. To learn more, see Exact Online Webhooks.

Bulk
A Bulk request gives you 1000 records per API call. It is best to use during full initial sync, or when you need to retrieve a large amount of data. When using the Bulk API, it is mandatory to provide the $select query option by selecting one or more resource properties.

Sync
The Sync API gives you 1000 records per call and is based on row versioning. By using a timestamp as a parameter, the Sync API returns only new and changed records. This is different than the Bulk API, which only returns records that meet certain conditions.

When retrieving records through this API, a timestamp value is returned. The highest timestamp value of the records returned is then stored on the client side. The next time you retrieve records through this API, the timestamp value stored on the client side is provided as a parameter. This method is more reliable than using modified date, because multiple records may have the same modified date and therefore the same record can be returned more than once.

Deleted
The Deleted API holds records of deleted entities, including accounts. Because the Sync API does not show deleted records, the Deleted API should be used simultaneously with the Sync API to keep the data between Exact Online and your app synchronised.