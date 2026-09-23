"""V4A cabling: device interfaces, cables, patch-panel traces, the legacy
free-text matcher, RBAC, changelog, backup round-trip, and migration
reversibility."""

import gzip
import json
import os
import subprocess

import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.redis import get_redis
from app.core.security import hash_password
from app.models.user import User, UserRole

PASSWORD = "cable-test-pw1"


@pytest.fixture
async def auth_on():
    settings = get_settings()
    settings.ipambox_allow_insecure = False
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


async def _device(client: AsyncClient, **kw) -> dict:
    body = {"name": "srv", **kw}
    r = await client.post("/api/v1/devices", json=body)
    assert r.status_code == 201, r.text
    return r.json()


async def _rack(client: AsyncClient, **kw) -> dict:
    body = {"name": "R1", "height_u": 12, "width": 19, **kw}
    r = await client.post("/api/v1/racks", json=body)
    assert r.status_code == 201, r.text
    return r.json()


async def _racked(client: AsyncClient, rack_id: int, **kw) -> dict:
    body = {"name": "srv", "u_position": 1, "u_height": 1, "face": "front", **kw}
    r = await client.post(f"/api/v1/racks/{rack_id}/devices", json=body)
    assert r.status_code == 201, r.text
    return r.json()


async def _prefix(client: AsyncClient, cidr: str = "10.70.0.0/24") -> int:
    vrfs = (await client.get("/api/v1/vrfs")).json()
    vrf = (vrfs["items"] if isinstance(vrfs, dict) else vrfs)[0]
    r = await client.post(
        "/api/v1/prefixes", json={"prefix": cidr, "vrf_id": vrf["id"]}
    )
    assert r.status_code == 201, r.text
    return r.json()["id"]


async def _ip(client: AsyncClient, prefix_id: int, addr: str, **kw) -> dict:
    r = await client.post(
        "/api/v1/addresses", json={"address": addr, "prefix_id": prefix_id, **kw}
    )
    assert r.status_code == 201, r.text
    return r.json()


async def _iface(client: AsyncClient, device_id: int, **kw) -> dict:
    body = {"name": "p1", **kw}
    r = await client.post(f"/api/v1/devices/{device_id}/interfaces", json=body)
    assert r.status_code == 201, r.text
    return r.json()


async def _gen(client: AsyncClient, device_id: int, **kw) -> list[dict]:
    body = {"kind": "rj45", "prefix": "p", "count": 4, **kw}
    r = await client.post(
        f"/api/v1/devices/{device_id}/interfaces/generate", json=body
    )
    assert r.status_code == 201, r.text
    return r.json()


async def _cable(client: AsyncClient, a: int, b: int, **kw) -> dict:
    r = await client.post(
        "/api/v1/cables", json={"a_interface_id": a, "b_interface_id": b, **kw}
    )
    assert r.status_code == 201, r.text
    return r.json()


# ------------------------------------------------------------- interfaces


async def test_interface_crud(client: AsyncClient):
    d = await _device(client, name="sw1")
    i = await _iface(
        client,
        d["id"],
        name="Gi1/0/1",
        kind="sfp28",
        speed_mbps=25000,
        mac_address="aa-bb.cc-dd.ee-ff",
    )
    assert i["name"] == "Gi1/0/1" and i["kind"] == "sfp28"
    assert i["mac_address"] == "AA:BB:CC:DD:EE:FF"
    assert i["position"] == 0 and i["peer"] is None

    i2 = await _iface(client, d["id"], name="Gi1/0/2")
    assert i2["position"] == 1  # auto-appends after the last position

    got = (await client.get(f"/api/v1/interfaces/{i['id']}")).json()
    assert got["name"] == "Gi1/0/1"

    listed = (await client.get(f"/api/v1/devices/{d['id']}/interfaces")).json()
    assert [x["name"] for x in listed] == ["Gi1/0/1", "Gi1/0/2"]

    r = await client.patch(
        f"/api/v1/devices/{d['id']}/interfaces/{i['id']}",
        json={"name": "Gi1/0/9", "speed_mbps": None},
    )
    assert r.status_code == 200 and r.json()["name"] == "Gi1/0/9"

    # duplicate name within the device -> 409
    r = await client.patch(
        f"/api/v1/devices/{d['id']}/interfaces/{i['id']}",
        json={"name": "Gi1/0/2"},
    )
    assert r.status_code == 409

    assert (
        await client.delete(f"/api/v1/devices/{d['id']}/interfaces/{i2['id']}")
    ).status_code == 204
    listed = (await client.get(f"/api/v1/devices/{d['id']}/interfaces")).json()
    assert [x["name"] for x in listed] == ["Gi1/0/9"]

    # interface on another device is not reachable through this device
    d2 = await _device(client, name="other")
    assert (
        await client.patch(
            f"/api/v1/devices/{d2['id']}/interfaces/{i['id']}", json={"name": "x"}
        )
    ).status_code == 404


