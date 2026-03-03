"""Tests for chat room and messaging endpoints."""
import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock


@pytest.mark.asyncio
async def test_list_rooms_empty(client: AsyncClient, test_user):
    """GET /chat/rooms with no rooms should return empty list."""
    _, token = test_user
    response = await client.get(
        "/chat/rooms",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_create_dm_room(client: AsyncClient, test_user, admin_user):
    """POST /chat/rooms should create a DM room between two users."""
    user, token = test_user
    other_user, _ = admin_user

    with patch("app.routers.chat.publish_message", new_callable=AsyncMock):
        response = await client.post(
            "/chat/rooms",
            json={"type": "dm", "member_ids": [other_user["id"]]},
            headers={"Authorization": f"Bearer {token}"},
        )
    assert response.status_code == 201
    data = response.json()
    assert data["type"] == "dm"
    assert user["id"] in data["members"]
    assert other_user["id"] in data["members"]
    return data


@pytest.mark.asyncio
async def test_create_group_room(client: AsyncClient, test_user, admin_user):
    """POST /chat/rooms with type=group should create a group room."""
    user, token = test_user
    other_user, _ = admin_user

    response = await client.post(
        "/chat/rooms",
        json={"type": "group", "name": "Research Team", "member_ids": [other_user["id"]]},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["type"] == "group"
    assert data["name"] == "Research Team"


@pytest.mark.asyncio
async def test_get_room(client: AsyncClient, test_user, admin_user):
    """GET /chat/rooms/{id} should return room details for members."""
    user, token = test_user
    other_user, _ = admin_user

    create_resp = await client.post(
        "/chat/rooms",
        json={"type": "dm", "member_ids": [other_user["id"]]},
        headers={"Authorization": f"Bearer {token}"},
    )
    room_id = create_resp.json()["id"]

    response = await client.get(
        f"/chat/rooms/{room_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["id"] == room_id


@pytest.mark.asyncio
async def test_get_room_not_member(client: AsyncClient, test_user, admin_user):
    """GET /chat/rooms/{id} should return 403 for non-members."""
    _, admin_token = admin_user
    # Create a room with only admin
    create_resp = await client.post(
        "/chat/rooms",
        json={"type": "group", "name": "Private", "member_ids": []},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    room_id = create_resp.json()["id"]

    _, user_token = test_user
    response = await client.get(
        f"/chat/rooms/{room_id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_send_message_rest(client: AsyncClient, test_user, admin_user):
    """POST /chat/rooms/{id}/messages should persist and return message."""
    user, token = test_user
    other_user, _ = admin_user

    create_resp = await client.post(
        "/chat/rooms",
        json={"type": "dm", "member_ids": [other_user["id"]]},
        headers={"Authorization": f"Bearer {token}"},
    )
    room_id = create_resp.json()["id"]

    with patch("app.routers.chat.publish_message", new_callable=AsyncMock):
        with patch("app.routers.chat.notify_user_of_message", new_callable=AsyncMock):
            msg_resp = await client.post(
                f"/chat/rooms/{room_id}/messages",
                json={"content": "Hello, world!"},
                headers={"Authorization": f"Bearer {token}"},
            )

    assert msg_resp.status_code == 201
    msg = msg_resp.json()
    assert msg["content"] == "Hello, world!"
    assert msg["sender_id"] == user["id"]
    assert msg["room_id"] == room_id


@pytest.mark.asyncio
async def test_get_messages(client: AsyncClient, test_user, admin_user):
    """GET /chat/rooms/{id}/messages should return message history."""
    user, token = test_user
    other_user, _ = admin_user

    create_resp = await client.post(
        "/chat/rooms",
        json={"type": "dm", "member_ids": [other_user["id"]]},
        headers={"Authorization": f"Bearer {token}"},
    )
    room_id = create_resp.json()["id"]

    with patch("app.routers.chat.publish_message", new_callable=AsyncMock):
        with patch("app.routers.chat.notify_user_of_message", new_callable=AsyncMock):
            await client.post(
                f"/chat/rooms/{room_id}/messages",
                json={"content": "Message 1"},
                headers={"Authorization": f"Bearer {token}"},
            )
            await client.post(
                f"/chat/rooms/{room_id}/messages",
                json={"content": "Message 2"},
                headers={"Authorization": f"Bearer {token}"},
            )

    msgs_resp = await client.get(
        f"/chat/rooms/{room_id}/messages",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert msgs_resp.status_code == 200
    messages = msgs_resp.json()
    assert len(messages) == 2
    contents = [m["content"] for m in messages]
    assert "Message 1" in contents
    assert "Message 2" in contents


@pytest.mark.asyncio
async def test_send_message_empty_content(client: AsyncClient, test_user, admin_user):
    """POST /chat/rooms/{id}/messages with empty content should return 422."""
    user, token = test_user
    other_user, _ = admin_user

    create_resp = await client.post(
        "/chat/rooms",
        json={"type": "dm", "member_ids": [other_user["id"]]},
        headers={"Authorization": f"Bearer {token}"},
    )
    room_id = create_resp.json()["id"]

    response = await client.post(
        f"/chat/rooms/{room_id}/messages",
        json={"content": ""},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_my_rooms(client: AsyncClient, test_user, admin_user):
    """GET /chat/rooms should return only rooms the user is a member of."""
    user, token = test_user
    other_user, admin_token = admin_user

    # Create a room with both users
    await client.post(
        "/chat/rooms",
        json={"type": "dm", "member_ids": [other_user["id"]]},
        headers={"Authorization": f"Bearer {token}"},
    )
    # Create a room with only admin
    await client.post(
        "/chat/rooms",
        json={"type": "group", "name": "Admin Only", "member_ids": []},
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    response = await client.get(
        "/chat/rooms",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    rooms = response.json()
    # All returned rooms should include the test user
    for room in rooms:
        assert user["id"] in room["members"]
