"""OAuth authentication router — Google and GitHub."""
import uuid
import httpx
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import RedirectResponse, JSONResponse
from authlib.integrations.httpx_client import AsyncOAuth2Client
from app.config import get_settings
from app.models.schemas import TokenResponse, UserFull
from app.services.redis_service import json_set, json_get, keys_matching
from app.utils.jwt_utils import create_access_token
router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()
# ── Helpers ───────────────────────────────────────────────────────────────────
async def _find_user_by_provider(provider: str, provider_id: str) -> dict | None:
    keys = await keys_matching("user:*")
    for key in keys:
        user = await json_get(key)
        print('user: ',user," key: ",key,"provider: ",provider,"provider_id: ",provider_id)
        if user and user.get("provider") == provider and user.get("provider_id") == str(provider_id):
            return user
    return None
async def _upsert_user(provider: str, provider_id: str, email: str, name: str, avatar_url: str | None) -> dict:
    existing = await _find_user_by_provider(provider, provider_id)
    if existing:
        existing["name"] = name
        existing["avatar_url"] = avatar_url
        await json_set(f"user:{existing['id']}", ".", existing)
        return existing
    user_id = str(uuid.uuid4())
    ntfy_topic = f"{settings.ntfy_topic_prefix}-{user_id[:8]}"
    user = {
        "id": user_id,
        "email": email,
        "name": name,
        "avatar_url": avatar_url,
        "provider": provider,
        "provider_id": str(provider_id),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "ntfy_topic": ntfy_topic,
        "is_admin": False,
        "profile": None,
    }
    await json_set(f"user:{user_id}", ".", user)
    return user
def _make_token_response(user: dict) -> dict:
    token = create_access_token({"sub": user["id"]})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user,
    }
# ── Google OAuth ──────────────────────────────────────────────────────────────
@router.get("/google/login")
async def google_login():
    """Redirect the user to Google's OAuth consent screen."""
    client = AsyncOAuth2Client(
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
        redirect_uri=settings.google_redirect_uri,
        scope="openid email profile",
    )
    uri, _ = client.create_authorization_url(
        "https://accounts.google.com/o/oauth2/v2/auth",
        access_type="offline",
    )
    return RedirectResponse(uri)
@router.get("/google/callback")
async def google_callback(code: str, state: str | None = None):
    """Handle Google OAuth callback, exchange code for user info."""
    async with AsyncOAuth2Client(
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
        redirect_uri=settings.google_redirect_uri,
    ) as client: # type: ignore
        try:
            token = await client.fetch_token(
                "https://oauth2.googleapis.com/token",
                code=code,
            )
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Token exchange failed: {exc}")

        resp = await client.get("https://www.googleapis.com/oauth2/v3/userinfo")
        info = resp.json()
    
    print("code:",code,"state:",state,"token:",token,"info:",info)
    user = await _upsert_user(
        provider="google",
        provider_id=info["sub"],
        email=info.get("email", ""),
        name=info.get("name", ""),
        avatar_url=info.get("picture"),
    )
    result = _make_token_response(user)
    # Redirect to frontend with token
    frontend_url = f"{settings.frontend_url}/auth-callback?token={result['access_token']}"
    return RedirectResponse(frontend_url)
# ── GitHub OAuth ──────────────────────────────────────────────────────────────
@router.get("/github/login")
async def github_login():
    """Redirect the user to GitHub's OAuth consent screen."""
    params = (
        f"client_id={settings.github_client_id}"
        f"&redirect_uri={settings.github_redirect_uri}"
        f"&scope=read:user%20user:email"
    )
    print("Redirecting to GitHub with params:", f"https://github.com/login/oauth/authorize?{params}")
    return RedirectResponse(f"https://github.com/login/oauth/authorize?{params}")
@router.get("/github/callback")
async def github_callback(code: str):
    """Handle GitHub OAuth callback."""
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            "https://github.com/login/oauth/access_token",
            data={
                "client_id": settings.github_client_id,
                "client_secret": settings.github_client_secret,
                "code": code,
            },
            headers={"Accept": "application/json"},
        )
        print("GitHub token response:", token_resp.text)
        token_data = token_resp.json()
        access_token = token_data.get("access_token")
        if not access_token:
            raise HTTPException(status_code=400, detail="GitHub token exchange failed")
        headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
        user_resp = await client.get("https://api.github.com/user", headers=headers)
        gh_user = user_resp.json()
        # Fetch primary email if not public
        email = gh_user.get("email")
        if not email:
            emails_resp = await client.get("https://api.github.com/user/emails", headers=headers)
            emails = emails_resp.json()
            primary = next((e for e in emails if e.get("primary")), None)
            email = primary["email"] if primary else f"{gh_user['login']}@github.local"
        print("GitHub user info:", gh_user, "email:", email)
    user = await _upsert_user(
        provider="github",
        provider_id=str(gh_user["id"]),
        email=email,
        name=gh_user.get("name") or gh_user.get("login", ""),
        avatar_url=gh_user.get("avatar_url"),
    )
    result = _make_token_response(user)
    frontend_url = f"{settings.frontend_url}/auth-callback?token={result['access_token']}"
    return RedirectResponse(frontend_url)
# ── Token verify / me ─────────────────────────────────────────────────────────
@router.get("/me")
async def get_me(request: Request):
    """Return current user from Bearer token."""
    from app.middleware.auth import get_current_user
    from fastapi.security import HTTPAuthorizationCredentials
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = auth_header[7:]
    from app.utils.jwt_utils import decode_access_token
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = await json_get(f"user:{payload['sub']}")
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user