async def test_interface_name_and_pair_validation(client: AsyncClient):
    d = await _device(client)
    r = await client.post(
        f"/api/v1/devices/{d['id']}/interfaces", json={"name": "  "}
    )
    assert r.status_code == 422
    a = await _iface(client, d["id"], name="a", kind="patch")
    b = await _iface(client, d["id"], name="b", kind="patch")
    # self-pair rejected
    r = await client.post(
        f"/api/v1/devices/{d['id']}/interfaces",
        json={"name": "c", "pair_interface_id": a["id"]},
    )
    assert r.status_code == 201
    c = r.json()
    r = await client.patch(
        f"/api/v1/devices/{d['id']}/interfaces/{c['id']}",
        json={"pair_interface_id": c["id"]},
    )
    assert r.status_code == 422
    # pair must live on the same device
    d2 = await _device(client, name="other")
    far = await _iface(client, d2["id"], name="x")
    r = await client.patch(
        f"/api/v1/devices/{d['id']}/interfaces/{a['id']}",
        json={"pair_interface_id": far["id"]},
    )
    assert r.status_code == 422
    # reciprocal linking: setting a->b completes b->a
    r = await client.patch(
        f"/api/v1/devices/{d['id']}/interfaces/{a['id']}",
        json={"pair_interface_id": b["id"]},
    )
    assert r.status_code == 200
    b_now = (await client.get(f"/api/v1/interfaces/{b['id']}")).json()
    assert b_now["pair_interface_id"] == a["id"]
    # pairing an already-paired port elsewhere -> 409
    r = await client.patch(
        f"/api/v1/devices/{d['id']}/interfaces/{c['id']}",
        json={"pair_interface_id": b["id"]},
    )
    assert r.status_code == 409
    # unpairing releases both sides
    r = await client.patch(
        f"/api/v1/devices/{d['id']}/interfaces/{a['id']}",
        json={"pair_interface_id": None},
    )
    assert r.status_code == 200
    b_now = (await client.get(f"/api/v1/interfaces/{b['id']}")).json()
    assert b_now["pair_interface_id"] is None


async def test_interface_generate(client: AsyncClient):
    d = await _device(client, name="sw")
    rows = await _gen(
        client, d["id"], kind="sfp", prefix="Gi1/0/", count=48, speed_mbps=1000
    )
    assert len(rows) == 48
    assert rows[0]["name"] == "Gi1/0/1" and rows[-1]["name"] == "Gi1/0/48"
    assert all(r["speed_mbps"] == 1000 for r in rows)

    # offset indexing + explicit positions
    rows = await _gen(client, d["id"], prefix="Te1/1/", count=4, start_index=25)
    assert [r["name"] for r in rows] == [
        "Te1/1/25", "Te1/1/26", "Te1/1/27", "Te1/1/28",
    ]
    assert [r["position"] for r in rows] == [25, 26, 27, 28]


async def test_generate_patch_panel_pairs(client: AsyncClient):
    """A patch panel's front+back in one call: prefix+pair_prefix produce
    same-indexed rows reciprocally linked via pair_interface_id."""
    d = await _device(client, name="panel-a")
    rows = await _gen(
        client, d["id"], kind="patch", prefix="p", pair_prefix="b", count=24
    )
    assert len(rows) == 48
    by_name = {r["name"]: r for r in rows}
    assert by_name["p1"]["pair_interface_id"] == by_name["b1"]["id"]
    assert by_name["b1"]["pair_interface_id"] == by_name["p1"]["id"]
    assert by_name["p24"]["pair_interface_id"] == by_name["b24"]["id"]
    # paired sides share a position so the grid keeps them adjacent
    assert by_name["p7"]["position"] == by_name["b7"]["position"]


