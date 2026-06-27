from redis.asyncio import Redis

from app.core.config import get_settings


class RedisConnectionManager:
    """Manage Redis client for future cache and queue infrastructure."""

    def __init__(self) -> None:
        self._client: Redis | None = None

    @property
    def client(self) -> Redis:
        if self._client is None:
            settings = get_settings()
            if not settings.redis_url:
                raise ValueError("REDIS_URL is not configured")
            self._client = Redis.from_url(settings.redis_url, encoding="utf-8", decode_responses=True)
        return self._client

    async def health_check(self) -> bool:
        try:
            await self.client.ping()
            return True
        except Exception:
            return False

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()


redis_manager = RedisConnectionManager()
