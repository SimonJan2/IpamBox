import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.redis import get_redis
from app.core.security import hash_password
from app.models.user import User, UserRole

PASSWORD = "rbac-test-pw1"


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


@pytest.fixture
def fake_arq(monkeypatch):
    class _Job:
        job_id = "fake-arq-job"

    class _Pool:
        async def enqueue_job(self, *a, **k):
            return _Job()

        async def close(self):
            pass

    async def _pool():
        return _Pool()

    monkeypatch.setattr("app.api.v1.scans.get_arq_pool", _pool)
    monkeypatch.setattr("app.api.v1.maintenance.get_arq_pool", _pool)


async def mkuser(session: AsyncSession, username: str, role: UserRole) -> User:
    u = User(username=username, password_hash=hash_password(PASSWORD), role=role)
    session.add(u)
    await session.commit()
    await session.refresh(u)
    return u


async def login(client: AsyncClient, username: str) -> None:
    r = await client.post(
        "/api/v1/auth/login", json={"username": username, "password": PASSWORD}
    )
    assert r.status_code == 200, r.text


def other_client() -> AsyncClient:
    from app.main import app

    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


# ---------------------------------------------------------------- status / me


async def test_status_exposes_role_and_permissions(client: AsyncClient, auth_on):
    r = await client.post(
        "/api/v1/auth/setup", json={"username": "admin", "password": PASSWORD}
    )
    assert r.status_code == 201

    status = (await client.get("/api/v1/auth/status")).json()
    assert status["role"] == "admin"
    for perm in (
        "data:read",
        "data:write",
        "data:delete",
        "backup:access",
        "system:admin",
        "users:manage",
    ):
        assert perm in status["permissions"]

    me = (await client.get("/api/v1/auth/me")).json()
    assert me["username"] == "admin"
    assert me["role"] == "admin"
    assert "users:manage" in me["permissions"]


async def test_setup_grants_admin_and_second_setup_blocked(
    client: AsyncClient, session: AsyncSession, auth_on
):
    r = await client.post(
        "/api/v1/auth/setup", json={"username": "first", "password": PASSWORD}
    )
    assert r.status_code == 201
    u = await session.scalar(select(User).where(User.username == "first"))
    assert u.role == UserRole.ADMIN

    r = await client.post(
        "/api/v1/auth/setup", json={"username": "second", "password": PASSWORD}
    )
    assert r.status_code == 409


# --------------------------------------------------------------------- viewer


async def test_viewer_is_read_only(
    client: AsyncClient, session: AsyncSession, auth_on
):
    await mkuser(session, "v", UserRole.VIEWER)
    await login(client, "v")

    # reads fine
    assert (await client.get("/api/v1/sites")).status_code == 200
    assert (await client.get("/api/v1/vrfs")).status_code == 200
    assert (await client.get("/api/v1/settings")).status_code == 200
    assert (await client.get("/api/v1/dashboard/stats")).status_code == 200

    # writes/deletes -> 403
    assert (
        await client.post("/api/v1/sites", json={"name": "x"})
    ).status_code == 403
    assert (
        await client.patch("/api/v1/sites/1", json={"name": "y"})
    ).status_code == 403
    assert (await client.delete("/api/v1/sites/1")).status_code == 403
    assert (
        await client.post(
            "/api/v1/addresses/bulk",
            json={"ids": [1], "action": "set_status", "status": "active"},
        )
    ).status_code == 403
    assert (await client.post("/api/v1/scans", json={})).status_code == 403

    # backups / user admin / system -> 403
    assert (await client.get("/api/v1/backup/files")).status_code == 403
    assert (
        await client.post("/api/v1/maintenance/backup-now")
    ).status_code == 403
    assert (await client.get("/api/v1/users")).status_code == 403
    assert (
        await client.patch("/api/v1/settings", json={"backup_keep": 7})
    ).status_code == 403


# ---------------------------------------------------------------- contributor


