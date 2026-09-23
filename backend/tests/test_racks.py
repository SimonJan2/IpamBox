"""Rack elevations: CRUD, face-aware collision rules, Rackula import."""

import ipaddress
import os
import subprocess
from datetime import datetime, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.redis import get_redis
from app.core.security import hash_password
from app.models.ip_address import IPAddress, IPStatus
from app.models.rack import Rack
from app.models.user import User, UserRole
from app.services.backup import BACKUP_TABLES

PASSWORD = "rack-test-pw1"


@pytest.fixture
async def auth_on():
    settings = get_settings()
    settings.ipambox_allow_insecure = False
    # httpx won't send a Secure cookie over http://test — force it off so
    # login flows work regardless of the container env.
    cookie_secure = settings.ipambox_cookie_secure
    settings.ipambox_cookie_secure = False
    r = get_redis()
    try:
        yield
    finally:
        settings.ipambox_allow_insecure = True
        settings.ipambox_cookie_secure = cookie_secure
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


async def test_patch_move_into_opposite_face_slot(client: AsyncClient):
    """check_placement runs on update too: a rear device may share a U with
    front gear, but flipping it to front (or moving front gear onto it)
    collides — the editor's drag/undo relies on this."""
    rack = await _rack(client)
    await _dev(client, rack["id"], name="front-srv", u_position=5, face="front")
    rear = await _dev(client, rack["id"], name="rear-pdu", u_position=2, face="rear")

    # rear legally moves into the front device's U (opposite faces share)
    r = await client.patch(
        f"/api/v1/racks/{rack['id']}/devices/{rear['id']}",
        json={"u_position": 5},
    )
    assert r.status_code == 200, r.text
    assert r.json()["u_position"] == 5

    # flipping that shared device to front at the same U collides
    r = await client.patch(
        f"/api/v1/racks/{rack['id']}/devices/{rear['id']}",
        json={"face": "front"},
    )
    assert r.status_code == 409
    assert "front-srv" in r.json()["detail"]

    # another front device can't move onto the same U either
    other = await _dev(client, rack["id"], name="sw", u_position=8, face="front")
    r = await client.patch(
        f"/api/v1/racks/{rack['id']}/devices/{other['id']}",
        json={"u_position": 5},
    )
    assert r.status_code == 409
    assert "front-srv" in r.json()["detail"]


async def test_patch_out_of_bounds_rejected(client: AsyncClient):
    rack = await _rack(client, height_u=6)
    d = await _dev(client, rack["id"], u_position=2, u_height=2)  # U2-3
    for body in (
        {"u_position": 0},  # below the schema floor
        {"u_position": 6},  # U6-7 exceeds a 6U rack
        {"u_position": 5, "u_height": 3},  # U5-7 exceeds a 6U rack
    ):
        r = await client.patch(
            f"/api/v1/racks/{rack['id']}/devices/{d['id']}", json=body
        )
        assert r.status_code == 422, body


# ------------------------------------------------------------- next-free-u


async def _next_free(client: AsyncClient, rack_id: int, **params) -> int | None:
    r = await client.get(f"/api/v1/racks/{rack_id}/next-free-u", params=params)
    assert r.status_code == 200, r.text
    return r.json()["u_position"]


async def test_next_free_u_empty_rack(client: AsyncClient):
    rack = await _rack(client)  # height_u=12
    assert await _next_free(client, rack["id"], height=1) == 1
    assert await _next_free(client, rack["id"], height=1, side="top") == 12
    assert await _next_free(client, rack["id"], height=4, side="top") == 9


async def test_next_free_u_face_aware(client: AsyncClient):
    rack = await _rack(client)
    await _dev(client, rack["id"], name="rear-pdu", u_position=1, face="rear")
    # a rear device does NOT block a front request at the same U
    assert await _next_free(client, rack["id"], height=1, face="front") == 1
    assert await _next_free(client, rack["id"], height=1, face="rear") == 2
    # `both` collides with everything: rear is now blocked at U1 AND U2
    await _dev(client, rack["id"], name="shelf", u_position=2, face="both")
    assert await _next_free(client, rack["id"], height=1, face="rear") == 3
    assert await _next_free(client, rack["id"], height=1, face="both") == 3
    # front still legally sits over the rear device at U1
    assert await _next_free(client, rack["id"], height=1, face="front") == 1


async def test_next_free_u_skips_fragmented_gaps(client: AsyncClient):
    rack = await _rack(client, height_u=6)
    for u in (1, 3, 5):
        await _dev(client, rack["id"], u_position=u, face="front")
    # three 1U gaps (U2, U4, U6) fit 1U but no contiguous 2U exists
    assert await _next_free(client, rack["id"], height=1) == 2
    assert await _next_free(client, rack["id"], height=2) is None


async def test_next_free_u_full_rack_returns_null(client: AsyncClient):
    rack = await _rack(client, height_u=2)
    await _dev(client, rack["id"], u_position=1, face="both")
    await _dev(client, rack["id"], name="b2", u_position=2, face="both")
    assert await _next_free(client, rack["id"], height=1, face="front") is None


