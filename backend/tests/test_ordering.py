"""Global row ordering: POST /{entity}/reorder + pinned rows.

Covered on both router styles — circuits ride the _crud_router factory,
sites/tags/vrfs/vlans are hand-written.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.redis import get_redis
from app.core.security import hash_password
from app.models.change_log import ChangeLog
from app.models.user import User, UserRole

PASSWORD = "order-test-pw1"


@pytest.fixture
async def auth_on():
    """Same pattern as test_rbac: flip auth on, restore + flush keys after."""
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


async def _mkuser(session: AsyncSession, username: str, role: UserRole) -> User:
    u = User(username=username, password_hash=hash_password(PASSWORD), role=role)
    session.add(u)
    await session.commit()
    return u


async def _login(client: AsyncClient, username: str) -> None:
    r = await client.post(
        "/api/v1/auth/login", json={"username": username, "password": PASSWORD}
    )
    assert r.status_code == 200, r.text


async def _mk_circuits(client: AsyncClient, names: list[str]) -> list[int]:
    ids = []
    for n in names:
        r = await client.post("/api/v1/circuits", json={"bezeq_circuit_id": n})
        assert r.status_code == 201, r.text
        ids.append(r.json()["id"])
    return ids


async def _circuit_order(client: AsyncClient) -> list[int]:
    return [c["id"] for c in (await client.get("/api/v1/circuits")).json()["items"]]


async def test_reorder_persists(client: AsyncClient):
    ids = await _mk_circuits(client, ["a", "b", "c"])
    assert await _circuit_order(client) == ids

    r = await client.post(
        "/api/v1/circuits/reorder", json={"ids": [ids[2], ids[0], ids[1]]}
    )
    assert r.status_code == 204, r.text

    assert await _circuit_order(client) == [ids[2], ids[0], ids[1]]
    # second fetch — the order is stored, not an in-memory fluke
    assert await _circuit_order(client) == [ids[2], ids[0], ids[1]]


async def test_reorder_subset_permutates_own_slots(client: AsyncClient):
    """Reordering a subset keeps the slots those rows already had — rows
    outside the submitted list are never displaced."""
    ids = await _mk_circuits(client, ["a", "b", "c", "d"])
    # Establish positions first — rows created via the API start unpositioned
    # (sort_order NULL); a full-scope reorder assigns 1..n.
    r = await client.post("/api/v1/circuits/reorder", json={"ids": ids})
    assert r.status_code == 204, r.text

    r = await client.post(
        "/api/v1/circuits/reorder", json={"ids": [ids[3], ids[1]]}
    )
    assert r.status_code == 204, r.text
    # d took b's slot, b took d's: a, d, c, b
    assert await _circuit_order(client) == [ids[0], ids[3], ids[2], ids[1]]


async def test_reorder_unknown_id_is_atomic(client: AsyncClient):
    ids = await _mk_circuits(client, ["a", "b"])

    r = await client.post(
        "/api/v1/circuits/reorder", json={"ids": [ids[1], 999999]}
    )
    assert r.status_code == 404
    assert await _circuit_order(client) == ids


async def test_reorder_rejects_duplicate_ids(client: AsyncClient):
    ids = await _mk_circuits(client, ["a", "b"])
    r = await client.post(
        "/api/v1/circuits/reorder", json={"ids": [ids[0], ids[0]]}
    )
    assert r.status_code == 400
    assert await _circuit_order(client) == ids


async def test_pinned_rows_sort_first(client: AsyncClient):
    ids = await _mk_circuits(client, ["a", "b", "c"])

    r = await client.patch(f"/api/v1/circuits/{ids[1]}", json={"pinned": True})
    assert r.status_code == 200 and r.json()["pinned"] is True

    assert await _circuit_order(client) == [ids[1], ids[0], ids[2]]

    # two pins: pinned group keeps manual order internally
    await client.patch(f"/api/v1/circuits/{ids[2]}", json={"pinned": True})
    assert await _circuit_order(client) == [ids[1], ids[2], ids[0]]


async def test_unpin_returns_row_to_its_old_slot(client: AsyncClient):
    ids = await _mk_circuits(client, ["a", "b", "c"])
    await client.patch(f"/api/v1/circuits/{ids[2]}", json={"pinned": True})
    assert await _circuit_order(client) == [ids[2], ids[0], ids[1]]

    await client.patch(f"/api/v1/circuits/{ids[2]}", json={"pinned": False})
    assert await _circuit_order(client) == ids


async def test_new_row_appends_after_positioned(client: AsyncClient):
    ids = await _mk_circuits(client, ["a", "b"])
    await client.post(
        "/api/v1/circuits/reorder", json={"ids": [ids[1], ids[0]]}
    )
    ids += await _mk_circuits(client, ["c"])
    # c is unpositioned (sort_order NULL) -> sinks to the end
    assert await _circuit_order(client) == [ids[1], ids[0], ids[2]]


async def test_reorder_handwritten_routers(client: AsyncClient):
    for name in ("x", "y", "z"):
        r = await client.post("/api/v1/sites", json={"name": name})
        assert r.status_code == 201, r.text
    site_ids = [s["id"] for s in (await client.get("/api/v1/sites")).json()["items"]]

    r = await client.post(
        "/api/v1/sites/reorder", json={"ids": list(reversed(site_ids))}
    )
    assert r.status_code == 204, r.text
    got = [s["id"] for s in (await client.get("/api/v1/sites")).json()["items"]]
    assert got == list(reversed(site_ids))

    # tags exercise the same path on a second hand-written router
    await client.post("/api/v1/tags", json={"name": "one"})
    await client.post("/api/v1/tags", json={"name": "two"})
    tag_ids = [t["id"] for t in (await client.get("/api/v1/tags")).json()]
    assert (
        await client.post(
            "/api/v1/tags/reorder", json={"ids": list(reversed(tag_ids))}
        )
    ).status_code == 204
    assert [
        t["id"] for t in (await client.get("/api/v1/tags")).json()
    ] == list(reversed(tag_ids))


async def test_reorder_and_pin_require_write_perm(
    client: AsyncClient, session: AsyncSession, auth_on
):
    await _mkuser(session, "v", UserRole.VIEWER)
    await _login(client, "v")

    assert (
        await client.post("/api/v1/sites/reorder", json={"ids": [1]})
    ).status_code == 403
    assert (
        await client.post("/api/v1/circuits/reorder", json={"ids": [1]})
    ).status_code == 403
    r = await client.post("/api/v1/sites", json={"name": "x"})
    assert r.status_code == 403  # viewers can't create either — sanity
    # pin toggle goes through PATCH — same DATA_WRITE gate as edits
    assert (
        await client.patch("/api/v1/sites/1", json={"pinned": True})
    ).status_code == 403


async def test_reorder_and_pin_leave_no_audit_trail(
    client: AsyncClient, session: AsyncSession
):
    r = await client.post("/api/v1/sites", json={"name": "HQ"})
    site = r.json()
    await client.patch(f"/api/v1/sites/{site['id']}", json={"pinned": True})
    await client.post("/api/v1/sites/reorder", json={"ids": [site["id"]]})

    entries = (
        await session.execute(
            select(ChangeLog).where(ChangeLog.object_type == "Site")
        )
    ).scalars().all()
    # the create entry only — sort_order/pinned churn is skipped, and a
    # reorder-only flush produces no update rows at all
    assert [e.action for e in entries] == ["create"]
    fields = {c["field"] for c in entries[0].changes}
    assert "sort_order" not in fields and "pinned" not in fields
