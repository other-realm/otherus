"""Tests for authentication endpoints."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """GET /health should return 200 with status ok."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "Other Us" in data["app"]


@pytest.mark.asyncio
async def test_get_me_unauthenticated(client: AsyncClient):
    """GET /auth/me without token should return 401."""
    response = await client.get("/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me_invalid_token(client: AsyncClient):
    """GET /auth/me with invalid token should return 401."""
    response = await client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalid.token.here"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me_valid_token(client: AsyncClient, test_user):
    """GET /auth/me with valid token should return user data."""
    user, token = test_user
    response = await client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user["id"]
    assert data["email"] == user["email"]
    assert data["name"] == user["name"]


@pytest.mark.asyncio
async def test_google_login_redirects(client: AsyncClient):
    """GET /auth/google/login should redirect to Google."""
    response = await client.get("/auth/google/login", follow_redirects=False)
    assert response.status_code in (302, 307)
    assert "accounts.google.com" in response.headers.get("location", "")


@pytest.mark.asyncio
async def test_github_login_redirects(client: AsyncClient):
    """GET /auth/github/login should redirect to GitHub."""
    response = await client.get("/auth/github/login", follow_redirects=False)
    assert response.status_code in (302, 307)
    assert "github.com" in response.headers.get("location", "")
