import pytest
from libs.infrastructure.cache.redis_client import HiqonisCacheService

@pytest.mark.asyncio
async def test_cache_service_serialization_and_fallback():
    # 1. Initialize cache service in in-memory fallback mode
    cache = HiqonisCacheService(redis_url=None)
    
    test_key = "user_session_123"
    test_payload = {
        "user_id": "abc-999",
        "roles": ["agent", "viewer"],
        "is_active": True,
        "quota": 1000
    }

    # 2. Test Set Key
    success_set = await cache.set_cache_key(test_key, test_payload, expire_seconds=60)
    assert success_set is True

    # 3. Test Get Key
    retrieved_payload = await cache.get_cache_key(test_key)
    assert retrieved_payload is not None
    assert retrieved_payload["user_id"] == "abc-999"
    assert retrieved_payload["is_active"] is True
    assert "agent" in retrieved_payload["roles"]

    # 4. Test Invalidation
    success_delete = await cache.invalidate_cache_key(test_key)
    assert success_delete is True

    # 5. Verify deleted key is missing
    missing_payload = await cache.get_cache_key(test_key)
    assert missing_payload is None
