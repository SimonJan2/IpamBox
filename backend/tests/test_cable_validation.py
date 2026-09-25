"""V8.2 cable validation — the physical-layer twin of mac_mismatch.

Three evidence-based checks run at the tail of ``poll_device`` and land
as ``device_interfaces.validation["cable_mismatch"]`` flags:

1. documented-but-down — cabled port reports oper=down;
2. far-end absent — bridge learned other MACs but none of the peer's;
3. undocumented neighbor — LLDP reports a neighbor on an uncabled port.

Absent evidence is never a violation: missing walks skip their check
entirely and never clear an open flag. No live SNMP — pysnmp is mocked
at the module boundary, same as test_snmp.
"""
from datetime import datetime, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.core.config import get_settings
from app.models.cabling import DeviceInterface
from app.models.change_log import ChangeLog
from app.models.device import Device
from app.models.ip_address import IPAddress
from app.models.review import ReviewDismissal
from app.services import cable_validation, notify
from app.services import snmp as snmp_svc

PASSWORD = "cableval-test-pw1"


@pytest.fixture
def key(monkeypatch):
    """Provision a master key on the cached settings object."""
    s = get_settings()
    monkeypatch.setattr(s, "ipambox_secret_key", "cv-test-key")
    monkeypatch.setattr(s, "ipambox_secret_key_file", "")
    return s


# --- helpers (mirrors test_snmp) --------------------------------------------


async def _device(client: AsyncClient, **kw) -> dict:
    r = await client.post("/api/v1/devices", json={"name": "sw1", **kw})
    assert r.status_code == 201, r.text
    return r.json()


async def _iface(client: AsyncClient, device_id: int, **kw) -> dict:
    r = await client.post(
        f"/api/v1/devices/{device_id}/interfaces",
        json={"name": "Gi0/1", **kw},
    )
    assert r.status_code == 201, r.text
    return r.json()


async def _cable(
    client: AsyncClient, a_interface_id: int, b_interface_id: int, **kw
) -> dict:
    r = await client.post(
        "/api/v1/cables",
        json={"a_interface_id": a_interface_id,
              "b_interface_id": b_interface_id, **kw},
    )
    assert r.status_code == 201, r.text
    return r.json()


async def _prefix(client: AsyncClient, cidr: str = "10.82.0.0/24") -> int:
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


def _enable(client: AsyncClient, device_id: int, **over):
    body = {
        "snmp_enabled": True,
        "snmp_version": "v2c",
        "snmp_cred": {"community": "public"},
        **over,
    }
    return client.patch(f"/api/v1/devices/{device_id}", json=body)


async def _orm_device(session, device_id: int) -> Device:
    d = await session.get(Device, device_id)
    assert d is not None
    return d


def _up(name="sw-core-1", descr="FakeOS 1.0"):
    return {"up": True, "sys_name": name, "sys_descr": descr, "error": None}


def _ifrow(idx, name, oper="up", admin="up", speed=1000, mac=None):
    return {
        "if_index": idx,
        "name": name,
        "oper": oper,
        "admin": admin,
        "speed_mbps": speed,
        "mac": mac,
    }


def _mock_poll(monkeypatch, *, test=None, ifs=(), bridge=None, lldp=None):
    """Point every network primitive at canned data (test_snmp's seam)."""
    async def _test(dev, host, *, timeout):
        return test if test is not None else _up()

    async def _ifs(dev, host, *, timeout):
        return list(ifs)

    async def _bridge(dev, host, *, timeout):
        return dict(bridge or {})

    async def _lldp(dev, host, *, timeout):
        return list(lldp or [])

    monkeypatch.setattr(snmp_svc, "test_device", _test)
    monkeypatch.setattr(snmp_svc, "walk_if_mib", _ifs)
    monkeypatch.setattr(snmp_svc, "walk_bridge_macs", _bridge)
    monkeypatch.setattr(snmp_svc, "walk_lldp", _lldp)


async def _switch(client, session, key, cidr="10.82.0.0/24"):
    """An SNMP-managed device with a pollable IP. Returns (device, dev_row)."""
    d = await _device(client)
    r = await _enable(client, d["id"])
    assert r.status_code == 200, r.text
    pid = await _prefix(client, cidr)
    await _ip(client, pid, cidr.split(".0/")[0] + ".5", device_id=d["id"])
    return d, await _orm_device(session, d["id"])


