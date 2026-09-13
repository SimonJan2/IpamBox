import os
import subprocess

# Tests run without auth by default; test_auth flips it back on per-test.
os.environ["IPAMBOX_ALLOW_INSECURE"] = "true"

import asyncpg
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

TEST_DB_NAME = "ipam_test"


def _base_dsn() -> str:
    url = os.environ.get("DATABASE_URL", "postgresql+asyncpg://ipam:ipam@localhost:5432/ipam")
    return url.replace("postgresql+asyncpg://", "postgresql://")


def test_url() -> str:
    base = _base_dsn().rsplit("/", 1)[0]
    return f"{base}/{TEST_DB_NAME}".replace("postgresql://", "postgresql+asyncpg://")


@pytest_asyncio.fixture(scope="session", loop_scope="session", autouse=True)
async def _prepare_test_db():
    """Create the test database (if missing) and run migrations against it."""
    root = _base_dsn().rsplit("/", 1)[0]
    conn = await asyncpg.connect(f"{root}/postgres")
    try:
        exists = await conn.fetchval("SELECT 1 FROM pg_database WHERE datname=$1", TEST_DB_NAME)
        if not exists:
            await conn.execute(f'CREATE DATABASE "{TEST_DB_NAME}"')
    finally:
        await conn.close()

    env = dict(os.environ, DATABASE_URL=test_url())
    subprocess.run(["alembic", "upgrade", "head"], check=True, env=env, cwd="/app")
    yield


@pytest_asyncio.fixture
async def engine(_prepare_test_db):
    # function-scoped: connections live on the test's own event loop
    e = create_async_engine(test_url())
    yield e
    await e.dispose()


@pytest_asyncio.fixture
async def sf(engine):
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture
async def session(engine, sf):
    async with engine.begin() as conn:
        await conn.execute(
            text(
                "TRUNCATE scan_jobs, ip_addresses, ip_ranges, prefixes, vrfs, "
                "sites, users, change_log, tag_assignments, tags, vlans, "
                "vlan_groups RESTART IDENTITY CASCADE"
            )
        )
        await conn.execute(
            text("INSERT INTO vrfs (name, description) VALUES ('Global', 'Default global routing table')")
        )
    async with sf() as s:
        yield s


@pytest_asyncio.fixture
async def client(session):
    from app.core.db import get_session
    from app.main import app

    async def _override():
        yield session

    app.dependency_overrides[get_session] = _override
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()