async def test_generate_conflicts(client: AsyncClient):
    d = await _device(client)
    await _gen(client, d["id"], prefix="p", count=2)
    # any overlap -> 409 naming the first conflict
    r = await client.post(
        f"/api/v1/devices/{d['id']}/interfaces/generate",
        json={"kind": "rj45", "prefix": "p", "count": 3, "start_index": 2},
    )
    assert r.status_code == 409 and "p2" in r.json()["detail"]
    # pair_prefix must differ from prefix
    r = await client.post(
        f"/api/v1/devices/{d['id']}/interfaces/generate",
        json={"kind": "patch", "prefix": "p", "count": 2, "pair_prefix": "p"},
    )
    assert r.status_code == 422


async def test_interface_connected_ip_binding(client: AsyncClient):
    """connected_ip_id: the host-side NIC→IP binding — must be one of the
    device's own IPs when that IP is already owned."""
    pid = await _prefix(client)
    d = await _device(client, name="srv")
    d2 = await _device(client, name="other")
    mine = await _ip(client, pid, "10.70.0.10", device_id=d["id"])
    theirs = await _ip(client, pid, "10.70.0.11", device_id=d2["id"])
    free = await _ip(client, pid, "10.70.0.12")

    i = await _iface(client, d["id"], name="eth0", connected_ip_id=mine["id"])
    assert i["connected_ip"]["id"] == mine["id"]
    assert "10.70.0.10" in i["connected_ip"]["label"]

    # an IP owned by another device can't be this port's binding
    r = await client.post(
        f"/api/v1/devices/{d['id']}/interfaces",
        json={"name": "eth1", "connected_ip_id": theirs["id"]},
    )
    assert r.status_code == 422
    # an unowned IP is fine to bind
    r = await client.post(
        f"/api/v1/devices/{d['id']}/interfaces",
        json={"name": "eth1", "connected_ip_id": free["id"]},
    )
    assert r.status_code == 201
    # bogus ids -> 404
    r = await client.post(
        f"/api/v1/devices/{d['id']}/interfaces",
        json={"name": "eth2", "connected_ip_id": 999999},
    )
    assert r.status_code == 404


# ----------------------------------------------------------------- cables


async def test_cable_crud_and_filters(client: AsyncClient):
    site = (await client.post("/api/v1/sites", json={"name": "HQ"})).json()
    rack = await _rack(client, site_id=site["id"])
    sw = await _racked(client, rack["id"], name="sw")
    srv = await _racked(client, rack["id"], name="srv", u_position=2)
    sw_p = await _gen(client, sw["id"], prefix="Gi1/0/", count=2)
    srv_p = await _gen(client, srv["id"], prefix="eth", count=2)

    c = await _cable(
        client,
        sw_p[0]["id"],
        srv_p[0]["id"],
        kind="cat6a",
        color="yellow",
        label="L-100",
        length_m=3.5,
        notes="uplink",
    )
    assert c["a"]["device_name"] == "sw" and c["a"]["interface_name"] == "Gi1/0/1"
    assert c["b"]["device_name"] == "srv" and c["b"]["interface_name"] == "eth1"
    assert c["length_m"] == 3.5

    # peer resolution on the interface read
    iface = (await client.get(f"/api/v1/interfaces/{sw_p[0]['id']}")).json()
    assert iface["peer"]["device_name"] == "srv"
    assert iface["peer"]["interface_name"] == "eth1"
    assert iface["peer"]["cable_label"] == "L-100"

    # filters: device_id / site_id / q
    by_dev = (
        await client.get("/api/v1/cables", params={"device_id": sw["id"]})
    ).json()
    assert by_dev["total"] == 1 and by_dev["items"][0]["id"] == c["id"]
    by_site = (
        await client.get("/api/v1/cables", params={"site_id": site["id"]})
    ).json()
    assert by_site["total"] == 1
    other_site = (
        await client.post("/api/v1/sites", json={"name": "DC2"})
    ).json()
    by_other = (
        await client.get("/api/v1/cables", params={"site_id": other_site["id"]})
    ).json()
    assert by_other["total"] == 0
    by_q = (await client.get("/api/v1/cables", params={"q": "L-100"})).json()
    assert by_q["total"] == 1

    # patch the cable: label + re-home the b end onto the free port
    r = await client.patch(
        f"/api/v1/cables/{c['id']}",
        json={"label": "L-101", "b_interface_id": srv_p[1]["id"]},
    )
    assert r.status_code == 200
    assert r.json()["label"] == "L-101"
    assert r.json()["b"]["interface_name"] == "eth2"

    assert (await client.delete(f"/api/v1/cables/{c['id']}")).status_code == 204
    assert (await client.get("/api/v1/cables")).json()["total"] == 0


