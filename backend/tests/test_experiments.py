"""Tests for experiment management endpoints."""
import pytest
from httpx import AsyncClient


SAMPLE_EXPERIMENT = {
    "title": "Quantum Entanglement Study",
    "slug": "quantum-entanglement-study",
    "content": "<p>Testing quantum consciousness theories.</p>",
    "status": "active",
    "tags": ["quantum", "consciousness"],
}


@pytest.mark.asyncio
async def test_list_experiments_empty(client: AsyncClient, test_user):
    """GET /experiments/ with no experiments should return empty list."""
    _, token = test_user
    response = await client.get(
        "/experiments/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_create_experiment_requires_admin(client: AsyncClient, test_user):
    """POST /experiments/ should require admin role."""
    _, token = test_user
    response = await client.post(
        "/experiments/",
        json=SAMPLE_EXPERIMENT,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_experiment_as_admin(client: AsyncClient, admin_user):
    """POST /experiments/ as admin should create experiment."""
    _, token = admin_user
    response = await client.post(
        "/experiments/",
        json=SAMPLE_EXPERIMENT,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == SAMPLE_EXPERIMENT["title"]
    assert data["slug"] == SAMPLE_EXPERIMENT["slug"]
    assert data["status"] == "active"
    assert "id" in data
    assert "created_at" in data
    return data


@pytest.mark.asyncio
async def test_get_experiment_by_id(client: AsyncClient, admin_user, test_user):
    """GET /experiments/{id} should return experiment details."""
    _, admin_token = admin_user
    create_resp = await client.post(
        "/experiments/",
        json=SAMPLE_EXPERIMENT,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    exp_id = create_resp.json()["id"]

    _, user_token = test_user
    response = await client.get(
        f"/experiments/{exp_id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200
    assert response.json()["id"] == exp_id


@pytest.mark.asyncio
async def test_get_experiment_not_found(client: AsyncClient, test_user):
    """GET /experiments/{unknown_id} should return 404."""
    _, token = test_user
    response = await client.get(
        "/experiments/nonexistent-id",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_experiment_as_admin(client: AsyncClient, admin_user):
    """PUT /experiments/{id} as admin should update experiment."""
    _, token = admin_user
    create_resp = await client.post(
        "/experiments/",
        json=SAMPLE_EXPERIMENT,
        headers={"Authorization": f"Bearer {token}"},
    )
    exp_id = create_resp.json()["id"]

    update_resp = await client.put(
        f"/experiments/{exp_id}",
        json={"title": "Updated Title", "status": "completed"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert update_resp.status_code == 200
    data = update_resp.json()
    assert data["title"] == "Updated Title"
    assert data["status"] == "completed"


@pytest.mark.asyncio
async def test_update_experiment_requires_admin(client: AsyncClient, admin_user, test_user):
    """PUT /experiments/{id} by non-admin should return 403."""
    _, admin_token = admin_user
    create_resp = await client.post(
        "/experiments/",
        json=SAMPLE_EXPERIMENT,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    exp_id = create_resp.json()["id"]

    _, user_token = test_user
    response = await client.put(
        f"/experiments/{exp_id}",
        json={"title": "Hacked Title"},
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_experiment_as_admin(client: AsyncClient, admin_user):
    """DELETE /experiments/{id} as admin should remove experiment."""
    _, token = admin_user
    create_resp = await client.post(
        "/experiments/",
        json=SAMPLE_EXPERIMENT,
        headers={"Authorization": f"Bearer {token}"},
    )
    exp_id = create_resp.json()["id"]

    delete_resp = await client.delete(
        f"/experiments/{exp_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert delete_resp.status_code == 204

    get_resp = await client.get(
        f"/experiments/{exp_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_filter_experiments_by_status(client: AsyncClient, admin_user, test_user):
    """GET /experiments/?status_filter=active should return only active experiments."""
    _, admin_token = admin_user
    await client.post(
        "/experiments/",
        json={**SAMPLE_EXPERIMENT, "slug": "active-exp", "status": "active"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    await client.post(
        "/experiments/",
        json={**SAMPLE_EXPERIMENT, "slug": "completed-exp", "status": "completed"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    _, user_token = test_user
    active_resp = await client.get(
        "/experiments/?status_filter=active",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert all(e["status"] == "active" for e in active_resp.json())

    completed_resp = await client.get(
        "/experiments/?status_filter=completed",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert all(e["status"] == "completed" for e in completed_resp.json())
