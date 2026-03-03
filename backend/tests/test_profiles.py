"""Tests for profile management endpoints."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_my_profile_empty(client: AsyncClient, test_user):
    """GET /profiles/me for a user with no profile should return empty dict."""
    _, token = test_user
    response = await client.get(
        "/profiles/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json() == {}


@pytest.mark.asyncio
async def test_update_my_profile(client: AsyncClient, test_user):
    """PUT /profiles/me should create/update profile data."""
    user, token = test_user
    profile_data = {
        "name": "Test User",
        "transhumanist_ideas": "<p>Quantum consciousness experiments</p>",
        "wants": {
            "items": {"deep_conver": 80, "shared_passions": 70},
            "other": "",
        },
    }
    response = await client.put(
        "/profiles/me",
        json={"data": profile_data},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == user["id"]
    assert data["data"]["name"] == "Test User"
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_get_my_profile_after_update(client: AsyncClient, test_user):
    """GET /profiles/me after update should return saved data."""
    _, token = test_user
    profile_data = {"name": "Updated Name"}
    await client.put(
        "/profiles/me",
        json={"data": profile_data},
        headers={"Authorization": f"Bearer {token}"},
    )
    response = await client.get(
        "/profiles/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["data"]["name"] == "Updated Name"


@pytest.mark.asyncio
async def test_list_profiles(client: AsyncClient, test_user):
    """GET /profiles/ should return list of profiles."""
    user, token = test_user
    await client.put(
        "/profiles/me",
        json={"data": {"name": "Test User"}},
        headers={"Authorization": f"Bearer {token}"},
    )
    response = await client.get(
        "/profiles/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    profiles = response.json()
    assert isinstance(profiles, list)
    assert len(profiles) >= 1
    assert any(p["user_id"] == user["id"] for p in profiles)


@pytest.mark.asyncio
async def test_list_profiles_with_search(client: AsyncClient, test_user):
    """GET /profiles/?search=... should filter results."""
    _, token = test_user
    await client.put(
        "/profiles/me",
        json={"data": {"name": "Quantum Researcher"}},
        headers={"Authorization": f"Bearer {token}"},
    )
    response = await client.get(
        "/profiles/?search=Quantum",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    profiles = response.json()
    assert len(profiles) >= 1

    response_no_match = await client.get(
        "/profiles/?search=xyznotfound",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response_no_match.json() == []


@pytest.mark.asyncio
async def test_get_profile_by_id(client: AsyncClient, test_user):
    """GET /profiles/{user_id} should return that user's profile."""
    user, token = test_user
    await client.put(
        "/profiles/me",
        json={"data": {"name": "Test User"}},
        headers={"Authorization": f"Bearer {token}"},
    )
    response = await client.get(
        f"/profiles/{user['id']}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["user_id"] == user["id"]


@pytest.mark.asyncio
async def test_get_profile_not_found(client: AsyncClient, test_user):
    """GET /profiles/{unknown_id} should return 404."""
    _, token = test_user
    response = await client.get(
        "/profiles/nonexistent-user-id",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_account(client: AsyncClient, test_user):
    """DELETE /profiles/me should delete user account and profile."""
    user, token = test_user
    # Create a profile first
    await client.put(
        "/profiles/me",
        json={"data": {"name": "To Be Deleted"}},
        headers={"Authorization": f"Bearer {token}"},
    )
    # Delete account
    response = await client.delete(
        "/profiles/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 204

    # Token is still valid JWT but user no longer exists in DB → 404 from auth middleware
    me_response = await client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_response.status_code in (401, 404)


@pytest.mark.asyncio
async def test_profile_requires_auth(client: AsyncClient):
    """Profile endpoints should require authentication."""
    response = await client.get("/profiles/me")
    assert response.status_code == 401

    response = await client.put("/profiles/me", json={"data": {}})
    assert response.status_code == 401
