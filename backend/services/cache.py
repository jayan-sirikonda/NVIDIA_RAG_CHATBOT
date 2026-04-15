import redis.asyncio as redis
import hashlib
from backend.core.config import settings

class SemanticCache:
    def __init__(self):
        self.redis_client = None
        if settings.REDIS_URL:
            self.redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        else:
            # Fallback to local memory if Redis is absent (local dev mode without docker)
            self._local_cache = {}

    def _hash_query(self, query: str) -> str:
        return f"semantic_cache:{hashlib.sha256(query.strip().lower().encode()).hexdigest()}"

    async def get(self, query: str) -> str:
        key = self._hash_query(query)
        if self.redis_client:
            try:
                return await self.redis_client.get(key)
            except Exception:
                return None
        return self._local_cache.get(key)

    async def set(self, query: str, response: str, expire: int = 86400):
        """Cache the response for 24 hours by default."""
        key = self._hash_query(query)
        if self.redis_client:
            try:
                await self.redis_client.set(key, response, ex=expire)
            except Exception:
                pass
        else:
            self._local_cache[key] = response

# Singleton
cache = SemanticCache()