async def test_next_free_u_validation(client: AsyncClient):
    rack = await _rack(client, height_u=4)
    for params in (
        {"height": 0},
        {"height": 5},  # exceeds rack height
        {"height": 1, "face": "side"},
        {"height": 1, "side": "middle"},
        {},  # height is required
    ):
        r = await client.get(
            f"/api/v1/racks/{rack['id']}/next-free-u", params=params
        )
        assert r.status_code == 422, params
    r = await client.get("/api/v1/racks/999/next-free-u", params={"height": 1})
    assert r.status_code == 404


async def test_next_free_u_viewer_can_read(
    client: AsyncClient, session: AsyncSession, auth_on
):
    rack = Rack(name="VR", height_u=6, width=19)
    session.add(rack)
    session.add(
        User(
            username="v",
            password_hash=hash_password(PASSWORD),
            role=UserRole.VIEWER,
        )
    )
    await session.commit()
    r = await client.post(
        "/api/v1/auth/login", json={"username": "v", "password": PASSWORD}
    )
    assert r.status_code == 200

    r = await client.get(
        f"/api/v1/racks/{rack.id}/next-free-u", params={"height": 1}
    )
    assert r.status_code == 200 and r.json()["u_position"] == 1


# ------------------------------------------------------------ device ↔ IP


async def test_detail_returns_linked_ip_health(
    client: AsyncClient, session: AsyncSession
):
    vrf_id = next(
        v["id"]
        for v in (await client.get("/api/v1/vrfs")).json()
        if v["name"] == "Global"
    )
    r = await client.post(
        "/api/v1/prefixes", json={"prefix": "10.99.0.0/24", "vrf_id": vrf_id}
    )
    assert r.status_code == 201, r.text
    seen = datetime(2026, 1, 2, 3, 4, 5, tzinfo=timezone.utc)
    ip = IPAddress(
        address="10.99.0.5",
        address_int=int(ipaddress.ip_address("10.99.0.5")),
        prefix_id=r.json()["id"],
        vrf_id=vrf_id,
        status=IPStatus.DISCOVERED,
        last_seen=seen,
    )
    session.add(ip)
    await session.commit()

    rack = await _rack(client)
    await _dev(client, rack["id"], name="with-ip", u_position=1, ip_address_id=ip.id)
    await _dev(client, rack["id"], name="no-ip", u_position=2)

    detail = (await client.get(f"/api/v1/racks/{rack['id']}")).json()
    by_name = {d["name"]: d for d in detail["devices"]}
    linked = by_name["with-ip"]
    assert linked["ip"]["id"] == ip.id
    assert linked["ip_status"] == "discovered"
    got = datetime.fromisoformat(linked["ip_last_seen"].replace("Z", "+00:00"))
    assert got == seen
    unlinked = by_name["no-ip"]
    assert unlinked["ip"] is None
    assert unlinked["ip_status"] is None and unlinked["ip_last_seen"] is None


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


# ---------------------------------------------------------------- carriers


async def _carrier(client: AsyncClient, rack_id: int, **kw) -> dict:
    body = {
        "name": "tray",
        "u_position": 5,
        "face": "front",
        "slot_layout": "halves",
        **kw,
    }
    r = await client.post(f"/api/v1/racks/{rack_id}/devices", json=body)
    assert r.status_code == 201, r.text
    return r.json()


async def _mount(
    client: AsyncClient, rack_id: int, carrier_id: int, slot: int, **kw
) -> dict:
    body = {"name": "kid", "carrier_id": carrier_id, "slot": slot, **kw}
    r = await client.post(f"/api/v1/racks/{rack_id}/devices", json=body)
    assert r.status_code == 201, r.text
    return r.json()


async def test_carrier_crud_and_mount(client: AsyncClient):
    rack = await _rack(client)
    tray = await _carrier(client, rack["id"], u_position=10, name="dual")
    assert tray["slot_layout"] == "halves"
    assert tray["carrier_id"] is None and tray["slot"] is None

    left = await _mount(client, rack["id"], tray["id"], 0, name="sw-l")
    assert left["carrier_id"] == tray["id"] and left["slot"] == 0
    # server derives u_position/face from the carrier, not the client payload
    right = await _mount(
        client, rack["id"], tray["id"], 1,
        name="sw-r", u_position=1, face="rear", u_height=1,
    )
    assert right["u_position"] == 10 and right["face"] == "front"

    detail = (await client.get(f"/api/v1/racks/{rack['id']}")).json()
    assert detail["device_count"] == 3 and detail["used_u"] == 1