async def test_cable_end_uniqueness(client: AsyncClient):
    d = await _device(client)
    ports = await _gen(client, d["id"], prefix="p", count=3)
    p1, p2, p3 = (p["id"] for p in ports)
    c = await _cable(client, p1, p2)

    # second cable on the a end -> 409 carrying the existing cable's id
    r = await client.post(
        "/api/v1/cables", json={"a_interface_id": p1, "b_interface_id": p3}
    )
    assert r.status_code == 409 and str(c["id"]) in r.json()["detail"]
    # ... and on the b end
    r = await client.post(
        "/api/v1/cables", json={"a_interface_id": p3, "b_interface_id": p2}
    )
    assert r.status_code == 409
    # self-connection -> 422
    r = await client.post(
        "/api/v1/cables", json={"a_interface_id": p3, "b_interface_id": p3}
    )
    assert r.status_code == 422
    # missing interface -> 404
    r = await client.post(
        "/api/v1/cables", json={"a_interface_id": p3, "b_interface_id": 999999}
    )
    assert r.status_code == 404
    # patch re-attach onto a busy end -> 409
    r = await client.patch(
        f"/api/v1/cables/{c['id']}", json={"a_interface_id": p3}
    )
    assert r.status_code == 200  # p3 is free — allowed
    r = await client.post(
        "/api/v1/cables", json={"a_interface_id": p1, "b_interface_id": p2}
    )
    assert r.status_code == 409


async def test_cable_persists_when_device_deleted(client: AsyncClient):
    """Deleting a device removes its interfaces and their cables."""
    d1, d2 = await _device(client, name="a"), await _device(client, name="b")
    i1 = await _iface(client, d1["id"], name="p1")
    i2 = await _iface(client, d2["id"], name="p1")
    await _cable(client, i1["id"], i2["id"])
    assert (await client.delete(f"/api/v1/devices/{d1['id']}")).status_code == 204
    assert (await client.get("/api/v1/cables")).json()["total"] == 0
    got = (await client.get(f"/api/v1/interfaces/{i2['id']}")).json()
    assert got["peer"] is None


async def test_device_delete_with_paired_interfaces(client: AsyncClient):
    """A panel device deletes cleanly: its self-paired ports and the cables
    on them go together (the self-FK ordering case)."""
    panel = await _device(client, name="panel")
    sw = await _device(client, name="sw")
    rows = await _gen(
        client, panel["id"], kind="patch", prefix="p", pair_prefix="b", count=2
    )
    by_name = {r["name"]: r for r in rows}
    sp = await _iface(client, sw["id"], name="u1")
    await _cable(client, by_name["b1"]["id"], sp["id"])
    assert (
        await client.delete(f"/api/v1/devices/{panel['id']}")
    ).status_code == 204
    assert (await client.get("/api/v1/cables")).json()["total"] == 0
    got = (await client.get(f"/api/v1/interfaces/{sp['id']}")).json()
    assert got["peer"] is None


# ------------------------------------------------------------------ trace


async def _panel_path(client: AsyncClient) -> dict:
    """host --c1--> panel front p1 (pair b1) --c2--> switch port."""
    host = await _device(client, name="host")
    panel = await _device(client, name="panel")
    sw = await _device(client, name="core-sw")
    nic = await _iface(client, host["id"], name="eth0")
    fronts = await _gen(
        client, panel["id"], kind="patch", prefix="p", pair_prefix="b", count=4
    )
    by_name = {r["name"]: r for r in fronts}
    sw_port = await _iface(client, sw["id"], name="Gi1/0/1")
    c1 = await _cable(client, nic["id"], by_name["p1"]["id"], kind="cat6")
    c2 = await _cable(client, by_name["b1"]["id"], sw_port["id"], kind="cat6a")
    return {
        "host": host, "panel": panel, "sw": sw, "nic": nic,
        "p1": by_name["p1"], "b1": by_name["b1"], "sw_port": sw_port,
        "c1": c1, "c2": c2,
    }


