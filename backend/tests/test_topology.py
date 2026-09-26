"""V10 topology map: /topology/graph aggregate payload (device nodes,
cable-collapsed edges, site/rack groups, unlinked-IP lane), the
diagram_layouts round-trip, backup coverage, and RBAC.

Edge semantics under test: an edge means "a cable directly joins these
two devices" — patch panels appear as their own node, so a host→panel→
switch chain yields host↔panel + panel↔switch edges, never a synthetic
host↔switch one (hop-through belongs to /cables/trace).
"""

import gzip
import json

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.redis import get_redis
from app.core.security import hash_password
from app.models.cabling import DeviceInterface
from app.models.user import User, UserRole

PASSWORD = "topo-test-pw1"


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
    r = await client.post("/api/v1/devices", json={"name": "srv", **kw})
    assert r.status_code == 201, r.text
    return r.json()


async def _site(client: AsyncClient, name: str, slug: str) -> dict:
    r = await client.post("/api/v1/sites", json={"name": name, "slug": slug})
    assert r.status_code == 201, r.text
    return r.json()


async def _rack(client: AsyncClient, **kw) -> dict:
    r = await client.post(
        "/api/v1/racks", json={"name": "R1", "height_u": 12, "width": 19, **kw}
    )
    assert r.status_code == 201, r.text
    return r.json()


async def _rack_group(client: AsyncClient, **kw) -> dict:
    r = await client.post("/api/v1/rack-groups", json={"name": "Row A", **kw})
    assert r.status_code == 201, r.text
    return r.json()


async def _racked(client: AsyncClient, rack_id: int, **kw) -> dict:
    r = await client.post(
        f"/api/v1/racks/{rack_id}/devices",
        json={"name": "srv", "u_position": 1, "u_height": 1, "face": "front", **kw},
    )
    assert r.status_code == 201, r.text
    return r.json()


async def _iface(client: AsyncClient, device_id: int, **kw) -> dict:
    r = await client.post(
        f"/api/v1/devices/{device_id}/interfaces", json={"name": "p1", **kw}
    )
    assert r.status_code == 201, r.text
    return r.json()


async def _gen(client: AsyncClient, device_id: int, **kw) -> list[dict]:
    r = await client.post(
        f"/api/v1/devices/{device_id}/interfaces/generate",
        json={"kind": "rj45", "prefix": "p", "count": 4, **kw},
    )
    assert r.status_code == 201, r.text
    return r.json()


async def _cable(client: AsyncClient, a: int, b: int, **kw) -> dict:
    r = await client.post(
        "/api/v1/cables", json={"a_interface_id": a, "b_interface_id": b, **kw}
    )
    assert r.status_code == 201, r.text
    return r.json()


async def _prefix(client: AsyncClient, cidr: str = "10.80.0.0/24", **kw) -> int:
    vrfs = (await client.get("/api/v1/vrfs")).json()
    vrf = (vrfs["items"] if isinstance(vrfs, dict) else vrfs)[0]
    r = await client.post(
        "/api/v1/prefixes",
        json={"prefix": cidr, "vrf_id": vrf["id"], **kw},
    )
    assert r.status_code == 201, r.text
    return r.json()["id"]


async def _ip(client: AsyncClient, prefix_id: int, addr: str, **kw) -> dict:
    r = await client.post(
        "/api/v1/addresses", json={"address": addr, "prefix_id": prefix_id, **kw}
    )
    assert r.status_code == 201, r.text
    return r.json()


async def _graph(client: AsyncClient, **params) -> dict:
    r = await client.get("/api/v1/topology/graph", params=params)
    assert r.status_code == 200, r.text
    return r.json()


def _edge(graph: dict, a: str, b: str) -> dict | None:
    for e in graph["edges"]:
        if {e["a"], e["b"]} == {a, b}:
            return e
    return None


# ------------------------------------------------------------------- graph


async def test_empty_db_returns_empty_graph(client: AsyncClient):
    g = await _graph(client)
    assert g["nodes"] == [] and g["edges"] == []
    assert g["groups"] == {"sites": [], "rack_groups": [], "racks": []}


