import redis.asyncio as aioredis
from arq import create_pool
from arq.connections import ArqRedis, RedisSettings

from app.core.config import get_settings

settings = get_settings()


def redis_settings_from_url(url: str) -> RedisSettings:
    return RedisSettings.from_dsn(url)


def get_redis() -> aioredis.Redis:
    return aioredis.from_url(settings.redis_url, decode_responses=True)


async def get_arq_pool() -> ArqRedis:
    return await create_pool(redis_settings_from_url(settings.redis_url))