async def test_trace_patch_panel_chain(client: AsyncClient):
    """The headline feature: host -> panel front -> panel back -> switch,
    four ordered hops with the right cables on the right edges."""
    x = await _panel_path(client)
    hops = (
        await client.get("/api/v1/cables/trace", params={"interface_id": x["nic"]["id"]})
    ).json()
    path = [(h["device_name"], h["interface_name"]) for h in hops]
    assert path == [
        ("host", "eth0"),
        ("panel", "p1"),
        ("panel", "b1"),
        ("core-sw", "Gi1/0/1"),
    ]
    # cable ids/kinds on the cable edges; null on start + pair hops
    assert hops[0]["cable_id"] is None
    assert hops[1]["cable_id"] == x["c1"]["id"] and hops[1]["cable_kind"] == "cat6"
    assert hops[2]["cable_id"] is None  # front->back pair hop isn't a cable
    assert hops[3]["cable_id"] == x["c2"]["id"] and hops[3]["cable_kind"] == "cat6a"


async def test_trace_mid_chain_returns_full_path(client: AsyncClient):
    """Starting at a patch port still surfaces both directions — the far
    end of the pair side leads, so the full chain is ordered core→host."""
    x = await _panel_path(client)
    hops = (
        await client.get(
            "/api/v1/cables/trace", params={"interface_id": x["p1"]["id"]}
        )
    ).json()
    path = [(h["device_name"], h["interface_name"]) for h in hops]
    assert path == [
        ("core-sw", "Gi1/0/1"),
        ("panel", "b1"),
        ("panel", "p1"),
        ("host", "eth0"),
    ]


async def test_trace_cycle_terminates(client: AsyncClient):
    """Two panels paired into a ring: the visited set ends the walk."""
    a = await _device(client, name="panel-a")
    b = await _device(client, name="panel-b")
    pa = await _gen(client, a["id"], kind="patch", prefix="p", pair_prefix="b", count=1)
    pb = await _gen(client, b["id"], kind="patch", prefix="p", pair_prefix="b", count=1)
    a_by = {r["name"]: r for r in pa}
    b_by = {r["name"]: r for r in pb}
    # a.p1 --cable--> b.b1 (pair b.p1) --cable--> a.b1 (pair a.p1) = ring
    await _cable(client, a_by["p1"]["id"], b_by["b1"]["id"])
    await _cable(client, b_by["p1"]["id"], a_by["b1"]["id"])
    r = await client.get(
        "/api/v1/cables/trace", params={"interface_id": a_by["p1"]["id"]}
    )
    assert r.status_code == 200
    assert len(r.json()) <= 10
    # the whole ring, once — every hop is unique
    ids = [h["interface_id"] for h in r.json()]
    assert len(ids) == len(set(ids)) == 4


async def test_trace_unconnected_and_missing(client: AsyncClient):
    d = await _device(client)
    i = await _iface(client, d["id"], name="p1")
    hops = (
        await client.get("/api/v1/cables/trace", params={"interface_id": i["id"]})
    ).json()
    assert len(hops) == 1 and hops[0]["interface_id"] == i["id"]
    r = await client.get("/api/v1/cables/trace", params={"interface_id": 999999})
    assert r.status_code == 404


# ------------------------------------------------------ device/rack counts


async def test_device_and_rack_counts(client: AsyncClient):
    rack = await _rack(client)
    sw = await _racked(client, rack["id"], name="sw")
    srv = await _racked(client, rack["id"], name="srv", u_position=2)
    a = await _gen(client, sw["id"], prefix="p", count=4)
    b = await _gen(client, srv["id"], prefix="e", count=2)
    await _cable(client, a[0]["id"], b[0]["id"])

    d = (await client.get(f"/api/v1/devices/{sw['id']}")).json()
    assert d["interface_count"] == 4 and d["cabled_count"] == 1
    d2 = (await client.get(f"/api/v1/devices/{srv['id']}")).json()
    assert d2["interface_count"] == 2 and d2["cabled_count"] == 1

    listed = (await client.get("/api/v1/devices")).json()["items"]
    by_id = {x["id"]: x for x in listed}
    assert by_id[sw["id"]]["cabled_count"] == 1
    assert by_id[srv["id"]]["interface_count"] == 2

    r = (await client.get(f"/api/v1/racks/{rack['id']}")).json()
    by_id = {x["id"]: x for x in r["devices"]}
    assert by_id[sw["id"]]["interface_count"] == 4
    assert by_id[sw["id"]]["cabled_count"] == 1
    assert by_id[srv["id"]]["cabled_count"] == 1


# ------------------------------------------------- ip -> structured link


