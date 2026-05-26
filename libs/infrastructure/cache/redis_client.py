import logging
import json
from typing import Any, Optional, Dict
import redis.asyncio as aioredis

logger = logging.getLogger("hiqonis.cache")

class HiqonisCacheService:
    """Enterprise Caching Service with Redis Connection Pooling and Memory Fallback."""

    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url
        self.client: Optional[aioredis.Redis] = None
        self._memory_fallback: Dict[str, str] = {} # Mock fallback database

        if redis_url:
            try:
                # Initialize async connection pooling
                pool = aioredis.ConnectionPool.from_url(
                    redis_url, 
                    max_connections=20, 
                    decode_responses=True
                )
                self.client = aioredis.Redis(connection_pool=pool)
                logger.info("Successfully established async Redis connection pool.")
            except Exception as e:
                logger.error(f"Failed to initialize Redis. Falling back to memory cache. Error: {str(e)}")
                self.client = None
        else:
            logger.info("No Redis URL specified. Operating in-memory cache mode.")

    async def set_cache_key(self, key: str, value: Any, expire_seconds: int = 3600) -> bool:
        """Stores a serialized JSON value under a key with a TTL expiration."""
        serialized = json.dumps(value)
        if self.client:
            try:
                await self.client.set(key, serialized, ex=expire_seconds)
                return True
            except Exception as e:
                logger.error(f"Redis set failed for key '{key}': {str(e)}")
        
        # In-memory fallback
        self._memory_fallback[key] = serialized
        return True

    async def get_cache_key(self, key: str) -> Optional[Any]:
        """Retrieves and de-serializes a JSON value stored under a key."""
        serialized = None
        if self.client:
            try:
                serialized = await self.client.get(key)
            except Exception as e:
                logger.error(f"Redis get failed for key '{key}': {str(e)}")
        
        if not serialized:
            # Check in-memory fallback
            serialized = self._memory_fallback.get(key)

        if not serialized:
            return None

        try:
            return json.loads(serialized)
        except Exception as e:
            logger.error(f"Failed to deserialize cache key '{key}': {str(e)}")
            return None

    async def invalidate_cache_key(self, key: str) -> bool:
        """Deletes a key from the cache."""
        if self.client:
            try:
                await self.client.delete(key)
                return True
            except Exception as e:
                logger.error(f"Redis delete failed for key '{key}': {str(e)}")
        
        if key in self._memory_fallback:
            del self._memory_fallback[key]
        return True