async def test_carrier_slot_conflict_and_range(client: AsyncClient):
    rack = await _rack(client)
    tray = await _carrier(client, rack["id"], u_position=4)
    await _mount(client, rack["id"], tray["id"], 0, name="a")

    # duplicate slot -> 409
    r = await client.post(
        f"/api/v1/racks/{rack['id']}/devices",
        json={"name": "b", "u_position": 4, "carrier_id": tray["id"], "slot": 0},
    )
    assert r.status_code == 409 and "a" in r.json()["detail"]
    # beyond the layout's slot count -> 422 (halves has 0..1)
    r = await client.post(
        f"/api/v1/racks/{rack['id']}/devices",
        json={"name": "c", "u_position": 4, "carrier_id": tray["id"], "slot": 2},
    )
    assert r.status_code == 422
    # mounting into a non-carrier -> 422
    srv = await _dev(client, rack["id"], name="srv", u_position=8)
    r = await client.post(
        f"/api/v1/racks/{rack['id']}/devices",
        json={"name": "d", "u_position": 8, "carrier_id": srv["id"], "slot": 0},
    )
    assert r.status_code == 422
    # missing carrier -> 422
    r = await client.post(
        f"/api/v1/racks/{rack['id']}/devices",
        json={"name": "e", "u_position": 1, "carrier_id": 9999, "slot": 0},
    )
    assert r.status_code == 422


async def test_carrier_rules(client: AsyncClient):
    rack = await _rack(client)
    tray = await _carrier(client, rack["id"], u_position=4)

    # a carrier can't itself be a child (single level)
    r = await client.post(
        f"/api/v1/racks/{rack['id']}/devices",
        json={
            "name": "nested", "u_position": 6, "slot_layout": "halves",
            "carrier_id": tray["id"], "slot": 0,
        },
    )
    assert r.status_code == 422
    # child taller than its carrier -> 422
    r = await client.post(
        f"/api/v1/racks/{rack['id']}/devices",
        json={
            "name": "tall", "u_position": 4, "u_height": 2,
            "carrier_id": tray["id"], "slot": 0,
        },
    )
    assert r.status_code == 422
    # slot without carrier_id -> 422
    r = await client.post(
        f"/api/v1/racks/{rack['id']}/devices",
        json={"name": "orphan", "u_position": 3, "slot": 0},
    )
    assert r.status_code == 422
    # self-carrier on patch -> 422
    r = await client.patch(
        f"/api/v1/racks/{rack['id']}/devices/{tray['id']}",
        json={"carrier_id": tray["id"], "slot": 0},
    )
    assert r.status_code == 422


async def test_child_never_conflicts_with_rack_level(client: AsyncClient):
    """Children ride inside the carrier's span — it's the carrier (not the
    child) that blocks rack-level placements on its face."""
    rack = await _rack(client)
    tray = await _carrier(client, rack["id"], u_position=10, face="front")
    await _mount(client, rack["id"], tray["id"], 0, name="sw-l")
    await _mount(client, rack["id"], tray["id"], 1, name="sw-r")

    # the carrier blocks a front device at U10, regardless of children
    r = await client.post(
        f"/api/v1/racks/{rack['id']}/devices",
        json={"name": "srv", "u_position": 10, "face": "front"},
    )
    assert r.status_code == 409 and "tray" in r.json()["detail"]
    # opposite face shares the U legally
    r = await client.post(
        f"/api/v1/racks/{rack['id']}/devices",
        json={"name": "pdu", "u_position": 10, "face": "rear"},
    )
    assert r.status_code == 201


async def test_carrier_move_syncs_children(client: AsyncClient):
    rack = await _rack(client)
    tray = await _carrier(client, rack["id"], u_position=5, face="front")
    kid = await _mount(client, rack["id"], tray["id"], 0)

    r = await client.patch(
        f"/api/v1/racks/{rack['id']}/devices/{tray['id']}",
        json={"u_position": 8, "face": "rear"},
    )
    assert r.status_code == 200
    detail = (await client.get(f"/api/v1/racks/{rack['id']}")).json()
    child = next(d for d in detail["devices"] if d["id"] == kid["id"])
    assert child["u_position"] == 8 and child["face"] == "rear"


async def test_mount_unmount_and_reseat_via_patch(client: AsyncClient):
    rack = await _rack(client)
    tray = await _carrier(client, rack["id"], u_position=6)
    srv = await _dev(client, rack["id"], name="srv", u_position=2)

    # mount an existing rack-level device into a slot
    r = await client.patch(
        f"/api/v1/racks/{rack['id']}/devices/{srv['id']}",
        json={"carrier_id": tray["id"], "slot": 1},
    )
    assert r.status_code == 200, r.text
    got = r.json()
    assert got["carrier_id"] == tray["id"] and got["slot"] == 1
    assert got["u_position"] == 6  # inherited from the carrier

    # re-seat into the other slot
    r = await client.patch(
        f"/api/v1/racks/{rack['id']}/devices/{srv['id']}", json={"slot": 0}
    )
    assert r.status_code == 200 and r.json()["slot"] == 0

    # unmount back to a rack position
    r = await client.patch(
        f"/api/v1/racks/{rack['id']}/devices/{srv['id']}",
        json={"carrier_id": None, "u_position": 3},
    )
    got = r.json()
    assert r.status_code == 200, r.text
    assert got["carrier_id"] is None and got["slot"] is None
    assert got["u_position"] == 3


