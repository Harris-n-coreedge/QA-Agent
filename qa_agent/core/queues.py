"""
Redis queue connection helpers.
"""
import redis.asyncio as redis
from rq import Queue
from typing import Optional

from qa_agent.core.config import settings


class QueueManager:
    """Manages Redis connections and RQ queues."""
    
    def __init__(self):
        self._redis: Optional[redis.Redis] = None
        self._queue: Optional[Queue] = None
    
    async def get_redis(self) -> redis.Redis:
        """Get Redis connection."""
        if self._redis is None:
            self._redis = redis.from_url(settings.REDIS_URL)
        return self._redis
    
    def get_queue(self) -> Queue:
        """Get RQ queue."""
        if self._queue is None:
            redis_conn = redis.from_url(settings.REDIS_URL)
            self._queue = Queue(connection=redis_conn)
        return self._queue
    
    async def close(self) -> None:
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()


# Global queue manager
queue_manager = QueueManager()


async def get_redis() -> redis.Redis:
    """Get Redis connection dependency."""
    return await queue_manager.get_redis()


def get_queue() -> Queue:
    """Get RQ queue dependency."""
    return queue_manager.get_queue()


async def close_queue_connections() -> None:
    """Close queue connections."""
    await queue_manager.close()
