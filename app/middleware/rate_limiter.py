import time
from fastapi import HTTPException, status
import redis.asyncio as redis

class RateLimiter:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    async def check_rate_limit(self, user_id: str, limit: int = 100, window_sec: int = 60) -> bool:
        """
        Implements a Sliding-Window rate limiter using Redis Sorted Sets (ZSET).
        """
        now = time.time()
        clear_before = now - window_sec
        key = f"rate_limit:{user_id}"

        async with self.redis.pipeline(transaction=True) as pipe:
            # 1. Clear timestamps older than the sliding window
            pipe.zremrangebyscore(key, 0, clear_before)
            # 2. Add current timestamp to set
            pipe.zadd(key, {str(now): now})
            # 3. Count total requests within current window
            pipe.zcard(key)
            # 4. Set key expiration to auto-cleanup inactive users
            pipe.expire(key, window_sec + 1)
            
            _, _, request_count, _ = await pipe.execute()

        if request_count > limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Maximum {limit} requests per {window_sec} seconds."
            )
        return True