async def test_carrier_layout_shrink_strands_children(client: AsyncClient):
    rack = await _rack(client)
    tray = await _carrier(client, rack["id"], u_position=4)
    await _mount(client, rack["id"], tray["id"], 1, name="right-half")

    # halves -> shelf would strand the child in slot 1
    r = await client.patch(
        f"/api/v1/racks/{rack['id']}/devices/{tray['id']}",
        json={"slot_layout": "shelf"},
    )
    assert r.status_code == 422 and "right-half" in r.json()["detail"]
    # clearing the layout outright with children mounted also fails
    r = await client.patch(
        f"/api/v1/racks/{rack['id']}/devices/{tray['id']}",
        json={"slot_layout": None},
    )
    assert r.status_code == 422
    # halves -> quarters is a superset — fine
    r = await client.patch(
        f"/api/v1/racks/{rack['id']}/devices/{tray['id']}",
        json={"slot_layout": "quarters"},
    )
    assert r.status_code == 200 and r.json()["slot_layout"] == "quarters"


async def test_delete_carrier_cascades_children(client: AsyncClient):
    rack = await _rack(client)
    tray = await _carrier(client, rack["id"], u_position=4)
    await _mount(client, rack["id"], tray["id"], 0, name="a")
    await _mount(client, rack["id"], tray["id"], 1, name="b")

    assert (
        await client.delete(
            f"/api/v1/racks/{rack['id']}/devices/{tray['id']}"
        )
    ).status_code == 204
    detail = (await client.get(f"/api/v1/racks/{rack['id']}")).json()
    assert detail["devices"] == []


async def test_import_creates_carriers_and_children(client: AsyncClient):
    """Rackula carrier gear arrives as a carrier entry (slot_layout +
    carrier_key) followed by children keyed to it."""
    rack = await _rack(client)
    r = await client.post(
        f"/api/v1/racks/{rack['id']}/devices/import",
        json={
            "mode": "merge",
            "devices": [
                {
                    "name": "dual shelf", "u_position": 9, "face": "front",
                    "slot_layout": "halves", "carrier_key": "dev-3",
                },
                {
                    "name": "sw-a", "u_position": 9,
                    "carrier_key": "dev-3", "slot": 0,
                },
                {
                    "name": "sw-b", "u_position": 9,
                    "carrier_key": "dev-3", "slot": 1,
                },
                # auto-carrier synthesized client-side as a plain shelf
                {
                    "name": "Shelf", "u_position": 12, "face": "front",
                    "slot_layout": "shelf", "carrier_key": "auto-7",
                },
                {
                    "name": "rpi", "u_position": 12,
                    "carrier_key": "auto-7", "slot": 0,
                },
                {
                    "name": "lost", "u_position": 1,
                    "carrier_key": "missing", "slot": 0,
                },
            ],
        },
    )
    assert r.status_code == 200, r.text
    out = r.json()
    assert out["created"] == 5
    assert [s["name"] for s in out["skipped"]] == ["lost"]

    detail = (await client.get(f"/api/v1/racks/{rack['id']}")).json()
    by_name = {d["name"]: d for d in detail["devices"]}
    tray = by_name["dual shelf"]
    assert by_name["sw-a"]["carrier_id"] == tray["id"]
    assert by_name["sw-b"]["slot"] == 1
    assert by_name["rpi"]["carrier_id"] == by_name["Shelf"]["id"]
    # every device carries the rackula source badge
    assert all(d["source"] == "rackula" for d in detail["devices"])


async def test_import_child_slot_conflict_skips(client: AsyncClient):
    rack = await _rack(client)
    r = await client.post(
        f"/api/v1/racks/{rack['id']}/devices/import",
        json={
            "mode": "merge",
            "devices": [
                {
                    "name": "tray", "u_position": 4, "slot_layout": "halves",
                    "carrier_key": "t",
                },
                {"name": "a", "u_position": 4, "carrier_key": "t", "slot": 0},
                {"name": "b", "u_position": 4, "carrier_key": "t", "slot": 0},
            ],
        },
    )
    out = r.json()
    assert out["created"] == 2
    assert [s["name"] for s in out["skipped"]] == ["b"]
    assert "a" in out["skipped"][0]["reason"]


# --------------------------------------------------------- migration check


