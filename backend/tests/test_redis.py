"""W6: one shared Redis client + ARQ pool per loop — never per operation.

Callers used to build a fresh client for every auth check / progress tick /
cancel poll and a fresh ARQ pool per enqueue. get_redis()/get_arq_pool() now
return loop-bound singletons closed only at shutdown.
"""
from app.core.redis import close_arq_pool, close_redis, get_arq_pool, get_redis


async def test_get_redis_returns_one_shared_client():
    r1 = get_redis()
    assert get_redis() is r1
    # closing resets the singleton — the next call builds a fresh client
    await close_redis()
    assert get_redis() is not r1
    await close_redis()


async def test_get_arq_pool_returns_one_shared_pool(monkeypatch):
    """The pool is created once per loop — verified without touching Redis
    by faking arq.create_pool."""
    import app.core.redis as redis_mod

    created = []

    async def fake_create_pool(settings):
        created.append(settings)
        return object()

    monkeypatch.setattr(redis_mod, "create_pool", fake_create_pool)
    try:
        p1 = await get_arq_pool()
        assert await get_arq_pool() is p1
        assert len(created) == 1
    finally:
        # reset the module-level singleton so later tests aren't confused
        redis_mod._arq_pool = None
        redis_mod._arq_loop = None