async def test_devices_become_nodes(client: AsyncClient):
    site = await _site(client, "HQ", "hq")
    group = await _rack_group(client, site_id=site["id"])
    rack = await _rack(
        client, name="R7", site_id=site["id"], group_id=group["id"]
    )
    racked = await _racked(client, rack["id"], name="sw-core-1")
    unracked = await _device(client, name="loose-pi")

    g = await _graph(client)
    by_id = {n["id"]: n for n in g["nodes"]}
    assert set(by_id) == {f"dev-{racked['id']}", f"dev-{unracked['id']}"}

    n = by_id[f"dev-{racked['id']}"]
    assert n["kind"] == "device" and n["label"] == "sw-core-1"
    assert n["health"] == "unmonitored"  # no linked IPs
    assert n["site_id"] == site["id"]  # effective site via the rack
    assert n["rack_id"] == rack["id"]
    assert n["rack_group_id"] == group["id"]
    assert n["href"] == f"/devices/{racked['id']}"
    assert n["interface_count"] == 0 and n["cabled_count"] == 0

    u = by_id[f"dev-{unracked['id']}"]
    assert u["site_id"] is None and u["rack_id"] is None

    # groups carry the compound-node vocabulary, unfiltered
    assert g["groups"]["sites"] == [{"id": site["id"], "name": "HQ"}]
    assert g["groups"]["rack_groups"] == [
        {"id": group["id"], "name": "Row A", "site_id": site["id"]}
    ]
    assert g["groups"]["racks"] == [
        {
            "id": rack["id"],
            "name": "R7",
            "site_id": site["id"],
            "group_id": group["id"],
        }
    ]


async def test_health_is_worst_of_linked_ips(client: AsyncClient):
    pid = await _prefix(client)
    dev = await _device(client, name="multi-ip")
    await _ip(client, pid, "10.80.0.10", status="active", device_id=dev["id"])
    await _ip(client, pid, "10.80.0.11", status="offline", device_id=dev["id"])

    g = await _graph(client)
    (n,) = g["nodes"]
    assert n["health"] == "offline"


async def test_cables_collapse_to_edges(client: AsyncClient):
    a = await _device(client, name="sw-a")
    b = await _device(client, name="sw-b")
    c = await _device(client, name="sw-c")
    ia = await _gen(client, a["id"], count=3)
    ib = await _gen(client, b["id"], count=2)
    ic = await _gen(client, c["id"], count=1)
    await _cable(client, ia[0]["id"], ib[0]["id"], kind="cat6a")
    await _cable(client, ia[1]["id"], ib[1]["id"], kind="dac")
    await _cable(client, ic[0]["id"], ia[2]["id"], kind="fiber_sm")

    g = await _graph(client)
    e = _edge(g, f"dev-{a['id']}", f"dev-{b['id']}")
    assert e is not None
    assert e["count"] == 2
    assert sorted(e["kinds"]) == ["cat6a", "dac"]
    assert e["mismatched"] is False
    # member cables resolve both ends for the popover
    labels = [(cbl["a_label"], cbl["b_label"]) for cbl in e["cables"]]
    assert ("sw-a · p1", "sw-b · p1") in labels
    assert ("sw-a · p2", "sw-b · p2") in labels

    e2 = _edge(g, f"dev-{a['id']}", f"dev-{c['id']}")
    assert e2 is not None and e2["count"] == 1 and e2["kinds"] == ["fiber_sm"]
    assert _edge(g, f"dev-{b['id']}", f"dev-{c['id']}") is None


async def test_patch_panel_chain_does_not_short_circuit(client: AsyncClient):
    """host → panel front p1 (pair b1) → switch: the map shows the two
    documented cables (host↔panel, panel↔switch), not a host↔switch edge."""
    host = await _device(client, name="host")
    panel = await _device(client, name="panel")
    sw = await _device(client, name="core-sw")
    nic = await _iface(client, host["id"], name="eth0")
    fronts = await _gen(
        client, panel["id"], kind="patch", prefix="p", pair_prefix="b", count=4
    )
    by_name = {r["name"]: r for r in fronts}
    sw_port = await _iface(client, sw["id"], name="Gi1/0/1")
    await _cable(client, nic["id"], by_name["p1"]["id"], kind="cat6")
    await _cable(client, by_name["b1"]["id"], sw_port["id"], kind="cat6a")

    g = await _graph(client)
    assert _edge(g, f"dev-{host['id']}", f"dev-{panel['id']}") is not None
    assert _edge(g, f"dev-{panel['id']}", f"dev-{sw['id']}") is not None
    # honest edges only — no synthetic hop-through edge
    assert _edge(g, f"dev-{host['id']}", f"dev-{sw['id']}") is None
    assert len(g["edges"]) == 2