async def _commit_fresh(session):
    """commit + expunge: poll_device's Core updates / bulk validation
    writes bypass ORM session state — dropping the identity map makes
    later reads see what a NEW request session would (stale copies are
    a test artifact of the shared-session client override)."""
    await session.commit()
    session.expunge_all()


async def _flag(session, iface_id: int):
    # populate_existing — validate_device writes via bulk update() with
    # synchronize_session=False, so the identity map holds stale blobs.
    i = await session.get(DeviceInterface, iface_id, populate_existing=True)
    assert i is not None
    return (i.validation or {}).get("cable_mismatch")


async def _fresh_iface(session, iface_id: int) -> DeviceInterface:
    i = await session.get(DeviceInterface, iface_id, populate_existing=True)
    assert i is not None
    return i


async def _review(client: AsyncClient) -> dict:
    r = await client.get("/api/v1/review")
    assert r.status_code == 200, r.text
    return r.json()


def _section(review: dict, key: str) -> dict:
    return next(s for s in review["sections"] if s["key"] == key)


# --- check 1: documented-but-down --------------------------------------------


async def test_cabled_down_port_flags(
    client, session, key, monkeypatch
):
    d, dev = await _switch(client, session, key)
    i1 = await _iface(client, d["id"], name="Gi0/1")
    peer = await _device(client, name="srv-a")
    p1 = await _iface(client, peer["id"], name="eth0")
    cable = await _cable(client, i1["id"], p1["id"])

    _mock_poll(monkeypatch, ifs=[_ifrow(1, "Gi0/1", oper="down")])
    res = await snmp_svc.poll_device(session, dev)
    await _commit_fresh(session)
    assert res["cable_checked"] == 1
    assert res["cable_flags"] == 1
    assert res["cable_flags_raised"] == 1
    assert len(res["cable_flags_new"]) == 1
    assert res["cable_flags_new"][0]["reason"] == "documented_down"

    flag = await _flag(session, i1["id"])
    assert flag["reason"] == "documented_down"
    assert flag["cable_id"] == cable["id"]
    assert flag["at"]
    # the row the API serves carries the same flag
    got = (await client.get(f"/api/v1/devices/{d['id']}/interfaces")).json()
    assert got[0]["validation"]["cable_mismatch"]["reason"] == "documented_down"
    # device header count
    detail = (await client.get(f"/api/v1/devices/{d['id']}")).json()
    assert detail["flagged_count"] == 1


async def test_down_flag_clears_on_recovery(
    client, session, key, monkeypatch
):
    d, dev = await _switch(client, session, key)
    i1 = await _iface(client, d["id"], name="Gi0/1")
    peer = await _device(client, name="srv-a")
    p1 = await _iface(client, peer["id"], name="eth0")
    await _cable(client, i1["id"], p1["id"])

    _mock_poll(monkeypatch, ifs=[_ifrow(1, "Gi0/1", oper="down")])
    res = await snmp_svc.poll_device(session, dev)
    await _commit_fresh(session)
    first_at = (await _flag(session, i1["id"]))["at"]

    # same condition polled again — flag keeps its first-seen `at` and
    # is NOT re-raised (raised deltas drive the notify emit)
    res = await snmp_svc.poll_device(session, dev)
    await _commit_fresh(session)
    assert res["cable_flags_raised"] == 0
    assert res["cable_flags_new"] == []
    assert (await _flag(session, i1["id"]))["at"] == first_at

    _mock_poll(monkeypatch, ifs=[_ifrow(1, "Gi0/1", oper="up")])
    res = await snmp_svc.poll_device(session, dev)
    await _commit_fresh(session)
    assert res["cable_flags_cleared"] == 1
    i = await _fresh_iface(session, i1["id"])
    assert i.validation is None or "cable_mismatch" not in i.validation


async def test_uncabled_down_port_no_flag(
    client, session, key, monkeypatch
):
    """down with nothing documented isn't a finding."""
    d, dev = await _switch(client, session, key)
    await _iface(client, d["id"], name="Gi0/1")
    _mock_poll(monkeypatch, ifs=[_ifrow(1, "Gi0/1", oper="down")])
    res = await snmp_svc.poll_device(session, dev)
    await _commit_fresh(session)
    assert res["cable_flags"] == 0
    got = (await client.get(f"/api/v1/devices/{d['id']}/interfaces")).json()
    assert not (got[0]["validation"] or {}).get("cable_mismatch")