def test_alembic_rack_carriers_roundtrip():
    """0020 upgrade + downgrade + upgrade again on a scratch database."""
    import asyncio

    import asyncpg

    from tests.conftest import TEST_DB_NAME, _base_dsn, _split_dsn, test_url

    scratch = f"{TEST_DB_NAME}_carriers"

    async def _run():
        root, query = _split_dsn(_base_dsn())
        conn = await asyncpg.connect(f"{root}/postgres{query}")
        try:
            await conn.execute(f'DROP DATABASE IF EXISTS "{scratch}"')
            await conn.execute(f'CREATE DATABASE "{scratch}"')
        finally:
            await conn.close()

        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        url = test_url().replace(f"/{TEST_DB_NAME}", f"/{scratch}")
        env = dict(os.environ, DATABASE_URL=url)
        for cmd in ("upgrade head", "downgrade -1", "upgrade head"):
            subprocess.run(
                ["alembic", *cmd.split()], check=True, env=env, cwd=backend_dir
            )

        conn = await asyncpg.connect(
            url.replace("postgresql+asyncpg://", "postgresql://")
        )
        try:
            cols = await conn.fetch(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name='rack_devices'"
            )
            names = {r["column_name"] for r in cols}
            assert {"carrier_id", "slot", "slot_layout"} <= names
        finally:
            await conn.close()
            conn = await asyncpg.connect(f"{root}/postgres{query}")
            try:
                await conn.execute(f'DROP DATABASE IF EXISTS "{scratch}"')
            finally:
                await conn.close()

    asyncio.run(_run())


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
    assert "rack_groups" in names
    # rack_devices restores after racks + its SET NULL parents
    order = [spec.name for spec in BACKUP_TABLES]
    assert order.index("racks") > order.index("sites")
    # racks restore after rack_groups (racks.group_id -> rack_groups.id)
    assert order.index("sites") < order.index("rack_groups")
    assert order.index("rack_groups") < order.index("racks")
    for parent in ("racks", "assets", "ip_addresses"):
        assert order.index("rack_devices") > order.index(parent)


async def test_search_finds_rack_by_name_room_and_device(client: AsyncClient):
    rack = await _rack(client, name="Colo-A", room="Cage 7")
    await _dev(client, rack["id"], name="unifi-aggregation", u_position=1)

    for q, why in (("colo-a", "name"), ("cage", "room"), ("unifi", "device")):
        out = (await client.get("/api/v1/search", params={"q": q})).json()
        assert any(r["id"] == rack["id"] for r in out["racks"]), why


# ------------------------------------------------------------------ groups


async def _group(client: AsyncClient, **kw) -> dict:
    body = {"name": "Row A", **kw}
    r = await client.post("/api/v1/rack-groups", json=body)
    assert r.status_code == 201, r.text
    return r.json()


async def test_rack_group_crud(client: AsyncClient):
    site = (await client.post("/api/v1/sites", json={"name": "DC1"})).json()
    g = await _group(
        client, name="Row A", site_id=site["id"], description="prod row"
    )
    assert g["site_id"] == site["id"] and g["rack_count"] == 0
    assert g["pinned"] is False and g["display_color"] is None

    r = await client.patch(
        f"/api/v1/rack-groups/{g['id']}",
        json={"description": "prod row 1", "pinned": True},
    )
    assert r.status_code == 200 and r.json()["description"] == "prod row 1"
    assert r.json()["pinned"] is True

    groups = (await client.get("/api/v1/rack-groups")).json()
    assert [x["name"] for x in groups] == ["Row A"]

    # site filter + unknown site on create/update -> 404
    filtered = (
        await client.get("/api/v1/rack-groups", params={"site_id": site["id"]})
    ).json()
    assert [x["id"] for x in filtered] == [g["id"]]
    r = await client.post(
        "/api/v1/rack-groups", json={"name": "x", "site_id": 9999}
    )
    assert r.status_code == 404
    r = await client.patch(
        f"/api/v1/rack-groups/{g['id']}", json={"site_id": 9999}
    )
    assert r.status_code == 404

    assert (
        await client.delete(f"/api/v1/rack-groups/{g['id']}")
    ).status_code == 204
    assert (
        await client.get(f"/api/v1/rack-groups/{g['id']}")
    ).status_code == 404


async def test_rack_group_membership_and_ordering(client: AsyncClient):
    g = await _group(client)
    # create straight into the group — no position -> appended at the end
    r1 = await _rack(client, name="auto-join", group_id=g["id"])
    assert r1["group_id"] == g["id"] and r1["group_position"] == 1
    assert r1["group_name"] == "Row A"
    # patching racks in is the move operation — explicit positions order them
    a = await _rack(client, name="A")
    b = await _rack(client, name="B")
    c = await _rack(client, name="C")
    for rack, pos in ((a, 4), (b, 2), (c, 3)):
        r = await client.patch(
            f"/api/v1/racks/{rack['id']}",
            json={"group_id": g["id"], "group_position": pos},
        )
        assert r.status_code == 200 and r.json()["group_name"] == "Row A"

    # group detail returns racks in group_position order
    detail = (await client.get(f"/api/v1/rack-groups/{g['id']}")).json()
    assert detail["rack_count"] == 4
    assert [r["name"] for r in detail["racks"]] == [
        "auto-join",  # position 1
        "B",          # position 2
        "C",          # position 3
        "A",          # position 4
    ]
    assert detail["racks"][1]["group_position"] == 2

    # list rows carry membership + aggregates
    listed = (await client.get("/api/v1/racks")).json()["items"]
    by_name = {r["name"]: r for r in listed}
    assert by_name["B"]["group_name"] == "Row A"
    assert by_name["B"]["group_position"] == 2

    # ?group_id= filters the rack list (the groups tab's "show members" link)
    filtered = (
        await client.get("/api/v1/racks", params={"group_id": g["id"]})
    ).json()
    assert filtered["total"] == 4

    # patch back out — group_id AND the now-meaningless position both clear
    r = await client.patch(f"/api/v1/racks/{a['id']}", json={"group_id": None})
    assert r.status_code == 200
    assert r.json()["group_id"] is None and r.json()["group_position"] is None
    detail = (await client.get(f"/api/v1/rack-groups/{g['id']}")).json()
    assert [r["name"] for r in detail["racks"]] == ["auto-join", "B", "C"]

    # bogus group -> 404
    r = await client.patch(f"/api/v1/racks/{b['id']}", json={"group_id": 9999})
    assert r.status_code == 404
    r = await client.post(
        "/api/v1/racks", json={"name": "x", "group_id": 9999}
    )
    assert r.status_code == 404


