"""Chat router — REST endpoints + WebSocket for real-time messaging."""
import uuid
import json
import asyncio
from datetime import datetime, timezone
from typing import Dict, Set
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query
from app.middleware.auth import get_current_user
from app.models.schemas import CreateRoomRequest, SendMessageRequest
from app.services.redis_service import (
    json_set, json_get, keys_matching, json_del, lpush, lrange, smembers, sadd, srem
)
from app.services.rabbitmq_service import publish_message
from app.services.notification_service import notify_user_of_message
from app.utils.jwt_utils import decode_access_token

router = APIRouter(prefix="/chat", tags=["chat"])

# In-memory WebSocket connection registry: room_id -> set of (user_id, websocket)
_ws_connections: Dict[str, Set[tuple]] = {}


# ── Room management ───────────────────────────────────────────────────────────

@router.post("/rooms", response_model=dict, status_code=201)
async def create_room(
    body: CreateRoomRequest,
    current_user: dict = Depends(get_current_user),
):
    """Create a DM or group chat room."""
    # For DMs, check if a room already exists between the two users
    if body.type == "dm" and len(body.member_ids) == 1:
        other_id = body.member_ids[0]
        members_sorted = sorted([current_user["id"], other_id])
        dm_key = f"dm:{members_sorted[0]}:{members_sorted[1]}"
        existing_room_id = await json_get(dm_key)
        if existing_room_id:
            room = await json_get(f"room:{existing_room_id}")
            if room:
                return room

    room_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    all_members = list(set([current_user["id"]] + body.member_ids))
    room = {
        "id": room_id,
        "type": body.type,
        "name": body.name or (", ".join(all_members[:2]) if body.type == "dm" else "Group Chat"),
        "members": all_members,
        "created_at": now,
        "last_message": None,
    }
    await json_set(f"room:{room_id}", ".", room)

    if body.type == "dm" and len(body.member_ids) == 1:
        other_id = body.member_ids[0]
        members_sorted = sorted([current_user["id"], other_id])
        dm_key = f"dm:{members_sorted[0]}:{members_sorted[1]}"
        await json_set(dm_key, ".", room_id)

    return room


@router.get("/rooms", response_model=list)
async def list_my_rooms(current_user: dict = Depends(get_current_user)):
    """List all chat rooms the current user is a member of."""
    keys = await keys_matching("room:*")
    rooms = []
    for key in keys:
        room = await json_get(key)
        if room and current_user["id"] in room.get("members", []):
            rooms.append(room)
    rooms.sort(key=lambda r: (r.get("last_message") or {}).get("created_at", r["created_at"]), reverse=True)
    return rooms


@router.get("/rooms/{room_id}", response_model=dict)
async def get_room(room_id: str, current_user: dict = Depends(get_current_user)):
    room = await json_get(f"room:{room_id}")
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    if current_user["id"] not in room.get("members", []):
        raise HTTPException(status_code=403, detail="Not a member of this room")
    return room


@router.get("/rooms/{room_id}/messages", response_model=list)
async def get_messages(
    room_id: str,
    limit: int = 50,
    current_user: dict = Depends(get_current_user),
):
    """Fetch the last N messages for a room."""
    room = await json_get(f"room:{room_id}")
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    if current_user["id"] not in room.get("members", []):
        raise HTTPException(status_code=403, detail="Not a member")
    raw_messages = await lrange(f"messages:{room_id}", 0, limit - 1)
    messages = [json.loads(m) for m in raw_messages]
    messages.reverse()
    return messages


@router.post("/rooms/{room_id}/messages", response_model=dict, status_code=201)
async def send_message(
    room_id: str,
    body: SendMessageRequest,
    current_user: dict = Depends(get_current_user),
):
    """Send a message to a room (REST fallback; WebSocket preferred)."""
    room = await json_get(f"room:{room_id}")
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    if current_user["id"] not in room.get("members", []):
        raise HTTPException(status_code=403, detail="Not a member")

    msg = _build_message(room_id, current_user, body.content)
    await _persist_and_broadcast(room, msg)
    return msg


# ── WebSocket ─────────────────────────────────────────────────────────────────

@router.websocket("/ws/{room_id}")
async def websocket_chat(
    websocket: WebSocket,
    room_id: str,
    token: str = Query(...),
):
    """WebSocket endpoint for real-time chat in a room."""
    payload = decode_access_token(token)
    if not payload:
        await websocket.close(code=4001)
        return

    user = await json_get(f"user:{payload['sub']}")
    if not user:
        await websocket.close(code=4001)
        return

    room = await json_get(f"room:{room_id}")
    if not room or user["id"] not in room.get("members", []):
        await websocket.close(code=4003)
        return

    await websocket.accept()

    # Register connection
    if room_id not in _ws_connections:
        _ws_connections[room_id] = set()
    conn_tuple = (user["id"], websocket)
    _ws_connections[room_id].add(conn_tuple)

    try:
        while True:
            data = await websocket.receive_text()
            try:
                payload_data = json.loads(data)
                content = payload_data.get("content", "").strip()
                if not content:
                    continue
            except json.JSONDecodeError:
                content = data.strip()

            msg = _build_message(room_id, user, content)
            await _persist_and_broadcast(room, msg)

    except WebSocketDisconnect:
        pass
    finally:
        _ws_connections.get(room_id, set()).discard(conn_tuple)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _build_message(room_id: str, user: dict, content: str) -> dict:
    return {
        "id": str(uuid.uuid4()),
        "room_id": room_id,
        "sender_id": user["id"],
        "sender_name": user["name"],
        "sender_avatar": user.get("avatar_url"),
        "content": content,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


async def _persist_and_broadcast(room: dict, msg: dict) -> None:
    room_id = room["id"]
    # Persist to Redis list
    await lpush(f"messages:{room_id}", json.dumps(msg))
    # Update last_message on room
    room["last_message"] = msg
    await json_set(f"room:{room_id}", ".", room)
    # Publish to RabbitMQ
    try:
        await publish_message(room_id, msg)
    except Exception:
        pass  # RabbitMQ unavailable — degrade gracefully

    # Broadcast to connected WebSocket clients in this room
    active_user_ids = {uid for uid, _ in _ws_connections.get(room_id, set())}
    for uid, ws in list(_ws_connections.get(room_id, set())):
        try:
            await ws.send_text(json.dumps(msg))
        except Exception:
            _ws_connections.get(room_id, set()).discard((uid, ws))

    # Send push notifications to offline members
    for member_id in room.get("members", []):
        if member_id != msg["sender_id"] and member_id not in active_user_ids:
            asyncio.create_task(
                notify_user_of_message(
                    recipient_user_id=member_id,
                    sender_name=msg["sender_name"],
                    room_name=room.get("name", "Chat"),
                    message_preview=msg["content"],
                )
            )
