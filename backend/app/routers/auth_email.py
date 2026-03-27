"""Email/password authentication endpoints."""
import uuid
from datetime import datetime, timezone
from email_validator import validate_email, EmailNotValidError # type: ignore
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from app.services.redis_service import json_get, json_set, json_mget, keys_matching
from app.utils.jwt_utils import create_access_token
from app.utils.password_utils import hash_password, verify_password
from app.config import get_settings
router = APIRouter(prefix="/auth", tags=["auth"])
print(router.prefix)
settings = get_settings()
class RegisterRequest(BaseModel):
    """Email/password registration request."""
    email: EmailStr
    password: str
    name: str
class LoginRequest(BaseModel):
    """Email/password login request."""
    email: EmailStr
    password: str
class AuthResponse(BaseModel):
    """Authentication response with token and user data."""
    access_token: str
    token_type: str
    user: dict
@router.post("/register", response_model=AuthResponse, status_code=201)
async def register(req: RegisterRequest):
    """Register a new user with email and password."""
    # Validate email format
    try:
        validate_email(req.email)
    except EmailNotValidError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid email: {str(e)}",
        )
    # Check if user already exists

    existing = await json_get(f"user:email:{req.email.lower()}")
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered.",
        )
    # Validate password strength (minimum 8 characters)
    if len(req.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long.",
        )
    # Create new user
    user_id = str(uuid.uuid4())
    user = {
        "id": user_id,
        "email": req.email.lower(),
        "name": req.name,
        "password_hash": hash_password(req.password),
        "provider": "email",
        "provider_id": req.email.lower(),
        "avatar_url": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "ntfy_topic": f"other-us-{user_id[:8]}",
        "is_admin": False,
        "profile": None,
    }
    # Store user in Redis
    await json_set(f"user:{user_id}", ".", user)
    # await json_set(f"user:email:{req.email.lower()}", ".", {"id": user_id})
    # Generate token
    token = create_access_token({"sub": user_id})
    # Remove sensitive fields before returning
    user_response = {k: v for k, v in user.items() if k != "password_hash"}
    return AuthResponse(
        access_token=token,
        token_type="bearer",
        user=user_response,
    )
async def _find_user_by_email(email: str) -> dict | None:
    """Scan all user:{id} documents and return the one matching the given email."""
    # Get all keys matching user:{id} pattern (exactly one colon — excludes user:email:* etc.)
    user_keys = [k for k in await keys_matching("user:*") if k.count(":") == 1]
    if not user_keys:
        return None
    # Fetch all user documents in a single Redis round-trip
    users = await json_mget(user_keys)
    for user in users:
        if user and user.get("email", "").lower() == email.lower():
            return user
    return None
@router.post("/email/login", response_model=AuthResponse)
async def login(req: LoginRequest):
    """Login with email and password."""
    print(f"Login attempt for email: {req.email}")
    # Find user by scanning user:{id} documents for a matching email field
    user = await _find_user_by_email(req.email.lower())
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )
    # Verify password
    if not verify_password(req.password, user.get("password_hash", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )
    user_id = user["id"]
    # Generate token
    token = create_access_token({"sub": user_id})
    # Remove sensitive fields before returning
    user_response = {k: v for k, v in user.items() if k != "password_hash"}
    return AuthResponse(
        access_token=token,
        token_type="bearer",
        user=user_response,
    )
class ChangePasswordRequest(BaseModel):
    """Change password request."""
    old_password: str
    new_password: str
@router.post("/change-password")
async def change_password(req: ChangePasswordRequest, user_id: str = None):
    """Change user password (requires authentication)."""
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated.",
        )
    # Retrieve user
    user = await json_get(f"user:{user_id}")
    if not user or user.get("provider") != "email":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password change only available for email-based accounts.",
        )
    # Verify old password
    if not verify_password(req.old_password, user.get("password_hash", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect current password.",
        )
    # Validate new password
    if len(req.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 8 characters long.",
        )
    # Update password
    user["password_hash"] = hash_password(req.new_password)
    await json_set(f"user:{user_id}", ".", user)
    return {"message": "Password changed successfully."}