"""
Other Us – FastAPI Backend
Handles: JWT auth, email/password login, Google OAuth, GitHub OAuth,
         user profiles, search, and account deletion.
Storage: Redis (JSON-style keys)
"""

import os
import json
import uuid
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

import httpx
import redis
from dotenv import load_dotenv
from fastapi import (
    FastAPI, HTTPException, Depends, status, Request, Response
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
import bcrypt as _bcrypt
from pydantic import BaseModel, EmailStr, field_validator
from sympy.abc import B

# ── Load env ──────────────────────────────────────────────────────────────────
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
BASE_URL = os.getenv("BASE_URL", "http://localhost")

SECRET_KEY = os.getenv("SECRET_KEY", "changeme")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
GITHUB_REDIRECT_URI = os.getenv("GITHUB_REDIRECT_URI")

REDIS_URL = os.getenv("REDIS_URL")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
REDIS_USERNAME = os.getenv("REDIS_USERNAME", "admin")
# ── Redis client ──────────────────────────────────────────────────────────────
def get_redis():
    return redis.Redis(
        host=REDIS_URL,
        port=6379,
        username=REDIS_USERNAME,
        password=REDIS_PASSWORD,
        decode_responses=True,
    )

# ── Password hashing (direct bcrypt — passlib is incompatible with bcrypt>=4) ──
def hash_password(plain: str) -> str:
    """Hash a plaintext password using bcrypt. Returns a UTF-8 string.
    Args:
        plain (str): The plaintext password to hash.
    Returns:
        str: The hashed password as a UTF-8 string.
    """    
    return _bcrypt.hashpw(plain.encode("utf-8"), _bcrypt.gensalt()).decode("utf-8")
def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    try:
        return _bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# ── FastAPI app ───────────────────────────────────────────────────────────────
app = FastAPI(title="Other Us API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Pydantic models ───────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    email: str
    password: str
    display_name: str
    bio: Optional[str] = ""
    interests: Optional[str] = ""
class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    bio: Optional[str] = None
    interests: Optional[str] = None
    avatar_url: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    display_name: str
    email: str
class OAuthStateRequest(BaseModel):
    provider: str  # "google" or "github"
# ── Redis helpers ─────────────────────────────────────────────────────────────
def redis_set_user(r: redis.Redis, user_id: str, data: dict):
    r.set(f"user:{user_id}", json.dumps(data))
    r.set(f"email_to_id:{data['email'].lower()}", user_id)
def redis_get_user(r: redis.Redis, user_id: str) -> Optional[dict]:
    raw = r.get(f"user:{user_id}")
    return json.loads(raw) if raw else None
def redis_get_user_by_email(r: redis.Redis, email: str) -> Optional[dict]:
    uid = r.get(f"email_to_id:{email.lower()}")
    if not uid:
        return None
    return redis_get_user(r, uid)
def redis_delete_user(r: redis.Redis, user_id: str):
    user = redis_get_user(r, user_id)
    if user:
        r.delete(f"email_to_id:{user['email'].lower()}")
    r.delete(f"user:{user_id}")
    # Remove from search index
    r.srem("users:all", user_id)
def redis_add_to_index(r: redis.Redis, user_id: str):
    r.sadd("users:all", user_id)
def redis_search_users(r: redis.Redis, query: str) -> list:
    all_ids = r.smembers("users:all")
    results = []
    query_lower = query.lower()
    for uid in all_ids: # type: ignore
        user = redis_get_user(r, uid)
        if user:
            searchable = " ".join([
                user.get("display_name", ""),
                user.get("email", ""),
                user.get("bio", ""),
                user.get("interests", ""),
                user.get("location", ""),
            ]).lower()
            if query_lower in searchable:
                results.append(public_user_view(user))
    return results
def public_user_view(user: dict) -> dict:
    """Return only public fields of a user."""
    return {
        "user_id": user.get("user_id"),
        "display_name": user.get("display_name", ""),
        "bio": user.get("bio", ""),
        "interests": user.get("interests", ""),
        "avatar_url": user.get("avatar_url", ""),
        "location": user.get("location", ""),
        "website": user.get("website", ""),
        "provider": user.get("provider", "email"),
        "created_at": user.get("created_at", ""),
    }

# ── JWT helpers ───────────────────────────────────────────────────────────────
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
def verify_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    r: redis.Redis = Depends(get_redis),
) -> dict:
    user_id = verify_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = redis_get_user(r, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# ── Auth routes ───────────────────────────────────────────────────────────────
@app.post("/auth/register", response_model=TokenResponse)
async def register(payload: UserCreate, r: redis.Redis = Depends(get_redis)):
    """Register a new user with email/password."""
    existing = redis_get_user_by_email(r, payload.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user_id = str(uuid.uuid4())
    hashed_pw = hash_password(payload.password)
    now = datetime.now(timezone.utc).isoformat()
    user_data = {
        "user_id": user_id,
        "email": payload.email.lower(),
        "password_hash": hashed_pw,
        "display_name": payload.display_name,
        "bio": payload.bio or "",
        "interests": payload.interests or "",
        "avatar_url": "",
        "location": "",
        "website": "",
        "provider": "email",
        "oauth_id": "",
        "created_at": now,
        "updated_at": now,
    }
    redis_set_user(r, user_id, user_data)
    redis_add_to_index(r, user_id)
    token = create_access_token({"sub": user_id})
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user_id=user_id,
        display_name=payload.display_name,
        email=payload.email.lower(),
    )
@app.post("/auth/token", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    r: redis.Redis = Depends(get_redis),
):
    """Login with email/password."""
    user = redis_get_user_by_email(r, form_data.username)
    if not user or not verify_password(form_data.password, user.get("password_hash", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token({"sub": user["user_id"]})
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user_id=user["user_id"],
        display_name=user["display_name"],
        email=user["email"],
    )


# ── Google OAuth ──────────────────────────────────────────────────────────────
@app.get("/auth/google/login")
async def google_login(r: redis.Redis = Depends(get_redis)):
    """Return the Google OAuth authorization URL."""
    state = secrets.token_urlsafe(32)
    r.setex(f"oauth_state:{state}", 600, "google")  # 10 min TTL
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "offline",
    }
    from urllib.parse import urlencode
    url = "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params)
    return {"auth_url": url, "state": state}
@app.get("/auth/google/callback")
async def google_callback(
    code: str,
    state: str,
    r: redis.Redis = Depends(get_redis),
):
    """Handle Google OAuth callback, exchange code for token."""
    stored = r.get(f"oauth_state:{state}")
    if not stored:
        raise HTTPException(status_code=400, detail="Invalid OAuth state")
    r.delete(f"oauth_state:{state}")
    async with httpx.AsyncClient() as client:
        # Exchange code for tokens
        token_resp = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
        )
        if token_resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to exchange Google code")
        token_data = token_resp.json()
        # Get user info
        userinfo_resp = await client.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {token_data['access_token']}"},
        )
        if userinfo_resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get Google user info")
        guser = userinfo_resp.json()
    email = guser.get("email", "").lower()
    oauth_id = guser.get("sub", "")
    display_name = guser.get("name", email.split("@")[0])
    avatar_url = guser.get("picture", "")
    # Find or create user
    user = redis_get_user_by_email(r, email)
    if not user:
        user_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        user = {
            "user_id": user_id,
            "email": email,
            "password_hash": "",
            "display_name": display_name,
            "bio": "",
            "interests": "",
            "avatar_url": avatar_url,
            "location": "",
            "website": "",
            "provider": "google",
            "oauth_id": oauth_id,
            "created_at": now,
            "updated_at": now,
        }
        redis_set_user(r, user_id, user)
        redis_add_to_index(r, user_id)
    else:
        # Update avatar if changed
        if avatar_url and user.get("avatar_url") != avatar_url:
            user["avatar_url"] = avatar_url
            user["updated_at"] = datetime.now(timezone.utc).isoformat()
            redis_set_user(r, user["user_id"], user)

    token = create_access_token({"sub": user["user_id"]})
    # Redirect to frontend with token
    redirect_url = f"{BASE_URL}:8550/oauth_callback?token={token}&provider=google"
    return RedirectResponse(url=redirect_url)