# --- check 2: far-end MAC absent ----------------------------------------------


async def _peer_with_mac(client, mac="AA:BB:CC:DD:EE:01", name="srv-a"):
    peer = await _device(client, name=name)
    p1 = await _iface(client, peer["id"], name="eth0", mac_address=mac)
    return peer, p1


async def test_far_end_mac_absent_flags(
    client, session, key, monkeypatch
):
    d, dev = await _switch(client, session, key)
    i1 = await _iface(client, d["id"], name="Gi0/1")
    _, p1 = await _peer_with_mac(client)
    await _cable(client, i1["id"], p1["id"])

    # The port learned MACs — just none belonging to the documented peer.
    _mock_poll(
        monkeypatch,
        ifs=[_ifrow(1, "Gi0/1")],
        bridge={1: ["00:11:22:33:44:55", "00:66:77:88:99:AA"]},
    )
    res = await snmp_svc.poll_device(session, dev)
    await _commit_fresh(session)
    flag = await _flag(session, i1["id"])
    assert flag is not None
    assert flag["reason"] == "far_end_absent"
    assert "srv-a" in flag["detail"]
    assert res["cable_flags"] == 1
    # learned MACs land in the evidence blob (bounded)
    i = await _fresh_iface(session, i1["id"])
    assert "00:11:22:33:44:55" in i.validation["macs_seen"]


async def test_peer_mac_present_no_flag(
    client, session, key, monkeypatch
):
    """The peer's own MAC learned on the port → documented truth holds."""
    d, dev = await _switch(client, session, key)
    i1 = await _iface(client, d["id"], name="Gi0/1")
    _, p1 = await _peer_with_mac(client, mac="AA:BB:CC:DD:EE:01")
    await _cable(client, i1["id"], p1["id"])

    _mock_poll(
        monkeypatch,
        ifs=[_ifrow(1, "Gi0/1")],
        bridge={1: ["aa:bb:cc:dd:ee:01", "00:11:22:33:44:55"]},
    )
    res = await snmp_svc.poll_device(session, dev)
    await _commit_fresh(session)
    assert res["cable_flags"] == 0
    assert await _flag(session, i1["id"]) is None


async def test_silent_port_no_flag(
    client, session, key, monkeypatch
):
    """A port that learned NO MACs is silent — silence isn't evidence."""
    d, dev = await _switch(client, session, key)
    i1 = await _iface(client, d["id"], name="Gi0/1")
    _, p1 = await _peer_with_mac(client)
    await _cable(client, i1["id"], p1["id"])

    _mock_poll(
        monkeypatch,
        ifs=[_ifrow(1, "Gi0/1")],
        bridge={1: [], 2: ["00:11:22:33:44:55"]},  # port 1 silent
    )
    res = await snmp_svc.poll_device(session, dev)
    await _commit_fresh(session)
    assert res["cable_flags"] == 0
    assert await _flag(session, i1["id"]) is None


async def test_peer_with_no_known_macs_no_flag(
    client, session, key, monkeypatch
):
    """far_end_absent needs an expected set — an unknown peer can't be
    absent from it."""
    d, dev = await _switch(client, session, key)
    i1 = await _iface(client, d["id"], name="Gi0/1")
    peer = await _device(client, name="srv-no-mac")
    p1 = await _iface(client, peer["id"], name="eth0")  # no mac_address
    await _cable(client, i1["id"], p1["id"])

    _mock_poll(
        monkeypatch,
        ifs=[_ifrow(1, "Gi0/1")],
        bridge={1: ["00:11:22:33:44:55"]},
    )
    res = await snmp_svc.poll_device(session, dev)
    await _commit_fresh(session)
    assert res["cable_flags"] == 0
    assert await _flag(session, i1["id"]) is None


# --- check 3: undocumented LLDP neighbor --------------------------------------


def _lldp_row(local_port_id, remote="esxi-2", port="vmnic1", mac="00:11:22:33:44:66"):
    return {
        "local_port": 7,
        "local_port_id": local_port_id,
        "remote_name": remote,
        "remote_port": port,
        "remote_mac": mac,
    }


