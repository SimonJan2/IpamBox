import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import get_settings
from app.core.redis import close_redis, get_redis


@pytest.fixture
async def auth_on():
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
        await close_redis()


async def test_users_crud_and_guards(client: AsyncClient):
    # insecure test mode: no "self" user — only the last-user guard applies
    r = await client.post(
        "/api/v1/users", json={"username": "bob", "password": "password1"}
    )
    assert r.status_code == 201, r.text
    uid = r.json()["id"]

    r = await client.post(
        "/api/v1/users", json={"username": "bob", "password": "password1"}
    )
    assert r.status_code == 409

    r = await client.patch(f"/api/v1/users/{uid}", json={"username": "bobby"})
    assert r.json()["username"] == "bobby"

    # last remaining user can't be deleted
    r = await client.delete(f"/api/v1/users/{uid}")
    assert r.status_code == 409

    r = await client.post(
        "/api/v1/users", json={"username": "carol", "password": "password2"}
    )
    assert r.status_code == 201
    r = await client.delete(f"/api/v1/users/{uid}")
    assert r.status_code == 204

    users = (await client.get("/api/v1/users")).json()
    assert [u["username"] for u in users] == ["carol"]
    assert "password" not in users[0] and "password_hash" not in users[0]


async def test_change_password_and_sessions(client: AsyncClient, auth_on):
    await client.post(
        "/api/v1/auth/setup", json={"username": "admin", "password": "secretpw1"}
    )

    sessions = (await client.get("/api/v1/auth/sessions")).json()
    assert len(sessions) == 1
    assert sessions[0]["current"] is True

    # second session via a separate client
    from app.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c2:
        await c2.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "secretpw1"},
        )
        sessions = (await client.get("/api/v1/auth/sessions")).json()
        assert len(sessions) == 2

        r = await client.post(
            "/api/v1/auth/change-password",
            json={
                "current_password": "wrong",
                "new_password": "newpassword1",
            },
        )
        assert r.status_code == 403

        r = await client.post(
            "/api/v1/auth/change-password",
            json={
                "current_password": "secretpw1",
                "new_password": "newpassword1",
                "logout_others": True,
            },
        )
        assert r.status_code == 200
        assert r.json()["revoked_sessions"] == 1

        # c2's session is dead; ours survives
        assert (await c2.get("/api/v1/users")).status_code == 401
        assert (await client.get("/api/v1/users")).status_code == 200

        # new password logs in
        r = await c2.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "newpassword1"},
        )
        assert r.status_code == 200


async def test_revoke_session_endpoint(client: AsyncClient, auth_on):
    await client.post(
        "/api/v1/auth/setup", json={"username": "admin", "password": "secretpw1"}
    )
    from app.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c2:
        await c2.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "secretpw1"},
        )
        sessions = (await client.get("/api/v1/auth/sessions")).json()
        other = next(s for s in sessions if not s["current"])

        r = await client.delete(f"/api/v1/auth/sessions/{other['id']}")
        assert r.status_code == 204
        assert (await c2.get("/api/v1/users")).status_code == 401

        # current session can't be revoked via this endpoint
        cur = (await client.get("/api/v1/auth/sessions")).json()[0]
        r = await client.delete(f"/api/v1/auth/sessions/{cur['id']}")
        assert r.status_code == 409