# ── GitHub OAuth ──────────────────────────────────────────────────────────────
@app.get("/auth/github/login")
async def github_login(r: redis.Redis = Depends(get_redis)):
    """Return the GitHub OAuth authorization URL."""
    state = secrets.token_urlsafe(32)
    r.setex(f"oauth_state:{state}", 600, "github")
    params = {
        "client_id": GITHUB_CLIENT_ID,
        "redirect_uri": GITHUB_REDIRECT_URI,
        "scope": "user:email read:user",
        "state": state,
    }
    from urllib.parse import urlencode
    url = "https://github.com/login/oauth/authorize?" + urlencode(params)
    return {"auth_url": url, "state": state}

@app.get("/auth/github/callback")
async def github_callback(
    code: str,
    state: str,
    r: redis.Redis = Depends(get_redis),
):
    """Handle GitHub OAuth callback."""
    stored = r.get(f"oauth_state:{state}")
    if not stored:
        raise HTTPException(status_code=400, detail="Invalid OAuth state")
    r.delete(f"oauth_state:{state}")
    async with httpx.AsyncClient() as client:
        # Exchange code for access token
        token_resp = await client.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={
                "client_id": GITHUB_CLIENT_ID,
                "client_secret": GITHUB_CLIENT_SECRET,
                "code": code,
                "redirect_uri": GITHUB_REDIRECT_URI,
            },
        )
        if token_resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to exchange GitHub code")
        token_data = token_resp.json()
        access_token = token_data.get("access_token")

        if not access_token:
            raise HTTPException(status_code=400, detail="No access token from GitHub")

        # Get user info
        user_resp = await client.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/vnd.github.v3+json",
            },
        )
        gh_user = user_resp.json()

        # Get primary email
        email_resp = await client.get(
            "https://api.github.com/user/emails",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/vnd.github.v3+json",
            },
        )
        emails = email_resp.json() if email_resp.status_code == 200 else []

    # Find primary verified email
    email = ""
    for e in emails:
        if isinstance(e, dict) and e.get("primary") and e.get("verified"):
            email = e["email"].lower()
            break
    if not email and gh_user.get("email"):
        email = gh_user["email"].lower()
    if not email:
        email = f"gh_{gh_user.get('id', uuid.uuid4().hex)}@github.noemail"

    oauth_id = str(gh_user.get("id", ""))
    display_name = gh_user.get("name") or gh_user.get("login", email.split("@")[0])
    avatar_url = gh_user.get("avatar_url", "")
    bio = gh_user.get("bio", "") or ""
    location = gh_user.get("location", "") or ""
    website = gh_user.get("blog", "") or ""

    user = redis_get_user_by_email(r, email)
    if not user:
        user_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        user = {
            "user_id": user_id,
            "email": email,
            "password_hash": "",
            "display_name": display_name,
            "bio": bio,
            "interests": "",
            "avatar_url": avatar_url,
            "location": location,
            "website": website,
            "provider": "github",
            "oauth_id": oauth_id,
            "created_at": now,
            "updated_at": now,
        }
        redis_set_user(r, user_id, user)
        redis_add_to_index(r, user_id)
    else:
        user["avatar_url"] = avatar_url
        user["updated_at"] = datetime.now(timezone.utc).isoformat()
        redis_set_user(r, user["user_id"], user)

    token = create_access_token({"sub": user["user_id"]})
    redirect_url = f"{BASE_URL}:8550/oauth_callback?token={token}&provider=github"
    return RedirectResponse(url=redirect_url)