async def test_lldp_neighbor_on_uncabled_port_flags(
    client, session, key, monkeypatch
):
    d, dev = await _switch(client, session, key)
    i1 = await _iface(client, d["id"], name="Gi0/9")

    _mock_poll(
        monkeypatch,
        ifs=[_ifrow(1, "Gi0/9")],
        lldp=[_lldp_row("Gi0/9")],
    )
    res = await snmp_svc.poll_device(session, dev)
    await _commit_fresh(session)
    flag = await _flag(session, i1["id"])
    assert flag is not None
    assert flag["reason"] == "lldp_neighbor"
    assert flag["remote_name"] == "esxi-2"
    assert "esxi-2" in flag["detail"]
    assert res["lldp_neighbors"] == 1


async def test_lldp_neighbor_on_cabled_port_no_flag(
    client, session, key, monkeypatch
):
    """A documented cable answering the neighbor is fine — check 3 only
    flags MISSING cables, never audits the far end's identity."""
    d, dev = await _switch(client, session, key)
    i1 = await _iface(client, d["id"], name="Gi0/9")
    peer = await _device(client, name="srv-a")
    p1 = await _iface(client, peer["id"], name="eth0")
    await _cable(client, i1["id"], p1["id"])

    _mock_poll(
        monkeypatch,
        ifs=[_ifrow(1, "Gi0/9")],
        lldp=[_lldp_row("Gi0/9")],
    )
    res = await snmp_svc.poll_device(session, dev)
    await _commit_fresh(session)
    assert res["cable_flags"] == 0
    # ...but the observed neighbor still lands in the evidence blob
    i = await _fresh_iface(session, i1["id"])
    assert i.validation["lldp"][0]["remote_name"] == "esxi-2"


async def test_lldp_flag_clears_when_cable_documented(
    client, session, key, monkeypatch
):
    d, dev = await _switch(client, session, key)
    i1 = await _iface(client, d["id"], name="Gi0/9")
    _mock_poll(
        monkeypatch,
        ifs=[_ifrow(1, "Gi0/9")],
        lldp=[_lldp_row("Gi0/9")],
    )
    await snmp_svc.poll_device(session, dev)
    await _commit_fresh(session)
    assert await _flag(session, i1["id"]) is not None

    # documenting the cable clears via clear_validation (cable create)
    peer = await _device(client, name="srv-a")
    p1 = await _iface(client, peer["id"], name="eth0")
    await _cable(client, i1["id"], p1["id"])
    assert await _flag(session, i1["id"]) is None


# --- evidence gaps: missing walks skip, never clear ---------------------------


async def test_missing_walks_skip_cleanly(
    client, session, key, monkeypatch
):
    """fills_connected off → no bridge evidence; lldp walk failed → no
    LLDP evidence. Neither check can raise or clear."""
    d, dev = await _switch(client, session, key)
    i1 = await _iface(client, d["id"], name="Gi0/1")
    _, p1 = await _peer_with_mac(client)
    await _cable(client, i1["id"], p1["id"])

    # raise a far_end flag first
    _mock_poll(
        monkeypatch,
        ifs=[_ifrow(1, "Gi0/1")],
        bridge={1: ["00:11:22:33:44:55"]},
    )
    await snmp_svc.poll_device(session, dev)
    await _commit_fresh(session)
    assert await _flag(session, i1["id"]) is not None

    # now poll with bridge collection OFF — the flag can't be re-proven,
    # and must NOT be cleared by absent evidence
    _mock_poll(monkeypatch, ifs=[_ifrow(1, "Gi0/1")])  # walk_bridge unused
    res = await snmp_svc.poll_device(
        session, dev, fills_connected=False
    )
    await _commit_fresh(session)
    assert res["cable_flags_cleared"] == 0
    assert await _flag(session, i1["id"]) is not None


