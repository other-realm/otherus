"""Pytest configuration and fixtures for Other Us backend tests."""
import json
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.utils.jwt_utils import create_access_token

# ── In-memory Redis mock ───────────────────────────────────────────────────────

class MockRedis:
    """Simple in-memory mock for Redis JSON operations used in tests."""

    def __init__(self):
        self._store: dict = {}
        self._sets: dict = {}
        self._lists: dict = {}
        self._kv: dict = {}

    async def execute_command(self, *args):
        cmd = args[0].upper()
        if cmd == "JSON.SET":
            key, path, value = args[1], args[2], args[3]
            self._store[key] = json.loads(value)
            return "OK"
        elif cmd == "JSON.GET":
            key = args[1]
            val = self._store.get(key)
            return json.dumps(val) if val is not None else None
        elif cmd == "JSON.DEL":
            key = args[1]
            self._store.pop(key, None)
            return 1
        elif cmd == "JSON.MGET":
            # args: "JSON.MGET", key1, key2, ..., path
            keys = list(args[1:-1])
            return [json.dumps(self._store[k]) if k in self._store else None for k in keys]
        return None

    async def keys(self, pattern: str):
        import fnmatch
        return [k for k in self._store if fnmatch.fnmatch(k, pattern)]

    async def setex(self, key, seconds, value):
        self._kv[key] = value

    async def get(self, key):
        return self._kv.get(key)

    async def delete(self, *keys):
        for k in keys:
            self._store.pop(k, None)
            self._kv.pop(k, None)
        return len(keys)

    async def sadd(self, key, *members):
        self._sets.setdefault(key, set()).update(members)
        return len(members)

    async def smembers(self, key):
        return self._sets.get(key, set())

    async def srem(self, key, *members):
        s = self._sets.get(key, set())
        removed = sum(1 for m in members if m in s)
        s.difference_update(members)
        return removed

    async def lpush(self, key, *values):
        lst = self._lists.setdefault(key, [])
        for v in values:
            lst.insert(0, v)
        return len(lst)

    async def lrange(self, key, start, end):
        lst = self._lists.get(key, [])
        if end == -1:
            return lst[start:]
        return lst[start:end + 1]

    async def aclose(self):
        pass


_mock_redis = MockRedis()


@pytest.fixture(autouse=True)
def reset_and_inject_mock_redis():
    """Reset the in-memory Redis store and inject into redis_service before each test."""
    import app.services.redis_service as rs
    _mock_redis._store.clear()
    _mock_redis._sets.clear()
    _mock_redis._lists.clear()
    _mock_redis._kv.clear()
    # Inject mock directly into the module-level variable
    rs._redis = _mock_redis
    yield
    rs._redis = None


@pytest_asyncio.fixture
async def client():
    """Async HTTP test client with mocked Redis."""
    from app.main import app
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ── User fixtures ──────────────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def test_user():
    """Create a test user in mock Redis and return (user_dict, token)."""
    import uuid
    from datetime import datetime, timezone
    from app.services.redis_service import json_set

    user_id = str(uuid.uuid4())
    user = {
        "id": user_id,
        "email": "test@example.com",
        "name": "Test User",
        "avatar_url": None,
        "provider": "google",
        "provider_id": "google-123",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "ntfy_topic": f"other-us-{user_id[:8]}",
        "is_admin": False,
        "profile": None,
    }
    await json_set(f"user:{user_id}", ".", user)
    token = create_access_token({"sub": user_id})
    return user, token


@pytest_asyncio.fixture
async def admin_user():
    """Create an admin test user."""
    import uuid
    from datetime import datetime, timezone
    from app.services.redis_service import json_set

    user_id = str(uuid.uuid4())
    user = {
        "id": user_id,
        "email": "admin@example.com",
        "name": "Admin User",
        "avatar_url": None,
        "provider": "google",
        "provider_id": "google-admin",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "ntfy_topic": f"other-us-{user_id[:8]}",
        "is_admin": True,
        "profile": None,
    }
    await json_set(f"user:{user_id}", ".", user)
    token = create_access_token({"sub": user_id})
    return user, token
