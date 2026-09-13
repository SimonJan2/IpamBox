import pytest
from httpx import AsyncClient

from app.core.config import get_settings
from app.core.redis import get_redis


@pytest.fixture
async def auth_on():
    """Turn auth on for a test, restore insecure mode after, and flush
    session/lockout keys so tests don't leak state into each other."""
    settings = get_settings()
    settings.ipambox_allow_insecure = False
    r = get_redis()
    try:
        yield
    finally:
        settings.ipambox_allow_insecure = True
        for pattern in ("ipam:session:*", "ipam:loginfails:*", "ipam:lockout:*"):
            async for key in r.scan_iter(pattern):
                await r.delete(key)
        await r.aclose()


async def test_endpoints_require_auth(client: AsyncClient, auth_on):
    assert (await client.get("/api/v1/prefixes")).status_code == 401
    assert (await client.get("/api/v1/sites")).status_code == 401
    # auth routes themselves stay open
    assert (await client.get("/api/v1/auth/status")).status_code == 200


async def test_setup_login_flow(client: AsyncClient, auth_on):
    status = (await client.get("/api/v1/auth/status")).json()
    assert status["initialized"] is False
    assert status["authenticated"] is False

    r = await client.post(
        "/api/v1/auth/setup", json={"username": "admin", "password": "secretpw1"}
    )
    assert r.status_code == 201
    assert "ipambox_session" in r.cookies

    # setup refuses to run twice
    r = await client.post(
        "/api/v1/auth/setup", json={"username": "x", "password": "anotherpw1"}
    )
    assert r.status_code == 409

    # the session set by setup is already authenticated
    assert (await client.get("/api/v1/sites")).status_code == 200

    # logout, then protected route is refused
    await client.post("/api/v1/auth/logout")
    assert (await client.get("/api/v1/sites")).status_code == 401

    # wrong password -> 401, right password -> cookie
    r = await client.post(
        "/api/v1/auth/login", json={"username": "admin", "password": "wrong"}
    )
    assert r.status_code == 401
    r = await client.post(
        "/api/v1/auth/login", json={"username": "admin", "password": "secretpw1"}
    )
    assert r.status_code == 200
    assert (await client.get("/api/v1/auth/me")).json()["username"] == "admin"


async def test_login_lockout(client: AsyncClient, auth_on):
    await client.post(
        "/api/v1/auth/setup", json={"username": "admin", "password": "secretpw1"}
    )
    await client.post("/api/v1/auth/logout")
    for _ in range(5):
        r = await client.post(
            "/api/v1/auth/login", json={"username": "admin", "password": "nope"}
        )
    assert r.status_code == 429
    # even the right password is refused while locked out
    r = await client.post(
        "/api/v1/auth/login", json={"username": "admin", "password": "secretpw1"}
    )
    assert r.status_code == 429
