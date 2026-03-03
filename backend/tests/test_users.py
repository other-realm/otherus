"""Tests for user management and notification endpoints."""
import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock


@pytest.mark.asyncio
async def test_list_users(client: AsyncClient, test_user, admin_user):
    """GET /users/ should return list of all users (public fields)."""
    _, token = test_user
    response = await client.get(
        "/users/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    users = response.json()
    assert isinstance(users, list)
    assert len(users) >= 2  # test_user + admin_user
    # Should not expose sensitive fields
    for u in users:
        assert "provider_id" not in u
        assert "is_admin" not in u


@pytest.mark.asyncio
async def test_get_user_by_id(client: AsyncClient, test_user, admin_user):
    """GET /users/{id} should return public user info."""
    user, token = test_user
    other_user, _ = admin_user

    response = await client.get(
        f"/users/{other_user['id']}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == other_user["id"]
    assert data["name"] == other_user["name"]


@pytest.mark.asyncio
async def test_get_user_not_found(client: AsyncClient, test_user):
    """GET /users/{unknown_id} should return 404."""
    _, token = test_user
    response = await client.get(
        "/users/nonexistent-id",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_ntfy_topic(client: AsyncClient, test_user):
    """PUT /users/me/ntfy should update the user's ntfy topic."""
    _, token = test_user
    response = await client.put(
        "/users/me/ntfy",
        json={"ntfy_topic": "my-custom-topic"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["ntfy_topic"] == "my-custom-topic"


@pytest.mark.asyncio
async def test_notification_service_sends_push(client: AsyncClient, test_user):
    """Notification service should call ntfy.sh with correct parameters."""
    from app.services.notification_service import send_push_notification

    with patch("app.services.notification_service.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(return_value=AsyncMock(status_code=200))

        result = await send_push_notification(
            ntfy_topic="test-topic",
            title="Test Notification",
            message="Hello from Other Us",
        )
        assert result is True
        mock_client.post.assert_called_once()
        call_args = mock_client.post.call_args
        assert "test-topic" in call_args[0][0]


@pytest.mark.asyncio
async def test_users_require_auth(client: AsyncClient):
    """User endpoints should require authentication."""
    response = await client.get("/users/")
    assert response.status_code == 401

    response = await client.put("/users/me/ntfy", json={"ntfy_topic": "test"})
    assert response.status_code == 401