async def test_rack_group_delete_unassigns_members(client: AsyncClient):
    g = await _group(client)
    r = await _rack(client, name="orphan", group_id=g["id"])
    assert (
        await client.delete(f"/api/v1/rack-groups/{g['id']}")
    ).status_code == 204
    got = (await client.get(f"/api/v1/racks/{r['id']}")).json()
    assert got["group_id"] is None and got["group_name"] is None


async def test_rack_group_reorder(client: AsyncClient):
    a = await _group(client, name="Row A")
    b = await _group(client, name="Row B")
    r = await client.post(
        "/api/v1/rack-groups/reorder", json={"ids": [b["id"], a["id"]]}
    )
    assert r.status_code == 204
    groups = (await client.get("/api/v1/rack-groups")).json()
    assert [g["name"] for g in groups] == ["Row B", "Row A"]


async def test_rack_group_rbac(
    client: AsyncClient, session: AsyncSession, auth_on
):
    from app.models.rack import RackGroup

    g = RackGroup(name="Row A")
    session.add(g)
    session.add_all(
        [
            User(
                username="v",
                password_hash=hash_password(PASSWORD),
                role=UserRole.VIEWER,
            ),
            User(
                username="c",
                password_hash=hash_password(PASSWORD),
                role=UserRole.CONTRIBUTOR,
            ),
        ]
    )
    await session.commit()
    await session.refresh(g)

    r = await client.post(
        "/api/v1/auth/login", json={"username": "v", "password": PASSWORD}
    )
    assert r.status_code == 200
    assert (await client.get("/api/v1/rack-groups")).status_code == 200
    assert (await client.get(f"/api/v1/rack-groups/{g.id}")).status_code == 200
    assert (
        await client.post("/api/v1/rack-groups", json={"name": "x"})
    ).status_code == 403
    assert (
        await client.patch(f"/api/v1/rack-groups/{g.id}", json={"name": "y"})
    ).status_code == 403
    assert (
        await client.post("/api/v1/rack-groups/reorder", json={"ids": [g.id]})
    ).status_code == 403
    assert (
        await client.delete(f"/api/v1/rack-groups/{g.id}")
    ).status_code == 403

    # contributor writes but cannot delete
    r = await client.post(
        "/api/v1/auth/login", json={"username": "c", "password": PASSWORD}
    )
    assert r.status_code == 200
    assert (
        await client.post("/api/v1/rack-groups", json={"name": "x"})
    ).status_code == 201
    assert (
        await client.patch(f"/api/v1/rack-groups/{g.id}", json={"name": "y"})
    ).status_code == 200
    assert (
        await client.delete(f"/api/v1/rack-groups/{g.id}")
    ).status_code == 403


async def test_rack_group_changes_are_audited(client: AsyncClient):
    g = await _group(client, name="Audited Row")
    await client.patch(
        f"/api/v1/rack-groups/{g['id']}", json={"description": "d"}
    )
    await client.delete(f"/api/v1/rack-groups/{g['id']}")
    log = (
        await client.get("/api/v1/changelog", params={"object_type": "RackGroup"})
    ).json()["items"]
    assert [e["action"] for e in log] == ["delete", "update", "create"]
    assert log[-1]["object_repr"] == "Audited Row"


async def test_search_finds_rack_groups_and_members(client: AsyncClient):
    g = await _group(client, name="ProdRow-9")
    rack = await _rack(client, name="member", group_id=g["id"])
    out = (await client.get("/api/v1/search", params={"q": "prodrow"})).json()
    assert any(x["id"] == g["id"] for x in out["rack_groups"])
    # member racks surface via their group's name too
    assert any(x["id"] == rack["id"] for x in out["racks"])


# ------------------------------------------------------ capacity aggregates