# ── User profile routes ───────────────────────────────────────────────────────

@app.get("/users/me")
async def get_my_profile(current_user: dict = Depends(get_current_user)):
    """Get the current user's full profile."""
    return {k: v for k, v in current_user.items() if k != "password_hash"}


@app.put("/users/me")
async def update_my_profile(
    payload: UserUpdate,
    current_user: dict = Depends(get_current_user),
    r: redis.Redis = Depends(get_redis),
):
    """Update the current user's profile."""
    updated = {**current_user}
    if payload.display_name is not None:
        updated["display_name"] = payload.display_name
    if payload.bio is not None:
        updated["bio"] = payload.bio
    if payload.interests is not None:
        updated["interests"] = payload.interests
    if payload.avatar_url is not None:
        updated["avatar_url"] = payload.avatar_url
    if payload.location is not None:
        updated["location"] = payload.location
    if payload.website is not None:
        updated["website"] = payload.website
    updated["updated_at"] = datetime.now(timezone.utc).isoformat()
    redis_set_user(r, current_user["user_id"], updated)
    return {k: v for k, v in updated.items() if k != "password_hash"}


@app.delete("/users/me")
async def delete_my_account(
    current_user: dict = Depends(get_current_user),
    r: redis.Redis = Depends(get_redis),
):
    """Permanently delete the current user's account."""
    redis_delete_user(r, current_user["user_id"])
    return {"message": "Account deleted successfully"}


@app.get("/users/{user_id}")
async def get_user_profile(
    user_id: str,
    current_user: dict = Depends(get_current_user),
    r: redis.Redis = Depends(get_redis),
):
    """Get a public profile of any user by ID."""
    user = redis_get_user(r, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return public_user_view(user)

@app.get("/users/search/query")
async def search_users(
    q: str,
    current_user: dict = Depends(get_current_user),
    r: redis.Redis = Depends(get_redis),
):
    """Search users by name, bio, interests, or location."""
    if len(q.strip()) < 2:
        raise HTTPException(status_code=400, detail="Query must be at least 2 characters")
    results = redis_search_users(r, q.strip())
    # Exclude self from results
    results = [u for u in results if u["user_id"] != current_user["user_id"]]
    return {"results": results, "count": len(results)}

@app.get("/health")
async def health():
    return {"status": "ok", "service": "Other Us API"}