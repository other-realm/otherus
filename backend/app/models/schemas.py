"""Pydantic schemas for request/response validation."""
from __future__ import annotations
from typing import Any, Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
# ── User ──────────────────────────────────────────────────────────────────────
class UserBase(BaseModel):
    email: str
    name: str
    avatar_url: Optional[str] = None
    provider: str  # "google" | "github"
    provider_id: str
class UserCreate(UserBase):
    pass
class UserPublic(BaseModel):
    id: str
    email: str
    name: str
    avatar_url: Optional[str] = None
    provider: str
    created_at: str
    ntfy_topic: Optional[str] = None
class UserFull(UserPublic):
    profile: Optional[dict] = None
    is_admin: bool = False
# ── Profile ───────────────────────────────────────────────────────────────────
class ProfileUpdate(BaseModel):
    data: dict[str, Any]
class ProfilePublic(BaseModel):
    user_id: str
    user_name: str
    avatar_url: Optional[str] = None
    data: dict[str, Any]
    updated_at: str
# ── Experiments ───────────────────────────────────────────────────────────────
class ExperimentCreate(BaseModel):
    title: str
    slug: str
    content: str  # HTML from WYSIWYG editor
    status: str = "active"  # "active" | "completed"
    tags: list[str] = []
class ExperimentUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[list[str]] = None
class ExperimentPublic(BaseModel):
    id: str
    title: str
    slug: str
    content: str
    status: str
    tags: list[str]
    author_id: str
    created_at: str
    updated_at: str
# ── Chat ──────────────────────────────────────────────────────────────────────
class ChatMessage(BaseModel):
    id: str
    room_id: str
    sender_id: str
    sender_name: str
    sender_avatar: Optional[str] = None
    content: str
    created_at: str
class ChatRoom(BaseModel):
    id: str
    type: str  # "dm" | "group"
    name: Optional[str] = None
    members: list[str]
    created_at: str
    last_message: Optional[ChatMessage] = None
class SendMessageRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=4000)
class CreateRoomRequest(BaseModel):
    type: str = "dm"  # "dm" | "group"
    name: Optional[str] = None
    member_ids: list[str]
# ── Auth ──────────────────────────────────────────────────────────────────────
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserFull
# ── Notifications ─────────────────────────────────────────────────────────────
class NotificationSubscribe(BaseModel):
    ntfy_topic: str
