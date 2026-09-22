"""Rack elevations: CRUD, face-aware collision rules, Rackula import."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.redis import get_redis
from app.core.security import hash_password
from app.models.user import User, UserRole
from app.services.backup import BACKUP_TABLES

PASSWORD = "rack-test-pw1"


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
        await r.aclose()


async def _rack(client: AsyncClient, **kw) -> dict:
    body = {"name": "R1", "height_u": 12, "width": 19, **kw}
    r = await client.post("/api/v1/racks", json=body)
    assert r.status_code == 201, r.text
    return r.json()


async def _dev(client: AsyncClient, rack_id: int, **kw) -> dict:
    body = {"name": "srv", "u_position": 1, "u_height": 1, "face": "front", **kw}
    r = await client.post(f"/api/v1/racks/{rack_id}/devices", json=body)
    assert r.status_code == 201, r.text
    return r.json()


# --------------------------------------------------------------------- CRUD


async def test_rack_crud_happy_path(client: AsyncClient):
    site = (await client.post("/api/v1/sites", json={"name": "DC1"})).json()
    rack = await _rack(
        client, name="A-01", site_id=site["id"], room="Hall 2", height_u=42
    )
    assert rack["device_count"] == 0 and rack["used_u"] == 0
    assert rack["display_color"] is None

    d = await _dev(
        client,
        rack["id"],
        name="sw-core",
        device_type="switch-48p",
        u_position=40,
        colour="#38bdf8",
    )
    assert d["face"] == "front" and d["source"] == "manual"

    detail = (await client.get(f"/api/v1/racks/{rack['id']}")).json()
    assert detail["device_count"] == 1 and detail["used_u"] == 1
    assert [x["name"] for x in detail["devices"]] == ["sw-core"]

    r = await client.patch(
        f"/api/v1/racks/{rack['id']}", json={"room": "Hall 3", "pinned": True}
    )
    assert r.status_code == 200 and r.json()["room"] == "Hall 3"

    listed = (await client.get("/api/v1/racks", params={"q": "hall 3"})).json()
    assert listed["total"] == 1 and listed["items"][0]["device_count"] == 1

    assert (await client.delete(f"/api/v1/racks/{rack['id']}")).status_code == 204
    assert (await client.get(f"/api/v1/racks/{rack['id']}")).status_code == 404


async def test_device_edit_and_delete(client: AsyncClient):
    rack = await _rack(client)
    d = await _dev(client, rack["id"], u_position=3)

    r = await client.patch(
        f"/api/v1/racks/{rack['id']}/devices/{d['id']}",
        json={"u_position": 4, "u_height": 2},
    )
    assert r.status_code == 200, r.text
    assert r.json()["u_height"] == 2

    # patching without moving must not conflict with itself
    r = await client.patch(
        f"/api/v1/racks/{rack['id']}/devices/{d['id']}", json={"name": "srv2"}
    )
    assert r.status_code == 200

    assert (
        await client.delete(f"/api/v1/racks/{rack['id']}/devices/{d['id']}")
    ).status_code == 204
    detail = (await client.get(f"/api/v1/racks/{rack['id']}")).json()
    assert detail["devices"] == []


async def test_viewer_cannot_write_racks(
    client: AsyncClient, session: AsyncSession, auth_on
):
    u = User(
        username="v", password_hash=hash_password(PASSWORD), role=UserRole.VIEWER
    )
    session.add(u)
    await session.commit()
    r = await client.post(
        "/api/v1/auth/login", json={"username": "v", "password": PASSWORD}
    )
    assert r.status_code == 200

    assert (await client.get("/api/v1/racks")).status_code == 200
    assert (
        await client.post("/api/v1/racks", json={"name": "x"})
    ).status_code == 403
    assert (
        await client.post("/api/v1/racks/1/devices", json={"name": "d", "u_position": 1})
    ).status_code == 403
    assert (
        await client.post(
            "/api/v1/racks/1/devices/import", json={"mode": "merge", "devices": []}
        )
    ).status_code == 403
    assert (await client.delete("/api/v1/racks/1")).status_code == 403


# --------------------------------------------------------------- collisions


async def test_front_rear_same_u_is_legal(client: AsyncClient):
    rack = await _rack(client)
    await _dev(client, rack["id"], name="front-srv", u_position=5, face="front")
    r = await client.post(
        f"/api/v1/racks/{rack['id']}/devices",
        json={"name": "rear-pdu", "u_position": 5, "face": "rear"},
    )
    assert r.status_code == 201


async def test_same_face_overlap_conflicts(client: AsyncClient):
    rack = await _rack(client)
    await _dev(client, rack["id"], name="sw-a", u_position=5, face="front")
    r = await client.post(
        f"/api/v1/racks/{rack['id']}/devices",
        json={"name": "sw-b", "u_position": 5, "face": "front"},
    )
    assert r.status_code == 409
    assert "sw-a" in r.json()["detail"]


async def test_both_face_collides_with_everything(client: AsyncClient):
    rack = await _rack(client)
    await _dev(client, rack["id"], name="ups", u_position=2, u_height=2, face="both")
    for face in ("front", "rear", "both"):
        r = await client.post(
            f"/api/v1/racks/{rack['id']}/devices",
            json={"name": f"d-{face}", "u_position": 3, "face": face},
        )
        assert r.status_code == 409, face


async def test_adjacent_u_allowed_and_multi_u_overlap_rejected(client: AsyncClient):
    rack = await _rack(client)
    await _dev(client, rack["id"], name="big", u_position=5, u_height=3)  # U5-7
    # adjacent below (U4) and above (U8) fit
    assert (
        await client.post(
            f"/api/v1/racks/{rack['id']}/devices",
            json={"name": "below", "u_position": 4, "face": "front"},
        )
    ).status_code == 201
    assert (
        await client.post(
            f"/api/v1/racks/{rack['id']}/devices",
            json={"name": "above", "u_position": 8, "face": "front"},
        )
    ).status_code == 201
    # overlapping the middle of the span does not
    r = await client.post(
        f"/api/v1/racks/{rack['id']}/devices",
        json={"name": "nope", "u_position": 6, "u_height": 2, "face": "front"},
    )
    assert r.status_code == 409


async def test_bounds_rejected(client: AsyncClient):
    rack = await _rack(client, height_u=4)
    for body in (
        {"name": "a", "u_position": 0},
        {"name": "b", "u_position": 5},
        {"name": "c", "u_position": 3, "u_height": 3},  # U3-5 > 4
    ):
        r = await client.post(f"/api/v1/racks/{rack['id']}/devices", json=body)
        assert r.status_code == 422, body


async def test_shrinking_rack_below_devices_rejected(client: AsyncClient):
    rack = await _rack(client, height_u=10)
    await _dev(client, rack["id"], u_position=9, u_height=2)  # U9-10
    r = await client.patch(f"/api/v1/racks/{rack['id']}", json={"height_u": 8})
    assert r.status_code == 422


# ------------------------------------------------------------------- import


def _imports():
    return [
        {"name": "fw-1", "u_position": 10, "face": "front"},
        {"name": "sw-1", "u_position": 11, "face": "front"},
    ]


async def test_import_merge_skips_conflicts(client: AsyncClient):
    rack = await _rack(client)
    await _dev(client, rack["id"], name="existing", u_position=10, face="front")

    r = await client.post(
        f"/api/v1/racks/{rack['id']}/devices/import",
        json={"mode": "merge", "devices": _imports()},
    )
    assert r.status_code == 200, r.text
    out = r.json()
    assert out["created"] == 1
    assert len(out["skipped"]) == 1
    assert out["skipped"][0]["name"] == "fw-1"
    assert out["skipped"][0]["u_position"] == 10
    assert "existing" in out["skipped"][0]["reason"]

    detail = (await client.get(f"/api/v1/racks/{rack['id']}")).json()
    assert sorted(d["name"] for d in detail["devices"]) == ["existing", "sw-1"]
    assert detail["devices"][0]["source"] == "manual"
    assert detail["devices"][1]["source"] == "rackula"


async def test_import_replace_wipes_first(client: AsyncClient):
    rack = await _rack(client)
    await _dev(client, rack["id"], name="old", u_position=1)

    r = await client.post(
        f"/api/v1/racks/{rack['id']}/devices/import",
        json={
            "mode": "replace",
            "devices": [{"name": "old", "u_position": 1, "face": "front"}],
        },
    )
    assert r.status_code == 200 and r.json()["created"] == 1

    detail = (await client.get(f"/api/v1/racks/{rack['id']}")).json()
    assert [d["name"] for d in detail["devices"]] == ["old"]
    assert detail["devices"][0]["source"] == "rackula"


async def test_import_skips_out_of_bounds(client: AsyncClient):
    rack = await _rack(client, height_u=2)
    r = await client.post(
        f"/api/v1/racks/{rack['id']}/devices/import",
        json={
            "mode": "merge",
            "devices": [
                {"name": "ok", "u_position": 1},
                {"name": "tall", "u_position": 9},
            ],
        },
    )
    out = r.json()
    assert out["created"] == 1
    assert out["skipped"][0]["name"] == "tall"


# ------------------------------------------------------------ integrations


async def test_rack_and_device_changes_are_audited(client: AsyncClient):
    rack = await _rack(client, name="Audited")
    d = await _dev(client, rack["id"], name="srv", u_position=1)
    await client.patch(
        f"/api/v1/racks/{rack['id']}/devices/{d['id']}", json={"u_position": 2}
    )
    await client.delete(f"/api/v1/racks/{rack['id']}")

    rack_log = (
        await client.get("/api/v1/changelog", params={"object_type": "Rack"})
    ).json()["items"]
    assert [e["action"] for e in rack_log] == ["delete", "create"]
    assert rack_log[1]["object_repr"] == "Audited"

    dev_log = (
        await client.get("/api/v1/changelog", params={"object_type": "RackDevice"})
    ).json()["items"]
    actions = sorted(e["action"] for e in dev_log)
    assert actions == ["create", "delete", "update"]
    assert dev_log[0]["object_repr"] == "srv@U2"


def test_backup_registry_covers_rack_tables():
    names = {spec.name for spec in BACKUP_TABLES}
    assert "racks" in names and "rack_devices" in names
    # rack_devices restores after racks + its SET NULL parents
    order = [spec.name for spec in BACKUP_TABLES]
    assert order.index("racks") > order.index("sites")
    for parent in ("racks", "assets", "ip_addresses"):
        assert order.index("rack_devices") > order.index(parent)


async def test_search_finds_rack_by_name_room_and_device(client: AsyncClient):
    rack = await _rack(client, name="Colo-A", room="Cage 7")
    await _dev(client, rack["id"], name="unifi-aggregation", u_position=1)

    for q, why in (("colo-a", "name"), ("cage", "room"), ("unifi", "device")):
        out = (await client.get("/api/v1/search", params={"q": q})).json()
        assert any(r["id"] == rack["id"] for r in out["racks"]), why