async def test_contributor_can_write_but_not_delete(
    client: AsyncClient, session: AsyncSession, auth_on
):
    await mkuser(session, "c", UserRole.CONTRIBUTOR)
    await login(client, "c")

    r = await client.post("/api/v1/sites", json={"name": "hq"})
    assert r.status_code == 201
    site_id = r.json()["id"]

    assert (
        await client.patch(f"/api/v1/sites/{site_id}", json={"name": "hq2"})
    ).status_code == 200

    # all deletion surfaces blocked
    assert (await client.delete(f"/api/v1/sites/{site_id}")).status_code == 403
    assert (
        await client.post(
            "/api/v1/addresses/bulk", json={"ids": [1], "action": "delete"}
        )
    ).status_code == 403

    # backups and user admin blocked
    assert (await client.get("/api/v1/backup/files")).status_code == 403
    assert (
        await client.post("/api/v1/maintenance/backup-now")
    ).status_code == 403
    assert (
        await client.post(
            "/api/v1/users",
            json={"username": "nope", "password": "password1", "role": "admin"},
        )
    ).status_code == 403
    assert (
        await client.patch("/api/v1/settings", json={"backup_keep": 7})
    ).status_code == 403


# ------------------------------------------------------------------ operator


async def test_operator_data_and_backup_but_no_admin(
    client: AsyncClient, session: AsyncSession, auth_on, fake_arq
):
    await mkuser(session, "op", UserRole.OPERATOR)
    await login(client, "op")

    # full data CRUD
    r = await client.post("/api/v1/sites", json={"name": "hq"})
    assert r.status_code == 201
    site_id = r.json()["id"]
    assert (
        await client.patch(f"/api/v1/sites/{site_id}", json={"name": "hq2"})
    ).status_code == 200
    assert (await client.delete(f"/api/v1/sites/{site_id}")).status_code == 204
    assert (
        await client.post(
            "/api/v1/addresses/bulk", json={"ids": [1], "action": "delete"}
        )
    ).status_code != 403  # 200/404/422 — never a permission error

    # backup access allowed (non-destructive)
    assert (await client.get("/api/v1/backup")).status_code == 200
    assert (await client.get("/api/v1/backup/files")).status_code == 200
    assert (
        await client.post("/api/v1/maintenance/backup-now")
    ).status_code == 202

    # destructive/system operations blocked
    assert (await client.post("/api/v1/backup/restore")).status_code == 403
    assert (
        await client.post("/api/v1/maintenance/purge-scans", json={})
    ).status_code == 403
    assert (
        await client.post(
            "/api/v1/maintenance/reset", json={"confirm": "RESET"}
        )
    ).status_code == 403
    assert (
        await client.patch("/api/v1/settings", json={"backup_keep": 7})
    ).status_code == 403

    # user administration blocked — no escalation possible
    assert (await client.get("/api/v1/users")).status_code == 403
    assert (
        await client.post(
            "/api/v1/users",
            json={"username": "x", "password": "password1", "role": "admin"},
        )
    ).status_code == 403
    me = (await client.get("/api/v1/auth/me")).json()
    op = await session.scalar(select(User).where(User.username == "op"))
    assert (
        await client.patch(f"/api/v1/users/{op.id}", json={"role": "admin"})
    ).status_code == 403


# ---------------------------------------------------------------------- admin


async def test_admin_full_access(
    client: AsyncClient, session: AsyncSession, auth_on, fake_arq
):
    await mkuser(session, "a", UserRole.ADMIN)
    await login(client, "a")

    assert (await client.get("/api/v1/users")).status_code == 200
    r = await client.post(
        "/api/v1/users",
        json={"username": "v1", "password": "password1", "role": "viewer"},
    )
    assert r.status_code == 201
    uid = r.json()["id"]

    r = await client.patch(f"/api/v1/users/{uid}", json={"role": "operator"})
    assert r.status_code == 200
    assert r.json()["role"] == "operator"

    assert (await client.delete(f"/api/v1/users/{uid}")).status_code == 204
    assert (
        await client.patch("/api/v1/settings", json={"backup_keep": 7})
    ).status_code == 200
    assert (await client.get("/api/v1/backup/files")).status_code == 200
    assert (
        await client.post("/api/v1/maintenance/backup-now")
    ).status_code == 202


# ----------------------------------------------------------------- guardrails