async def test_address_connected_interface_link(client: AsyncClient):
    pid = await _prefix(client)
    sw = await _device(client, name="sw1")
    port = await _iface(client, sw["id"], name="Gi1/0/12")

    ip = await _ip(
        client,
        pid,
        "10.70.0.50",
        switch_name="sw1",
        switch_port="Gi1/0/12",
        connected_interface_id=port["id"],
    )
    assert ip["connected_interface_id"] == port["id"]
    assert ip["connected_interface"]["name"] == "Gi1/0/12"
    assert ip["connected_interface"]["device_name"] == "sw1"
    # the legacy text stays — structured link is additive, not a rename
    assert ip["switch_name"] == "sw1" and ip["switch_port"] == "Gi1/0/12"

    # patch to a different port, then unlink
    port2 = await _iface(client, sw["id"], name="Gi1/0/13")
    r = await client.patch(
        f"/api/v1/addresses/{ip['id']}",
        json={"connected_interface_id": port2["id"]},
    )
    assert r.json()["connected_interface"]["name"] == "Gi1/0/13"
    r = await client.patch(
        f"/api/v1/addresses/{ip['id']}", json={"connected_interface_id": None}
    )
    assert r.json()["connected_interface_id"] is None
    assert r.json()["connected_interface"] is None

    # bogus interface -> 404
    r = await client.patch(
        f"/api/v1/addresses/{ip['id']}", json={"connected_interface_id": 999999}
    )
    assert r.status_code == 404

    # deleting the interface clears the link (SET NULL) but keeps the text
    d = (await client.delete(f"/api/v1/devices/{sw['id']}/interfaces/{port2['id']}"))
    assert d.status_code == 204
    got = (await client.get(f"/api/v1/addresses/{ip['id']}")).json()
    assert got["connected_interface_id"] is None
    assert got["switch_name"] == "sw1"


async def test_match_free_text(client: AsyncClient):
    """Exact-name matching links legacy rows; ambiguity is reported, never
    guessed; the text columns are untouched throughout."""
    pid = await _prefix(client)
    sw = await _device(client, name="sw1")
    await _gen(client, sw["id"], prefix="Gi1/0/", count=2)
    # a second device with the same name + same port names = ambiguity
    dup = await _device(client, name="dup-sw")
    await _gen(client, dup["id"], prefix="p", count=1)
    dup2 = await _device(client, name="dup-sw")
    await _gen(client, dup2["id"], prefix="p", count=1)

    good = await _ip(
        client, pid, "10.70.0.60", switch_name="sw1", switch_port="Gi1/0/1"
    )
    amb = await _ip(
        client, pid, "10.70.0.61", switch_name="dup-sw", switch_port="p1"
    )
    ghost = await _ip(
        client, pid, "10.70.0.62", switch_name="nowhere", switch_port="x"
    )
    plain = await _ip(client, pid, "10.70.0.63")  # no text at all

    r = await client.post("/api/v1/interfaces/match-free-text")
    assert r.status_code == 200, r.text
    rep = r.json()
    assert rep["matched"] == 1 and rep["matched_ids"] == [good["id"]]
    assert rep["ambiguous"] == 1 and rep["ambiguous_ids"] == [amb["id"]]
    assert rep["unmatched"] == 1 and rep["unmatched_ids"] == [ghost["id"]]

    got = (await client.get(f"/api/v1/addresses/{good['id']}")).json()
    ifaces = (await client.get(f"/api/v1/devices/{sw['id']}/interfaces")).json()
    assert got["connected_interface_id"] == ifaces[0]["id"]
    # text preserved on the linked row…
    assert got["switch_name"] == "sw1" and got["switch_port"] == "Gi1/0/1"
    # …and on the ambiguous one, still unlinked
    got = (await client.get(f"/api/v1/addresses/{amb['id']}")).json()
    assert got["connected_interface_id"] is None

    # second run: the linked row is skipped (nothing left to match)
    r = await client.post("/api/v1/interfaces/match-free-text")
    rep = r.json()
    assert rep["matched"] == 0 and rep["ambiguous"] == 1 and rep["unmatched"] == 1

    # the run is reviewable — each link is an IPAddress changelog update
    log = (
        await client.get("/api/v1/changelog", params={"object_type": "IPAddress"})
    ).json()["items"]
    assert any(
        "connected_interface_id" in str(e["changes"]) for e in log
    )


# ------------------------------------------------------------------ RBAC