async def test_walk_failure_keeps_flags(
    client, session, key, monkeypatch
):
    """A failed LLDP walk (SnmpError → lldp=None) leaves an open
    lldp_neighbor flag standing — absent evidence isn't disproof."""
    d, dev = await _switch(client, session, key)
    i1 = await _iface(client, d["id"], name="Gi0/9")
    _mock_poll(
        monkeypatch,
        ifs=[_ifrow(1, "Gi0/9")],
        lldp=[_lldp_row("Gi0/9")],
    )
    await snmp_svc.poll_device(session, dev)
    await _commit_fresh(session)
    assert await _flag(session, i1["id"]) is not None

    from app.services.snmp import SnmpError

    async def _boom(dev, host, *, timeout):
        raise SnmpError("timeout")

    monkeypatch.setattr(snmp_svc, "walk_lldp", _boom)
    res = await snmp_svc.poll_device(session, dev)
    await _commit_fresh(session)
    assert "lldp-mib" in res["error"]
    assert res["cable_flags_cleared"] == 0
    assert await _flag(session, i1["id"]) is not None


# --- provenance: unmanaged/manual devices -------------------------------------


async def test_unmanaged_port_never_flagged(session):
    """An unmanaged (un-polled) device has no SNMP evidence — its ports
    can never be 'covered', so validate_device flags nothing even when
    called directly."""
    dev = Device(name="bare", snmp_enabled=False)
    session.add(dev)
    await _commit_fresh(session)
    i = DeviceInterface(device_id=dev.id, name="eth0", source="manual")
    session.add(i)
    await _commit_fresh(session)

    res = await cable_validation.validate_device(
        session, dev, polled=[], bridge={}, lldp=[],
        now=datetime.now(timezone.utc),
    )
    assert res["checked"] == 0
    assert res["flagged"] == 0
    i = await _fresh_iface(session, i.id)
    assert i.validation is None


async def test_manual_port_without_evidence_no_flag(
    client, session, key, monkeypatch
):
    """A hand-drawn cabled port the device never reports (no if_index,
    not in any walk) is uncovered — absent evidence, no flag."""
    d, dev = await _switch(client, session, key)
    i1 = await _iface(client, d["id"], name="AUX-0")
    peer = await _device(client, name="srv-a")
    p1 = await _iface(client, peer["id"], name="eth0")
    await _cable(client, i1["id"], p1["id"])

    _mock_poll(monkeypatch, ifs=[_ifrow(1, "Gi0/1")])
    res = await snmp_svc.poll_device(session, dev)
    await _commit_fresh(session)
    i = await _fresh_iface(session, i1["id"])
    assert i.validation is None or "cable_mismatch" not in i.validation
    assert res["cable_flags"] == 0


# --- mutations clear the flag --------------------------------------------------


async def test_cable_patch_clears_flag(
    client, session, key, monkeypatch
):
    d, dev = await _switch(client, session, key)
    i1 = await _iface(client, d["id"], name="Gi0/1")
    _, p1 = await _peer_with_mac(client)
    cable = await _cable(client, i1["id"], p1["id"])

    _mock_poll(monkeypatch, ifs=[_ifrow(1, "Gi0/1", oper="down")])
    await snmp_svc.poll_device(session, dev)
    await _commit_fresh(session)
    assert await _flag(session, i1["id"]) is not None

    r = await client.patch(
        f"/api/v1/cables/{cable['id']}", json={"label": "re-patched"}
    )
    assert r.status_code == 200, r.text
    # PATCH drops the flag keys — the next poll re-derives the truth
    assert await _flag(session, i1["id"]) is None
    i = await _fresh_iface(session, i1["id"])
    assert "cable_mismatch" not in (i.validation or {})


async def test_cable_delete_clears_flag(
    client, session, key, monkeypatch
):
    d, dev = await _switch(client, session, key)
    i1 = await _iface(client, d["id"], name="Gi0/1")
    _, p1 = await _peer_with_mac(client)
    cable = await _cable(client, i1["id"], p1["id"])

    _mock_poll(monkeypatch, ifs=[_ifrow(1, "Gi0/1", oper="down")])
    await snmp_svc.poll_device(session, dev)
    await _commit_fresh(session)
    assert await _flag(session, i1["id"]) is not None

    r = await client.delete(f"/api/v1/cables/{cable['id']}")
    assert r.status_code == 204
    assert await _flag(session, i1["id"]) is None


