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
        for pattern in ("ipam:session:*", "ipam:loginfails*", "ipam:lockout*"):
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


def _xff(ip: str) -> dict[str, str]:
    return {"x-forwarded-for": ip}


async def test_lockout_keyed_per_user_ip_pair(client: AsyncClient, auth_on):
    """Five bad logins for one (user, ip) pair must not lock out other users
    on the same IP or the same user from another IP — the pre-W4 behavior
    (keyed on proxy IP alone) let anyone lock every user at once."""
    await client.post(
        "/api/v1/auth/setup", json={"username": "admin", "password": "secretpw1"}
    )
    await client.post("/api/v1/auth/logout")

    a_ip = "203.0.113.10"
    for _ in range(5):
        r = await client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "nope"},
            headers=_xff(a_ip),
        )
    assert r.status_code == 429

    # same IP, different user -> not locked
    r = await client.post(
        "/api/v1/auth/login",
        json={"username": "bob", "password": "nope"},
        headers=_xff(a_ip),
    )
    assert r.status_code == 401
    # same user, different IP -> not locked, correct password succeeds
    r = await client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "secretpw1"},
        headers=_xff("203.0.113.99"),
    )
    assert r.status_code == 200
    # the locked pair stays locked even with the right password
    r = await client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "secretpw1"},
        headers=_xff(a_ip),
    )
    assert r.status_code == 429


async def test_xff_only_honored_from_trusted_peer(
    client: AsyncClient, auth_on, monkeypatch
):
    """When the socket peer isn't in ipambox_trusted_proxies, a supplied XFF
    is ignored and the peer IP keys the counters — clients can't rotate XFF
    to dodge lockout."""
    settings = get_settings()
    monkeypatch.setattr(settings, "ipambox_trusted_proxies", "10.88.0.0/16")
    await client.post(
        "/api/v1/auth/setup", json={"username": "admin", "password": "secretpw1"}
    )
    await client.post("/api/v1/auth/logout")

    # five failures, each claiming a different XFF — all count against the
    # real peer (127.0.0.1), so the sixth is refused regardless of header
    for i in range(5):
        r = await client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "nope"},
            headers=_xff(f"203.0.113.{20 + i}"),
        )
    assert r.status_code == 429
    r = await client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "nope"},
        headers=_xff("203.0.113.200"),
    )
    assert r.status_code == 429


async def test_per_ip_aggregate_backstop(client: AsyncClient, auth_on, monkeypatch):
    """Spreading failures across many usernames from one IP trips the
    aggregate lock — and the 429 body is identical to a pair lock (no
    oracle for which counter fired)."""
    from app.core import security

    monkeypatch.setattr(security, "_LOCKOUT_IP_AFTER", 8)
    await client.post(
        "/api/v1/auth/setup", json={"username": "admin", "password": "secretpw1"}
    )
    await client.post("/api/v1/auth/logout")

    ip = "203.0.113.50"
    detail = None
    for i in range(8):
        r = await client.post(
            "/api/v1/auth/login",
            json={"username": f"user{i}", "password": "nope"},
            headers=_xff(ip),
        )
        if r.status_code == 429:
            detail = r.json()["detail"]
    assert detail is not None  # aggregate tripped on the 8th failure

    # a username that never failed from this IP is still refused
    r = await client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "secretpw1"},
        headers=_xff(ip),
    )
    assert r.status_code == 429
    assert r.json()["detail"] == detail

    # ...but the same user from another IP is unaffected
    r = await client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "secretpw1"},
        headers=_xff("203.0.113.60"),
    )
    assert r.status_code == 200