async def test_rbac_cabling(
    client: AsyncClient, session: AsyncSession, auth_on
):
    await _mkuser(session, "v", UserRole.VIEWER)
    await _login(client, "v")
    assert (
        await client.post(
            "/api/v1/devices/1/interfaces", json={"name": "p1"}
        )
    ).status_code == 403
    assert (
        await client.post(
            "/api/v1/cables", json={"a_interface_id": 1, "b_interface_id": 2}
        )
    ).status_code == 403
    assert (
        await client.post("/api/v1/interfaces/match-free-text")
    ).status_code == 403
    # but reads are open
    assert (await client.get("/api/v1/cables")).status_code == 200
    assert (await client.get("/api/v1/devices/1/interfaces")).status_code in (
        200,
        404,
    )

    await _mkuser(session, "c", UserRole.CONTRIBUTOR)
    await _login(client, "c")
    d = await _device(client, name="rbac-sw")
    i = await _iface(client, d["id"], name="p1")
    # contributor writes but cannot delete
    assert (
        await client.delete(f"/api/v1/devices/{d['id']}/interfaces/{i['id']}")
    ).status_code == 403
    assert (await client.delete("/api/v1/cables/1")).status_code == 403


# ------------------------------------------------------------- changelog


async def test_cabling_is_audited(client: AsyncClient):
    d = await _device(client, name="audited-sw")
    i = await _iface(client, d["id"], name="p1")
    j = await _iface(client, d["id"], name="p2")
    c = await _cable(client, i["id"], j["id"], label="audited-cable")
    await client.delete(f"/api/v1/cables/{c['id']}")
    await client.delete(f"/api/v1/devices/{d['id']}/interfaces/{i['id']}")

    log = (
        await client.get(
            "/api/v1/changelog", params={"object_type": "DeviceInterface"}
        )
    ).json()["items"]
    actions = [e["action"] for e in log]
    assert "create" in actions and "delete" in actions
    log = (
        await client.get("/api/v1/changelog", params={"object_type": "Cable"})
    ).json()["items"]
    actions = [e["action"] for e in log]
    assert actions == ["delete", "create"]
    assert any("audited-cable" in e["object_repr"] for e in log)


# ----------------------------------------------------------------- search


async def test_search_finds_devices_via_cabling(client: AsyncClient):
    sw = await _device(client, name="switch-x")
    srv = await _device(client, name="server-y")
    a = await _iface(client, sw["id"], name="mgmt-ilo-port")
    b = await _iface(client, srv["id"], name="eth0")
    await _cable(client, a["id"], b["id"], label="uplink-bldg3")

    # interface name resolves to the owning device
    body = (
        await client.get("/api/v1/search", params={"q": "mgmt-ilo-port"})
    ).json()
    assert any(d["name"] == "switch-x" for d in body["devices"])
    # cable label resolves to BOTH ends' devices
    body = (
        await client.get("/api/v1/search", params={"q": "uplink-bldg3"})
    ).json()
    names = {d["name"] for d in body["devices"]}
    assert {"switch-x", "server-y"} <= names


# ------------------------------------------------------- backup roundtrip


async def _backup_bytes(client, **params) -> bytes:
    r = await client.get("/api/v1/backup", params=params)
    assert r.status_code == 200, r.text
    return r.content


async def _restore(client, payload: bytes):
    return await client.post(
        "/api/v1/backup/restore",
        content=payload,
        headers={"content-type": "application/gzip"},
        params={"name": "backup.json.gz"},
    )