async def test_rack_capacity_aggregates(client: AsyncClient):
    rack = await _rack(client, height_u=10)
    await _dev(client, rack["id"], name="pdu", u_position=1)
    detail = (await client.get(f"/api/v1/racks/{rack['id']}")).json()
    # no device supplied values -> nulls (the UI hides the block entirely)
    assert detail["power_w"] is None and detail["weight_kg"] is None

    await _dev(
        client, rack["id"], name="srv-a", u_position=2,
        watts=400, weight_kg=12.5,
    )
    await _dev(client, rack["id"], name="srv-b", u_position=3, watts=300)

    detail = (await client.get(f"/api/v1/racks/{rack['id']}")).json()
    assert detail["power_w"] == 700
    assert detail["weight_kg"] == 12.5
    by_name = {x["name"]: x for x in detail["devices"]}
    assert by_name["srv-a"]["watts"] == 400
    assert by_name["srv-a"]["weight_kg"] == 12.5
    assert by_name["srv-b"]["watts"] == 300
    assert by_name["srv-b"]["weight_kg"] is None
    assert by_name["pdu"]["watts"] is None

    # carrier children still draw real power/weight even though they share
    # the carrier's U span
    tray = await _carrier(client, rack["id"], u_position=6, watts=50)
    await _mount(
        client, rack["id"], tray["id"], 0, name="half-a",
        watts=100, weight_kg=2,
    )
    detail = (await client.get(f"/api/v1/racks/{rack['id']}")).json()
    assert detail["used_u"] == 4  # U1,U2,U3 + U6 tray (child shares its span)
    assert detail["power_w"] == 850
    assert detail["weight_kg"] == 14.5

    # the same sums land on the list endpoint
    row = next(
        r
        for r in (await client.get("/api/v1/racks")).json()["items"]
        if r["id"] == rack["id"]
    )
    assert row["power_w"] == 850 and row["weight_kg"] == 14.5

    # clearing values re-nulls the aggregate (vs. reporting a fake 0)
    r = await client.patch(
        f"/api/v1/racks/{rack['id']}/devices/{by_name['srv-a']['id']}",
        json={"watts": None, "weight_kg": None},
    )
    assert r.status_code == 200 and r.json()["watts"] is None
    detail = (await client.get(f"/api/v1/racks/{rack['id']}")).json()
    assert detail["power_w"] == 450 and detail["weight_kg"] == 2

    # negative / out-of-precision values are rejected
    for bad in ({"watts": -5}, {"weight_kg": -1}, {"weight_kg": 123456}):
        r = await client.patch(
            f"/api/v1/racks/{rack['id']}/devices/{by_name['srv-b']['id']}",
            json=bad,
        )
        assert r.status_code == 422, bad


async def test_rack_group_detail_carries_aggregates(client: AsyncClient):
    g = await _group(client)
    a = await _rack(
        client, name="A", height_u=10, group_id=g["id"], group_position=2
    )
    await _rack(client, name="B", height_u=8, group_id=g["id"], group_position=1)
    await _dev(client, a["id"], u_position=1, watts=500, weight_kg=20)

    detail = (await client.get(f"/api/v1/rack-groups/{g['id']}")).json()
    assert [r["name"] for r in detail["racks"]] == ["B", "A"]
    a_row = detail["racks"][1]
    assert a_row["used_u"] == 1
    assert a_row["power_w"] == 500 and a_row["weight_kg"] == 20
    # devices ride along (the row view draws elevations from them)
    assert a_row["devices"][0]["watts"] == 500


async def test_dashboard_rack_capacity(client: AsyncClient):
    stats = (await client.get("/api/v1/dashboard/stats")).json()
    assert stats["racks_total"] == 0
    assert stats["rack_u_used"] == 0 and stats["rack_u_total"] == 0

    a = await _rack(client, height_u=10)
    b = await _rack(client, height_u=4)
    # front+rear pair shares U1-2 (counts once); a lone device at U4 of b
    await _dev(client, a["id"], u_position=1, u_height=2, face="front")
    await _dev(client, a["id"], u_position=1, u_height=2, face="rear")
    await _dev(client, b["id"], u_position=4)
    stats = (await client.get("/api/v1/dashboard/stats")).json()
    assert stats["racks_total"] == 2
    assert stats["rack_u_total"] == 14
    assert stats["rack_u_used"] == 3


# ---------------------------------------------------------- cross-rack move


async def test_device_cross_rack_move(client: AsyncClient):
    src = await _rack(client, name="src", height_u=10)
    dst = await _rack(client, name="dst", height_u=10)
    d = await _dev(client, src["id"], name="nomad", u_position=2, watts=200)
    await _dev(client, dst["id"], name="blocker", u_position=5, face="front")

    # colliding with the target rack's gear -> 409, device stays put
    r = await client.patch(
        f"/api/v1/racks/{src['id']}/devices/{d['id']}",
        json={"rack_id": dst["id"], "u_position": 5},
    )
    assert r.status_code == 409
    # past the target's top -> 422
    r = await client.patch(
        f"/api/v1/racks/{src['id']}/devices/{d['id']}",
        json={"rack_id": dst["id"], "u_position": 11},
    )
    assert r.status_code == 422
    # bogus target -> 404
    r = await client.patch(
        f"/api/v1/racks/{src['id']}/devices/{d['id']}",
        json={"rack_id": 9999, "u_position": 1},
    )
    assert r.status_code == 404

    r = await client.patch(
        f"/api/v1/racks/{src['id']}/devices/{d['id']}",
        json={"rack_id": dst["id"], "u_position": 7},
    )
    assert r.status_code == 200, r.text
    got = r.json()
    assert got["rack_id"] == dst["id"] and got["u_position"] == 7

    src_detail = (await client.get(f"/api/v1/racks/{src['id']}")).json()
    dst_detail = (await client.get(f"/api/v1/racks/{dst['id']}")).json()
    assert src_detail["device_count"] == 0 and src_detail["power_w"] is None
    assert dst_detail["device_count"] == 2 and dst_detail["power_w"] == 200