async def test_interface_patch_clears_flag(
    client, session, key, monkeypatch
):
    d, dev = await _switch(client, session, key)
    i1 = await _iface(client, d["id"], name="Gi0/1")
    _, p1 = await _peer_with_mac(client)
    await _cable(client, i1["id"], p1["id"])

    _mock_poll(monkeypatch, ifs=[_ifrow(1, "Gi0/1", oper="down")])
    await snmp_svc.poll_device(session, dev)
    await _commit_fresh(session)
    assert await _flag(session, i1["id"]) is not None

    r = await client.patch(
        f"/api/v1/devices/{d['id']}/interfaces/{i1['id']}",
        json={"speed_mbps": 10000},
    )
    assert r.status_code == 200, r.text
    assert await _flag(session, i1["id"]) is None


# --- review center + dashboard -------------------------------------------------


async def test_review_section_and_sticky_dismissal(
    client, session, key, monkeypatch
):
    d, dev = await _switch(client, session, key)
    i1 = await _iface(client, d["id"], name="Gi0/1")
    _, p1 = await _peer_with_mac(client)
    cable = await _cable(client, i1["id"], p1["id"])

    _mock_poll(monkeypatch, ifs=[_ifrow(1, "Gi0/1", oper="down")])
    await snmp_svc.poll_device(session, dev)
    await _commit_fresh(session)

    sec = _section(await _review(client), "cable_mismatch")
    assert sec["count"] == 1
    it = sec["items"][0]
    assert it["entity_type"] == "device_interface"
    assert it["entity_id"] == i1["id"]
    assert it["label"] == f"{d['name']} · Gi0/1"
    assert it["detail"]["reason"] == "documented_down"
    assert it["detail"]["device_id"] == d["id"]
    assert it["fingerprint"] == f"documented_down|c{cable['id']}"

    # dismiss → leaves the open queue, stays recallable
    body = {
        "kind": "cable_mismatch",
        "entity_type": it["entity_type"],
        "entity_id": it["entity_id"],
        "fingerprint": it["fingerprint"],
        "notes": "host is down for maintenance",
    }
    r = await client.post("/api/v1/review/dismiss", json=body)
    assert r.status_code == 200, r.text
    sec = _section(await _review(client), "cable_mismatch")
    assert sec["count"] == 0
    assert len(sec["dismissed"]) == 1
    assert sec["dismissed"][0]["dismiss_notes"] == body["notes"]

    # re-poll keeps flagging the same fingerprint → stays dismissed
    await snmp_svc.poll_device(session, dev)
    await _commit_fresh(session)
    sec = _section(await _review(client), "cable_mismatch")
    assert sec["count"] == 0 and len(sec["dismissed"]) == 1

    # undismiss → back on the open queue
    r = await client.post("/api/v1/review/undismiss", json=body)
    assert r.status_code == 204
    sec = _section(await _review(client), "cable_mismatch")
    assert sec["count"] == 1


async def test_dashboard_counts_flags(
    client, session, key, monkeypatch
):
    d, dev = await _switch(client, session, key)
    i1 = await _iface(client, d["id"], name="Gi0/1")
    _, p1 = await _peer_with_mac(client)
    await _cable(client, i1["id"], p1["id"])

    before = (await client.get("/api/v1/dashboard/stats")).json()
    _mock_poll(monkeypatch, ifs=[_ifrow(1, "Gi0/1", oper="down")])
    await snmp_svc.poll_device(session, dev)
    await _commit_fresh(session)
    after = (await client.get("/api/v1/dashboard/stats")).json()
    assert after["cable_mismatches"] == before["cable_mismatches"] + 1
    item = next(
        i for i in after["cable_mismatch_items"] if i["id"] == i1["id"]
    )
    assert item["device"] == d["name"]
    assert item["port"] == "Gi0/1"
    assert item["reason"] == "documented_down"
    assert item["device_id"] == d["id"]

    # clearing moves the count back down
    _mock_poll(monkeypatch, ifs=[_ifrow(1, "Gi0/1", oper="up")])
    await snmp_svc.poll_device(session, dev)
    await _commit_fresh(session)
    done = (await client.get("/api/v1/dashboard/stats")).json()
    assert done["cable_mismatches"] == before["cable_mismatches"]


# --- audit + notify discipline -------------------------------------------------


