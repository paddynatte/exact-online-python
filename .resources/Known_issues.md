Known issues
Request: POST requests sent with the Expect: 100-Continue header are failing more than those without the Expect: 100-Continue header.

Response: 500

Possible problem
Requests with this header are more likely to be separated and return an error. Therefore the usage of this header is not supported.

Please make sure to exclude this header from your code.

Possible solution
Explicitly unset the Expect header in .NET by setting the ExpectContinue/Expect100Continue to false.

When using HttpClient in .NET:

var client = new HttpClient();

client.DefaultRequestHeaders.ExpectContinue = false;

When using HttpWebRequest in .NET:

var request = HttpWebRequest.Create();

request.ServicePoint.Expect100Continue = false;