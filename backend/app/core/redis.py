import asyncio

import redis.asyncio as aioredis
from arq import create_pool
from arq.connections import ArqRedis, RedisSettings

from app.core.config import get_settings

settings = get_settings()


def redis_settings_from_url(url: str) -> RedisSettings:
    return RedisSettings.from_dsn(url)


# One client + one ARQ pool per event loop, created lazily on first use.
# redis.asyncio connections are bound to their loop, so a new loop (each
# pytest test gets one) gets a fresh client — the previous loop's pool is
# dead anyway. Lifespan/worker shutdown calls the close_* helpers.
_client: aioredis.Redis | None = None
_client_loop: asyncio.AbstractEventLoop | None = None
_arq_pool: ArqRedis | None = None
_arq_loop: asyncio.AbstractEventLoop | None = None


def get_redis() -> aioredis.Redis:
    """Shared process-wide Redis client. Do NOT aclose() it per call —
    connections come from its internal pool; the client lives until the
    process (or loop) shuts down."""
    global _client, _client_loop
    loop = asyncio.get_running_loop()
    if _client is None or _client_loop is not loop:
        _client = aioredis.from_url(settings.redis_url, decode_responses=True)
        _client_loop = loop
    return _client


async def close_redis() -> None:
    """Shut down the shared client — lifespan/worker shutdown only."""
    global _client, _client_loop
    client, _client, _client_loop = _client, None, None
    if client is not None:
        await client.aclose()


async def get_arq_pool() -> ArqRedis:
    """Shared ARQ pool — callers must not close() it per job."""
    global _arq_pool, _arq_loop
    loop = asyncio.get_running_loop()
    if _arq_pool is None or _arq_loop is not loop:
        _arq_pool = await create_pool(redis_settings_from_url(settings.redis_url))
        _arq_loop = loop
    return _arq_pool


async def close_arq_pool() -> None:
    global _arq_pool, _arq_loop
    pool, _arq_pool, _arq_loop = _arq_pool, None, None
    if pool is not None:
        await pool.close()