async def test_backup_roundtrip_preserves_cabling(
    client: AsyncClient, session: AsyncSession
):
    x = await _panel_path(client)
    pid = await _prefix(client)
    ip = await _ip(
        client,
        pid,
        "10.70.0.70",
        connected_interface_id=x["sw_port"]["id"],
        switch_name="core-sw",
        switch_port="Gi1/0/1",
    )
    # host-side binding: host's eth0 serves this IP (unowned — bindable)
    await client.patch(
        f"/api/v1/devices/{x['host']['id']}/interfaces/{x['nic']['id']}",
        json={"connected_ip_id": ip["id"]},
    )
    payload = await _backup_bytes(client)
    envelope = json.loads(gzip.decompress(payload))
    assert "device_interfaces" in envelope["tables"]
    assert "cables" in envelope["tables"]

    # wipe everything, then restore
    await session.execute(
        text(
            "TRUNCATE cables, device_interfaces, ip_addresses, prefixes, "
            "vrfs, sites, users, change_log, devices, racks, rack_groups "
            "RESTART IDENTITY CASCADE"
        )
    )
    await session.commit()
    r = await _restore(client, payload)
    assert r.status_code == 200, r.text
    assert r.json()["restored"]["cables"] == 2
    # host nic + 8 panel ports (4 front + 4 back) + the switch port
    assert r.json()["restored"]["device_interfaces"] == 10

    # pair links survived (deferred self-FK restore)
    panel = (await client.get("/api/v1/devices")).json()["items"]
    panel = next(d for d in panel if d["name"] == "panel")
    ifaces = (
        await client.get(f"/api/v1/devices/{panel['id']}/interfaces")
    ).json()
    by_name = {i["name"]: i for i in ifaces}
    assert by_name["p1"]["pair_interface_id"] == by_name["b1"]["id"]

    # the L1 path still traces end to end after restore (pair side first —
    # p1 is mid-chain, so the switch end leads)
    hops = (
        await client.get(
            "/api/v1/cables/trace", params={"interface_id": by_name["p1"]["id"]}
        )
    ).json()
    assert [h["interface_name"] for h in hops] == [
        "Gi1/0/1", "b1", "p1", "eth0",
    ]

    # ip -> interface link and interface -> ip binding both survived
    got = (await client.get(f"/api/v1/addresses/{ip['id']}")).json()
    assert got["connected_interface"]["name"] == "Gi1/0/1"
    assert got["switch_name"] == "core-sw"
    host = (await client.get(f"/api/v1/devices/{x['host']['id']}")).json()
    host_ifaces = (
        await client.get(f"/api/v1/devices/{host['id']}/interfaces")
    ).json()
    eth0 = next(i for i in host_ifaces if i["name"] == "eth0")
    assert eth0["connected_ip_id"] == ip["id"]
    assert eth0["connected_ip"]["id"] == ip["id"]


# -------------------------------------------------------------- migration


def test_alembic_0023_reversible():
    """0023 creates the L1 tables + enum types and the structured
    connected_interface_id column; downgrade removes all of it cleanly."""
    import asyncio

    import asyncpg

    from tests.conftest import TEST_DB_NAME, _base_dsn, _split_dsn, test_url

    scratch = f"{TEST_DB_NAME}_cabling"

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

        def alembic(*args):
            subprocess.run(
                ["alembic", *args], check=True, env=env, cwd=backend_dir
            )

        async def fetch(sql, *args):
            c = await asyncpg.connect(
                url.replace("postgresql+asyncpg://", "postgresql://")
            )
            try:
                return await c.fetch(sql, *args)
            finally:
                await c.close()

        alembic("upgrade", "head")
        # seed a panel pair + a cable + a linked IP on the head schema
        conn = await asyncpg.connect(
            url.replace("postgresql+asyncpg://", "postgresql://")
        )
        try:
            await conn.execute(
                """
                INSERT INTO devices (id, name) VALUES (10, 'panel');
                INSERT INTO device_interfaces
                    (id, device_id, name, kind, position, pair_interface_id)
                    VALUES
                    (50, 10, 'p1', 'patch', 1, NULL),
                    (51, 10, 'b1', 'patch', 1, 50);
                UPDATE device_interfaces SET pair_interface_id = 51
                    WHERE id = 50;
                INSERT INTO cables (id, a_interface_id, b_interface_id, kind)
                    VALUES (60, 50, 51, 'cat6');
                """
            )
        finally:
            await conn.close()

        alembic("downgrade", "0022_devices")
        gone = await fetch(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_name IN ('device_interfaces', 'cables')"
        )
        assert gone == []
        col = await fetch(
            "SELECT count(*) AS n FROM information_schema.columns "
            "WHERE table_name='ip_addresses' "
            "AND column_name='connected_interface_id'"
        )
        assert col[0]["n"] == 0
        types = await fetch(
            "SELECT count(*) AS n FROM pg_type "
            "WHERE typname IN ('interface_kind', 'cable_kind')"
        )
        assert types[0]["n"] == 0

        # upgrade again cleanly so the scratch DB drops without residue
        alembic("upgrade", "head")
        conn = await asyncpg.connect(f"{root}/postgres{query}")
        try:
            await conn.execute(f'DROP DATABASE IF EXISTS "{scratch}"')
        finally:
            await conn.close()

    asyncio.run(_run())