async def test_mismatched_flag_flows(
    client: AsyncClient, session: AsyncSession
):
    a = await _device(client, name="sw-a")
    b = await _device(client, name="sw-b")
    ia = await _iface(client, a["id"], name="u1")
    ib = await _iface(client, b["id"], name="u1")
    await _cable(client, ia["id"], ib["id"])

    assert _edge(await _graph(client), f"dev-{a['id']}", f"dev-{b['id']}")[
        "mismatched"
    ] is False

    # v8.2 poll output: validation blob carrying the cable_mismatch flag
    iface = await session.scalar(
        select(DeviceInterface).where(DeviceInterface.id == ia["id"])
    )
    iface.validation = {
        "cable_mismatch": {"reason": "lldp_neighbor", "detail": "sees sw-z"}
    }
    await session.commit()

    e = _edge(await _graph(client), f"dev-{a['id']}", f"dev-{b['id']}")
    assert e["mismatched"] is True


async def test_site_id_filter(client: AsyncClient):
    s1 = await _site(client, "HQ", "hq")
    s2 = await _site(client, "Branch", "br")
    rack = await _rack(client, site_id=s1["id"])
    in_s1 = await _racked(client, rack["id"], name="s1-dev")  # site via rack
    in_s2 = await _device(client, name="s2-dev", site_id=s2["id"])
    nosite = await _device(client, name="nosite-dev")
    ia = await _iface(client, in_s1["id"], name="u1")
    ib = await _iface(client, in_s2["id"], name="u1")
    ib2 = await _iface(client, in_s2["id"], name="u2")
    ic = await _iface(client, nosite["id"], name="u1")
    await _cable(client, ia["id"], ib["id"])  # cross-site cable
    await _cable(client, ib2["id"], ic["id"])  # site2 ↔ nosite

    g = await _graph(client, site_id=s1["id"])
    assert [n["id"] for n in g["nodes"]] == [f"dev-{in_s1['id']}"]
    # the cross-site cable has a non-renderable far end — dropped
    assert g["edges"] == []
    # groups stay unfiltered so the picker keeps every site
    assert {s["name"] for s in g["groups"]["sites"]} == {"HQ", "Branch"}

    g = await _graph(client, site_id=s2["id"])
    assert [n["id"] for n in g["nodes"]] == [f"dev-{in_s2['id']}"]
    assert g["edges"] == []


async def test_include_unlinked(client: AsyncClient):
    site = await _site(client, "HQ", "hq")
    pid = await _prefix(client, site_id=site["id"])
    ip = await _ip(
        client, pid, "10.80.0.9", status="active", hostname="mystery"
    )
    dev = await _device(client, name="sw")
    pid2 = await _prefix(client, "10.81.0.0/24")
    await _ip(client, pid2, "10.81.0.9", device_id=dev["id"])  # linked

    # default: devices only
    g = await _graph(client)
    assert [n["id"] for n in g["nodes"]] == [f"dev-{dev['id']}"]

    g = await _graph(client, include_unlinked=1)
    by_id = {n["id"]: n for n in g["nodes"]}
    n = by_id[f"unlinked-{ip['id']}"]
    assert n["kind"] == "ip" and n["label"] == "10.80.0.9 (mystery)"
    assert n["health"] == "active"
    assert n["site_id"] == site["id"]  # inherited from the prefix
    assert n["href"] == f"/prefixes/{pid}?q=10.80.0.9"
    # the linked address and the unlinked one under another site
    assert f"unlinked-{ip['id']}" in by_id

    # site filter applies to unlinked hosts via their prefix's site
    g = await _graph(client, include_unlinked=1, site_id=site["id"])
    ids = {n["id"] for n in g["nodes"]}
    assert f"unlinked-{ip['id']}" in ids
    assert f"dev-{dev['id']}" not in ids  # dev has no site


# ------------------------------------------------------------------ layout