async def test_carrier_move_takes_children_across_racks(client: AsyncClient):
    src = await _rack(client)
    dst = await _rack(client)
    tray = await _carrier(client, src["id"], u_position=5, name="tray")
    kid = await _mount(client, src["id"], tray["id"], 0, name="kid")
    await _mount(client, src["id"], tray["id"], 1, name="kid2")

    r = await client.patch(
        f"/api/v1/racks/{src['id']}/devices/{tray['id']}",
        json={"rack_id": dst["id"], "u_position": 3},
    )
    assert r.status_code == 200, r.text
    dst_detail = (await client.get(f"/api/v1/racks/{dst['id']}")).json()
    by_name = {d["name"]: d for d in dst_detail["devices"]}
    assert by_name["tray"]["u_position"] == 3
    # the tray physically carries its children — they moved with it and
    # mirror its new span
    assert by_name["kid"]["rack_id"] == dst["id"]
    assert by_name["kid"]["u_position"] == 3
    assert by_name["kid"]["carrier_id"] == by_name["tray"]["id"]
    src_detail = (await client.get(f"/api/v1/racks/{src['id']}")).json()
    assert src_detail["devices"] == []

    # a mounted child moved alone leaves its carrier behind — it unmounts
    r = await client.patch(
        f"/api/v1/racks/{dst['id']}/devices/{kid['id']}",
        json={"rack_id": src["id"], "u_position": 8},
    )
    assert r.status_code == 200, r.text
    got = r.json()
    assert got["rack_id"] == src["id"]
    assert got["carrier_id"] is None and got["slot"] is None
    dst_detail = (await client.get(f"/api/v1/racks/{dst['id']}")).json()
    assert sorted(d["name"] for d in dst_detail["devices"]) == ["kid2", "tray"]


# --------------------------------------------------------- migration check


def test_alembic_rack_groups_roundtrip():
    """0021 upgrade + downgrade + upgrade again on a scratch database."""
    import asyncio

    import asyncpg

    from tests.conftest import TEST_DB_NAME, _base_dsn, _split_dsn, test_url

    scratch = f"{TEST_DB_NAME}_groups"

    async def _run():
        root, query = _split_dsn(_base_dsn())
        conn = await asyncpg.connect(f"{root}/postgres{query}")
        try:
            await conn.execute(f'DROP DATABASE IF EXISTS "{scratch}"')
            await conn.execute(f'CREATE DATABASE "{scratch}"')
        finally:
            await conn.close()

        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        url = test_url().replace(f"/{TEST_DB_NAME}", f"/{scratch}")
        env = dict(os.environ, DATABASE_URL=url)

        def alembic(*cmd):
            subprocess.run(
                ["alembic", *cmd], check=True, env=env, cwd=backend_dir
            )

        async def fetch(sql):
            c = await asyncpg.connect(
                url.replace("postgresql+asyncpg://", "postgresql://")
            )
            try:
                return await c.fetch(sql)
            finally:
                await c.close()

        alembic("upgrade", "head")
        rows = await fetch(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_name='rack_groups'"
        )
        assert len(rows) == 1
        cols = await fetch(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name='racks'"
        )
        assert {"group_id", "group_position"} <= {
            r["column_name"] for r in cols
        }

        # downgrade restores the pre-0021 schema
        alembic("downgrade", "-1")
        rows = await fetch(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_name='rack_groups'"
        )
        assert len(rows) == 0
        cols = await fetch(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name='racks'"
        )
        assert "group_id" not in {r["column_name"] for r in cols}
        cols = await fetch(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name='rack_devices'"
        )
        assert "watts" not in {r["column_name"] for r in cols}

        # and upgrades again cleanly
        alembic("upgrade", "head")
        rows = await fetch(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_name='rack_groups'"
        )
        assert len(rows) == 1
        cols = await fetch(
            "SELECT column_name, data_type, numeric_precision, numeric_scale "
            "FROM information_schema.columns WHERE table_name='rack_devices' "
            "AND column_name IN ('watts','weight_kg')"
        )
        types = {r["column_name"]: r["data_type"] for r in cols}
        assert types == {"watts": "integer", "weight_kg": "numeric"}
        assert {r["numeric_scale"] for r in cols if r["column_name"] == "weight_kg"} == {2}

        conn = await asyncpg.connect(f"{root}/postgres{query}")
        try:
            await conn.execute(f'DROP DATABASE IF EXISTS "{scratch}"')
        finally:
            await conn.close()

    asyncio.run(_run())
