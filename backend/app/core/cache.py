"""
Redis Caching Module.
Handles connection to Redis and provides caching utilities.
"""
import json
import redis.asyncio as redis
from typing import Optional, Any
from functools import lru_cache

from .config import settings
from .logging import logger


class CacheService:
    """Service for caching data in Redis."""
    
    def __init__(self):
        self._redis: Optional[redis.Redis] = None
        self.enabled = False
        
        if settings.REDIS_URL:
            try:
                self._redis = redis.from_url(
                    settings.REDIS_URL, 
                    encoding="utf-8", 
                    decode_responses=True
                )
                self.enabled = True
                logger.info(f"Redis caching enabled: {settings.REDIS_URL}")
            except Exception as e:
                logger.warning(f"Failed to initialize Redis: {e}")
                self.enabled = False
        else:
            logger.info("Redis caching disabled (no REDIS_URL provided)")

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.enabled or not self._redis:
            return None
            
        try:
            value = await self._redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None

    async def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        """Set value in cache."""
        if not self.enabled or not self._redis:
            return False
            
        try:
            json_value = json.dumps(value)
            await self._redis.set(key, json_value, ex=expire)
            return True
        except Exception as e:
            logger.error(f"Redis set error: {e}")
            return False
            
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        if not self.enabled or not self._redis:
            return False
            
        try:
            await self._redis.delete(key)
            return True
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
            return False
            
    async def close(self):
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()


# Singleton instance
cache_service = CacheService()


def get_cache_service() -> CacheService:
    return cache_service
