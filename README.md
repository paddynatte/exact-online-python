Implementing Exact Online’s resources in our services was challenging and, frankly, inelegant. That’s likely on us, but we felt we were missing something, so we built this.

We may not cover every resource out of the box. We focused on what was most useful for us, and we’d love your contributions so this can help everyone.

The SDK handles most of the complexity, but you are responsible for token storage to ensure tokens persist after each refresh. Exact Online access tokens expire after 10 minutes and must be refreshed about 30 seconds before expiry to prevent race conditions, so storing the newly issued tokens matters.

### Authorization

Construct the authorization URL, sign in, and capture the authorization code from the callback (`?code=xxx`).

```
https://start.exactonline.nl/api/oauth2/auth?client_id=YOUR_CLIENT_ID&redirect_uri=YOUR_REDIRECT_URI&response_type=code
```

After signing in, Exact Online redirects to your `redirect_uri` with the code:

```
https://yourapp.com/callback?code=XTzM!IAAAACbPTzQJXwFhM...
```

Example FastAPI callback:

```python
@app.get("/callback")
async def callback(code: str):
    await oauth.exchange(code)
    return True
```

> The authorization code expires after 3 minutes. After exchange, tokens are saved via your token storage implementation.

### Token Storage

Implement the `TokenStorage` protocol to persist tokens. Exact Online rotates the refresh token on every refresh, if you don’t persist the newest tokens, you lose access.

```python
class MyTokenStorage:
    async def get_tokens(self) -> TokenData | None:
        ...
    
    async def save_tokens(self, tokens: TokenData) -> None:
        ...
```

> Store `expires_at` as a timezone-aware UTC datetime. Naive or local times will break the refresh logic.