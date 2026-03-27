"""Redis / RedisJSON connection and helpers."""
import json
from typing import Any, Optional
import redis.asyncio as aioredis
from app.config import get_settings

_redis: Optional[aioredis.Redis] = None


async def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        settings = get_settings()
        _redis = aioredis.from_url(
            settings.redis_url,
            username=settings.redis_username,
            password=settings.redis_password,
            decode_responses=True,
        )
    return _redis
async def close_redis():
    global _redis
    if _redis:
        await _redis.aclose()
        _redis = None
# ── RedisJSON helpers ─────────────────────────────────────────────────────────
async def json_set(key: str, path: str, value: Any) -> None:
    r = await get_redis()
    await r.execute_command("JSON.SET", key, path, json.dumps(value))
async def json_get(key: str, path: str = ".") -> Optional[Any]:
    r = await get_redis()
    raw = await r.execute_command("JSON.GET", key, path)
    if raw is None:
        return None
    # Handle case where raw is already a dict (from decode_responses=True)
    if isinstance(raw, dict):
        return raw
    # Otherwise, parse the JSON string
    return json.loads(raw)
async def json_del(key: str, path: str = ".") -> int:
    r = await get_redis()
    return await r.execute_command("JSON.DEL", key, path)
async def json_mget(keys: list[str], path: str = ".") -> list[Optional[Any]]:
    if not keys:
        return []
    r = await get_redis()
    raws = await r.execute_command("JSON.MGET", *keys, path)
    return [json.loads(r) if r else None for r in raws]
async def keys_matching(pattern: str) -> list[str]:
    r = await get_redis()
    return await r.keys(pattern)
async def set_with_expiry(key: str, value: str, seconds: int) -> None:
    r = await get_redis()
    await r.setex(key, seconds, value)
async def get_value(key: str) -> Optional[str]:
    r = await get_redis()
    return await r.get(key)
async def delete_key(key: str) -> int:
    r = await get_redis()
    return await r.delete(key)
async def sadd(key: str, *members: str) -> int:
    r = await get_redis()
    return await r.sadd(key, *members)
async def smembers(key: str) -> set:
    r = await get_redis()
    return await r.smembers(key)
async def srem(key: str, *members: str) -> int:
    r = await get_redis()
    return await r.srem(key, *members)
async def lpush(key: str, *values: str) -> int:
    r = await get_redis()
    return await r.lpush(key, *values)


async def lrange(key: str, start: int, end: int) -> list[str]:
    r = await get_redis()
    return await r.lrange(key, start, end)