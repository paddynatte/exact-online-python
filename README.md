Implementing Exact Online's resources into our services was challenging and inelegant, to say the least. This was probably our issue, but we felt like we were missing something, so I created this SDK.

This may not meet all your needs, we added what was helpful for us. We don't support every Exact Online resource out-of-the-box, but we'd love you to contribute so this can help everyone.

The SDK handles much of the complexity, but you'll need to manage token storage yourself to ensure tokens persist after each refresh. One challenge we faced was that Exact Online's access tokens expire after 10 minutes and must be refreshed 30 seconds before expiry to prevent race conditions, hence the need for token storage.

### Authorization

Initial authorization should be done by yourself. Construct the authorization URL, sign in, and obtain the authorization code from the callback redirect (`?code=xxx`).

```
https://start.exactonline.nl/api/oauth2/auth?client_id=YOUR_CLIENT_ID&redirect_uri=YOUR_REDIRECT_URI&response_type=code
```

After signing in, Exact Online redirects to your `redirect_uri` with the authorization code.

```
https://yourapp.com/callback?code=XTzM!IAAAACbPTzQJXwFhM...
```

You'll need a callback endpoint to receive this code. Here's an example using FastAPI.

```python
@app.get("/callback")
async def callback(code: str):
    await oauth.exchange(code)
    return True
```

> The authorization code expires after 3 minutes. After exchange, tokens are automatically saved via your token storage implementation.

### Token Storage

You must implement the `TokenStorage` protocol to persist tokens. This is critical because Exact Online rotates refresh tokens on every refresh, if you don't persist the new tokens, you lose access.

```python
class MyTokenStorage:
    async def get_tokens(self) -> TokenData | None:
        ...
    
    async def save_tokens(self, tokens: TokenData) -> None:
        ...
```

> Store `expires_at` as a timezone-aware datetime in UTC. Using naive datetimes or local times will cause token refresh logic to fail.