async def test_flag_writes_no_changelog(
    client, session, key, monkeypatch
):
    """validation is observed state — bulk update() like oper_status,
    so flag writes never touch the changelog."""
    d, dev = await _switch(client, session, key)
    i1 = await _iface(client, d["id"], name="Gi0/1")
    _, p1 = await _peer_with_mac(client)
    await _cable(client, i1["id"], p1["id"])

    _mock_poll(monkeypatch, ifs=[_ifrow(1, "Gi0/1", oper="down")])
    await snmp_svc.poll_device(session, dev)
    await _commit_fresh(session)
    _mock_poll(monkeypatch, ifs=[_ifrow(1, "Gi0/1", oper="up")])
    await snmp_svc.poll_device(session, dev)
    await _commit_fresh(session)

    logs = (
        (
            await session.execute(
                select(ChangeLog).where(
                    ChangeLog.object_type == "DeviceInterface",
                    ChangeLog.action == "update",
                )
            )
        )
        .scalars()
        .all()
    )
    # observed-state writes (flag raise AND clear) never audit
    assert logs == []


async def test_poll_endpoint_emits_only_on_raise(
    client, session, key, monkeypatch
):
    """The API lane's emit seam: POST snmp/poll pages cable.mismatch when
    a flag is newly raised; a persistent flag stays silent."""
    d, dev = await _switch(client, session, key)
    i1 = await _iface(client, d["id"], name="Gi0/1")
    _, p1 = await _peer_with_mac(client)
    await _cable(client, i1["id"], p1["id"])

    calls: list[str] = []

    async def _rec(event_type, summary, payload=None):
        calls.append(event_type)

    monkeypatch.setattr(notify, "emit", _rec)
    _mock_poll(monkeypatch, ifs=[_ifrow(1, "Gi0/1", oper="down")])
    r = await client.post(f"/api/v1/devices/{d['id']}/snmp/poll")
    assert r.status_code == 200, r.text
    assert calls == ["cable.mismatch"]

    # drop expired/stale identity-map rows so the second request sees
    # what a fresh session would (the first poll's stamps expired dev)
    session.expunge_all()

    # same flag persists → not re-raised → no second event
    r = await client.post(f"/api/v1/devices/{d['id']}/snmp/poll")
    assert r.status_code == 200, r.text
    assert calls == ["cable.mismatch"]


async def test_cable_mismatch_event_shape(monkeypatch):
    """emit_new_flags wraps the poll's new_flags into one cable.mismatch
    event per device; empty input never calls emit."""
    calls: list[tuple] = []

    async def _rec(event_type, summary, payload=None):
        calls.append((event_type, summary, payload))

    monkeypatch.setattr(notify, "emit", _rec)
    await cable_validation.emit_new_flags(7, "sw1", [])
    assert calls == []
    await cable_validation.emit_new_flags(
        7,
        "sw1",
        [{"interface_id": 3, "interface": "Gi0/1",
          "reason": "documented_down", "detail": "srv-a · eth0"}],
    )
    assert len(calls) == 1
    et, summary, payload = calls[0]
    assert et == "cable.mismatch"
    assert payload["device_id"] == 7
    assert payload["items"][0]["reason"] == "documented_down"


async def test_raised_deltas_drive_silent_recovery(
    client, session, key, monkeypatch
):
    """Flag raise → clear → re-raise cycle: raised counts only on the
    transition, so emit-once per NEW finding holds end to end."""
    d, dev = await _switch(client, session, key)
    i1 = await _iface(client, d["id"], name="Gi0/1")
    _, p1 = await _peer_with_mac(client)
    await _cable(client, i1["id"], p1["id"])

    _mock_poll(monkeypatch, ifs=[_ifrow(1, "Gi0/1", oper="down")])
    r1 = await snmp_svc.poll_device(session, dev)
    await _commit_fresh(session)
    assert r1["cable_flags_raised"] == 1 and r1["cable_flags_cleared"] == 0

    r2 = await snmp_svc.poll_device(session, dev)  # still down
    await _commit_fresh(session)
    assert r2["cable_flags_raised"] == 0 and r2["cable_flags_cleared"] == 0

    _mock_poll(monkeypatch, ifs=[_ifrow(1, "Gi0/1", oper="up")])
    r3 = await snmp_svc.poll_device(session, dev)
    await _commit_fresh(session)
    assert r3["cable_flags_raised"] == 0 and r3["cable_flags_cleared"] == 1
