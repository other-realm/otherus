"""Users router — list users, update ntfy topic, admin operations."""
from fastapi import APIRouter, Depends, HTTPException
from app.middleware.auth import get_current_user
from app.models.schemas import NotificationSubscribe
from app.services.redis_service import json_set, json_get, keys_matching

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list)
async def list_users(current_user: dict = Depends(get_current_user)):
    """Return a list of all users (public fields only)."""
    keys = await keys_matching("user:*")
    users = []
    for key in keys:
        u = await json_get(key)
        print('user: ',u," key: ",key)
        if u:
            users.append({
                "id": u["id"],
                "name": u["name"],
                "avatar_url": u.get("avatar_url"),
                "created_at": u.get("created_at"),
            })
    return users


@router.get("/{user_id}", response_model=dict)
async def get_user(user_id: str, current_user: dict = Depends(get_current_user)):
    user = await json_get(f"user:{user_id}")
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": user["id"],
        "name": user["name"],
        "avatar_url": user.get("avatar_url"),
        "created_at": user.get("created_at"),
    }


@router.put("/me/ntfy", response_model=dict)
async def update_ntfy_topic(
    body: NotificationSubscribe,
    current_user: dict = Depends(get_current_user),
):
    """Update the user's ntfy.sh topic for push notifications."""
    user = await json_get(f"user:{current_user['id']}")
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user["ntfy_topic"] = body.ntfy_topic
    await json_set(f"user:{current_user['id']}", ".", user)
    return {"ntfy_topic": body.ntfy_topic}


@router.put("/me/admin", response_model=dict)
async def toggle_admin(current_user: dict = Depends(get_current_user)):
    """Toggle admin status — development helper only."""
    user = await json_get(f"user:{current_user['id']}")
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user["is_admin"] = not user.get("is_admin", False)
    await json_set(f"user:{current_user['id']}", ".", user)
    return {"is_admin": user["is_admin"]}