async def test_layout_roundtrip(client: AsyncClient):
    # nothing saved yet → empty positions, not an error
    got = (await client.get("/api/v1/topology/layout")).json()
    assert got["key"] == "main" and got["positions"] == {}

    positions = {"dev-12": {"x": 40.0, "y": 120.5}, "rack-7": {"x": 0, "y": 0}}
    r = await client.put(
        "/api/v1/topology/layout",
        json={"key": "main", "positions": positions},
    )
    assert r.status_code == 200, r.text
    assert r.json()["positions"] == positions
    assert r.json()["updated_at"] is not None

    got = (await client.get("/api/v1/topology/layout")).json()
    assert got["positions"]["dev-12"] == {"x": 40.0, "y": 120.5}

    # replace semantics: a second PUT overwrites the whole blob
    r = await client.put(
        "/api/v1/topology/layout",
        json={"positions": {"dev-40": {"x": 9, "y": 9}}},
    )
    assert r.status_code == 200
    got = (await client.get("/api/v1/topology/layout")).json()
    assert got["positions"] == {"dev-40": {"x": 9.0, "y": 9.0}}

    # a second key is an independent layout
    got = (
        await client.get("/api/v1/topology/layout", params={"key": "site-3"})
    ).json()
    assert got["positions"] == {}


async def test_layout_put_validation(client: AsyncClient):
    r = await client.put(
        "/api/v1/topology/layout",
        json={"positions": {"dev-1": {"x": "not-a-number", "y": 0}}},
    )
    assert r.status_code == 422
    r = await client.put(
        "/api/v1/topology/layout",
        json={"positions": {"dev-1": {"x": 0, "y": 0, "z": 1}}},
    )
    assert r.status_code == 422  # extra keys are rejected, not stored
    r = await client.put(
        "/api/v1/topology/layout",
        json={"key": "k" * 65, "positions": {}},
    )
    assert r.status_code == 422


async def test_backup_covers_diagram_layouts(client: AsyncClient):
    await client.put(
        "/api/v1/topology/layout",
        json={"positions": {"dev-1": {"x": 1, "y": 2}}},
    )
    r = await client.get("/api/v1/backup")
    assert r.status_code == 200
    envelope = json.loads(gzip.decompress(r.content))
    assert "diagram_layouts" in envelope["tables"]
    rows = envelope["tables"]["diagram_layouts"]
    assert rows[0]["key"] == "main"
    assert rows[0]["positions"] == {"dev-1": {"x": 1, "y": 2}}

    # restore round-trips the layout blob
    r = await client.post(
        "/api/v1/backup/restore",
        content=r.content,
        headers={"content-type": "application/gzip"},
        params={"name": "backup.json.gz"},
    )
    assert r.status_code == 200, r.text
    got = (await client.get("/api/v1/topology/layout")).json()
    assert got["positions"] == {"dev-1": {"x": 1, "y": 2}}


# -------------------------------------------------------------------- RBAC


async def test_topology_rbac(
    client: AsyncClient, session: AsyncSession, auth_on
):
    await _mkuser(session, "viewer1", UserRole.VIEWER)
    await _mkuser(session, "contrib1", UserRole.CONTRIBUTOR)

    # unauthenticated
    from app.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as anon:
        assert (await anon.get("/api/v1/topology/graph")).status_code == 401
        assert (await anon.get("/api/v1/topology/layout")).status_code == 401
        assert (
            await anon.put("/api/v1/topology/layout", json={"positions": {}})
        ).status_code == 401

    await _login(client, "viewer1")
    assert (await client.get("/api/v1/topology/graph")).status_code == 200
    assert (await client.get("/api/v1/topology/layout")).status_code == 200
    r = await client.put(
        "/api/v1/topology/layout", json={"positions": {"dev-1": {"x": 1, "y": 2}}}
    )
    assert r.status_code == 403  # viewer lacks data:write

    await _login(client, "contrib1")
    r = await client.put(
        "/api/v1/topology/layout", json={"positions": {"dev-1": {"x": 1, "y": 2}}}
    )
    assert r.status_code == 200


async def test_layout_not_audited(client: AsyncClient):
    """Layout churn is UI state — a save must not write change_log rows."""
    await client.put(
        "/api/v1/topology/layout",
        json={"positions": {"dev-1": {"x": 1, "y": 2}}},
    )
    r = await client.get(
        "/api/v1/changelog", params={"object_type": "DiagramLayout"}
    )
    assert r.json()["items"] == []