async def test_sole_admin_cannot_demote_or_delete_self(
    client: AsyncClient, session: AsyncSession, auth_on
):
    admin = await mkuser(session, "a", UserRole.ADMIN)
    await login(client, "a")

    r = await client.patch(f"/api/v1/users/{admin.id}", json={"role": "viewer"})
    assert r.status_code == 409
    r = await client.delete(f"/api/v1/users/{admin.id}")
    assert r.status_code == 409

    # still an admin afterwards
    me = (await client.get("/api/v1/auth/me")).json()
    assert me["role"] == "admin"


async def test_admin_can_step_down_once_second_admin_exists(
    client: AsyncClient, session: AsyncSession, auth_on
):
    admin = await mkuser(session, "a", UserRole.ADMIN)
    await mkuser(session, "b", UserRole.ADMIN)
    await login(client, "a")

    r = await client.patch(f"/api/v1/users/{admin.id}", json={"role": "viewer"})
    assert r.status_code == 200

    # role change revoked the old session — re-auth required
    assert (await client.get("/api/v1/users")).status_code == 401


async def test_role_change_revokes_target_sessions(
    client: AsyncClient, session: AsyncSession, auth_on
):
    await mkuser(session, "a", UserRole.ADMIN)
    op = await mkuser(session, "op", UserRole.OPERATOR)
    await login(client, "a")

    async with other_client() as oc:
        await login(oc, "op")
        assert (await oc.get("/api/v1/sites")).status_code == 200

        r = await client.patch(f"/api/v1/users/{op.id}", json={"role": "viewer"})
        assert r.status_code == 200

        # operator's session is dead even though it was valid moments ago
        assert (await oc.get("/api/v1/sites")).status_code == 401


async def test_delete_user_revokes_sessions(
    client: AsyncClient, session: AsyncSession, auth_on
):
    await mkuser(session, "a", UserRole.ADMIN)
    v = await mkuser(session, "v", UserRole.VIEWER)
    await login(client, "a")

    async with other_client() as oc:
        await login(oc, "v")
        assert (await oc.get("/api/v1/sites")).status_code == 200

        assert (await client.delete(f"/api/v1/users/{v.id}")).status_code == 204
        assert (await oc.get("/api/v1/sites")).status_code == 401


async def test_admin_cannot_delete_last_user(
    client: AsyncClient, session: AsyncSession, auth_on
):
    admin = await mkuser(session, "a", UserRole.ADMIN)
    await login(client, "a")
    assert (await client.delete(f"/api/v1/users/{admin.id}")).status_code == 409


# ------------------------------------------------------------- insecure mode


async def test_insecure_mode_bypasses_all_guards(client: AsyncClient):
    """allow_insecure keeps full access (existing behavior preserved)."""
    assert (await client.get("/api/v1/users")).status_code == 200
    status = (await client.get("/api/v1/auth/status")).json()
    assert status["allow_insecure"] is True
    assert "users:manage" in status["permissions"]


# ------------------------------------------------------- users-inclusive backup


async def test_operator_cannot_export_users(
    client: AsyncClient, session: AsyncSession, auth_on
):
    await mkuser(session, "op", UserRole.OPERATOR)
    await login(client, "op")

    # plain backup is fine for operators
    assert (await client.get("/api/v1/backup")).status_code == 200
    # ...but a users-inclusive export carries password hashes -> admin only
    r = await client.get("/api/v1/backup", params={"include_users": 1})
    assert r.status_code == 403


async def test_restore_users_backup_keeps_admin_session(
    client: AsyncClient, session: AsyncSession, auth_on
):
    await mkuser(session, "a", UserRole.ADMIN)
    op = await mkuser(session, "op", UserRole.OPERATOR)
    await login(client, "a")

    r = await client.get("/api/v1/backup", params={"include_users": 1})
    assert r.status_code == 200

    # non-admin changes on the target are replaced by the restore
    await session.delete(op)
    await session.commit()

    r = await client.post(
        "/api/v1/backup/restore",
        content=r.content,
        headers={"content-type": "application/gzip"},
    )
    assert r.status_code == 200, r.text

    # the restoring admin's session still maps to their preserved user id
    me = await client.get("/api/v1/auth/me")
    assert me.status_code == 200
    assert me.json()["username"] == "a"

    # and the non-admin set was replaced from the file
    restored = await session.scalar(select(User).where(User.username == "op"))
    assert restored is not None and restored.role == UserRole.OPERATOR
