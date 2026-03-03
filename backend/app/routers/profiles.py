"""Profile management router."""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from app.middleware.auth import get_current_user
from app.models.schemas import ProfileUpdate, ProfilePublic
from app.services.redis_service import json_set, json_get, keys_matching, json_del

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.get("/me", response_model=dict)
async def get_my_profile(current_user: dict = Depends(get_current_user)):
    """Return the current user's profile data."""
    profile = await json_get(f"profile:{current_user['id']}")
    return profile or {}


@router.put("/me", response_model=dict)
async def update_my_profile(
    body: ProfileUpdate,
    current_user: dict = Depends(get_current_user),
):
    """Create or update the current user's profile."""
    now = datetime.now(timezone.utc).isoformat()
    profile = {
        "user_id": current_user["id"],
        "user_name": current_user["name"],
        "avatar_url": current_user.get("avatar_url"),
        "data": body.data,
        "updated_at": now,
    }
    await json_set(f"profile:{current_user['id']}", ".", profile)
    # Also update the user record to mark profile as set
    user = await json_get(f"user:{current_user['id']}")
    if user:
        user["profile"] = True
        await json_set(f"user:{current_user['id']}", ".", user)
    return profile


@router.get("/", response_model=list)
async def list_profiles(
    search: str = "",
    current_user: dict = Depends(get_current_user),
):
    """List all public profiles, optionally filtered by search term."""
    keys = await keys_matching("profile:*")
    profiles = []
    for key in keys:
        p = await json_get(key)
        if p is None:
            continue
        if search:
            name_match = search.lower() in p.get("user_name", "").lower()
            data_str = str(p.get("data", {})).lower()
            data_match = search.lower() in data_str
            if not (name_match or data_match):
                continue
        profiles.append(p)
    return profiles


@router.get("/{user_id}", response_model=dict)
async def get_profile(
    user_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Get a specific user's public profile."""
    profile = await json_get(f"profile:{user_id}")
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.delete("/me", status_code=204)
async def delete_my_account(current_user: dict = Depends(get_current_user)):
    """Delete the current user's account and all associated data."""
    uid = current_user["id"]
    # Delete profile
    await json_del(f"profile:{uid}")
    # Delete chat rooms membership (rooms where user is a member)
    room_keys = await keys_matching("room:*")
    for key in room_keys:
        room = await json_get(key)
        if room and uid in room.get("members", []):
            room["members"] = [m for m in room["members"] if m != uid]
            if not room["members"]:
                await json_del(key)
            else:
                await json_set(key, ".", room)
    # Delete user record
    await json_del(f"user:{uid}")
    return None
