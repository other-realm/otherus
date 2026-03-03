"""Experiments and results router."""
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from app.middleware.auth import get_current_user
from app.models.schemas import ExperimentCreate, ExperimentUpdate, ExperimentPublic
from app.services.redis_service import json_set, json_get, keys_matching, json_del

router = APIRouter(prefix="/experiments", tags=["experiments"])


def _require_admin(user: dict):
    if not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")


@router.get("/", response_model=list)
async def list_experiments(
    status_filter: str = "",
    current_user: dict = Depends(get_current_user),
):
    """List all experiments, optionally filtered by status."""
    keys = await keys_matching("experiment:*")
    results = []
    for key in keys:
        exp = await json_get(key)
        if exp is None:
            continue
        if status_filter and exp.get("status") != status_filter:
            continue
        results.append(exp)
    results.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return results


@router.get("/{experiment_id}", response_model=dict)
async def get_experiment(
    experiment_id: str,
    current_user: dict = Depends(get_current_user),
):
    exp = await json_get(f"experiment:{experiment_id}")
    if exp is None:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return exp


@router.post("/", response_model=dict, status_code=201)
async def create_experiment(
    body: ExperimentCreate,
    current_user: dict = Depends(get_current_user),
):
    _require_admin(current_user)
    now = datetime.now(timezone.utc).isoformat()
    exp_id = str(uuid.uuid4())
    exp = {
        "id": exp_id,
        "title": body.title,
        "slug": body.slug,
        "content": body.content,
        "status": body.status,
        "tags": body.tags,
        "author_id": current_user["id"],
        "created_at": now,
        "updated_at": now,
    }
    await json_set(f"experiment:{exp_id}", ".", exp)
    return exp


@router.put("/{experiment_id}", response_model=dict)
async def update_experiment(
    experiment_id: str,
    body: ExperimentUpdate,
    current_user: dict = Depends(get_current_user),
):
    _require_admin(current_user)
    exp = await json_get(f"experiment:{experiment_id}")
    if exp is None:
        raise HTTPException(status_code=404, detail="Experiment not found")
    if body.title is not None:
        exp["title"] = body.title
    if body.content is not None:
        exp["content"] = body.content
    if body.status is not None:
        exp["status"] = body.status
    if body.tags is not None:
        exp["tags"] = body.tags
    exp["updated_at"] = datetime.now(timezone.utc).isoformat()
    await json_set(f"experiment:{experiment_id}", ".", exp)
    return exp


@router.delete("/{experiment_id}", status_code=204)
async def delete_experiment(
    experiment_id: str,
    current_user: dict = Depends(get_current_user),
):
    _require_admin(current_user)
    exp = await json_get(f"experiment:{experiment_id}")
    if exp is None:
        raise HTTPException(status_code=404, detail="Experiment not found")
    await json_del(f"experiment:{experiment_id}")
    return None
