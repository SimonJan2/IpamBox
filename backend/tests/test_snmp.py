"""V8 SNMP enrichment — write-only creds, IF-MIB upsert, bridge-MAC links,
manual-data protection, the bounded poll lane, and the global kill switch.

No live SNMP here: pysnmp is mocked at the module boundary (``_get`` /
``_walk`` for parsing, ``test_device``/``walk_*`` for the poll pipeline).
"""
import json
from datetime import datetime, timedelta, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy import func, select

from app.core.config import get_settings
from app.core.security import hash_password
from app.models.cabling import DeviceInterface
from app.models.change_log import ChangeLog
from app.models.device import Device
from app.models.ip_address import IPAddress
from app.models.user import User, UserRole
from app.services import runtime_settings
from app.services import snmp as snmp_svc
from app.services.secrets import decrypt_str

PASSWORD = "snmp-test-pw1"


@pytest.fixture
def key(monkeypatch):
    """Provision a master key on the cached settings object."""
    s = get_settings()
    monkeypatch.setattr(s, "ipambox_secret_key", "snmp-test-key")
    monkeypatch.setattr(s, "ipambox_secret_key_file", "")
    return s


# --- helpers ------------------------------------------------------------------


async def _device(client: AsyncClient, **kw) -> dict:
    r = await client.post("/api/v1/devices", json={"name": "sw1", **kw})
    assert r.status_code == 201, r.text
    return r.json()


async def _prefix(client: AsyncClient, cidr: str = "10.80.0.0/24") -> int:
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
    """PATCH the device SNMP-ready: v2c + community, enabled."""
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


def _down(error="requestTimedOut"):
    return {"up": False, "sys_name": None, "sys_descr": None, "error": error}


def _mock_poll(monkeypatch, *, test=None, ifs=(), bridge=None, lldp=None):
    """Point every network primitive at canned data."""
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


# --- credential handling --------------------------------------------------------


async def test_cred_write_encrypts_and_never_serializes(client, session, key):
    d = await _device(client)
    r = await _enable(client, d["id"])
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["snmp_enabled"] is True
    assert body["snmp_cred_set"] is True
    # the credential and its blob never touch a response
    assert "snmp_cred" not in body
    assert "snmp_cred_enc" not in body
    assert "public" not in r.text

    row = await _orm_device(session, d["id"])
    assert row.snmp_cred_enc.startswith("v1:")
    assert json.loads(decrypt_str(row.snmp_cred_enc)) == {
        "community": "public"
    }
    # list + detail both carry only the *_set flag
    detail = (await client.get(f"/api/v1/devices/{d['id']}")).json()
    listing = (
        await client.get("/api/v1/devices", params={"q": "sw1"})
    ).json()["items"][0]
    for b in (detail, listing):
        assert b["snmp_cred_set"] is True
        assert "snmp_cred_enc" not in b and "snmp_cred" not in b


async def test_cred_rotation_and_clear(client, session, key):
    d = await _device(client)
    await _enable(client, d["id"])
    row = await _orm_device(session, d["id"])
    blob1 = row.snmp_cred_enc

    r = await client.patch(
        f"/api/v1/devices/{d['id']}",
        json={"snmp_cred": {"community": "rotated"}},
    )
    assert r.status_code == 200
    await session.refresh(row)
    assert row.snmp_cred_enc != blob1
    assert json.loads(decrypt_str(row.snmp_cred_enc)) == {
        "community": "rotated"
    }

    # clearing the credential while enabled is refused — disable first
    r = await client.patch(
        f"/api/v1/devices/{d['id']}", json={"snmp_cred": None}
    )
    assert r.status_code == 422
    await client.patch(
        f"/api/v1/devices/{d['id']}", json={"snmp_enabled": False}
    )
    r = await client.patch(
        f"/api/v1/devices/{d['id']}", json={"snmp_cred": None}
    )
    assert r.status_code == 200
    assert r.json()["snmp_cred_set"] is False
    await session.refresh(row)
    assert row.snmp_cred_enc is None


async def test_enable_requires_version_and_cred(client, key):
    d = await _device(client)
    r = await client.patch(
        f"/api/v1/devices/{d['id']}", json={"snmp_enabled": True}
    )
    assert r.status_code == 422  # no version, no cred
    r = await client.patch(
        f"/api/v1/devices/{d['id']}",
        json={"snmp_enabled": True, "snmp_version": "v2c"},
    )
    assert r.status_code == 422  # still no cred
    # cred shape must match the version
    r = await client.patch(
        f"/api/v1/devices/{d['id']}",
        json={
            "snmp_enabled": True,
            "snmp_version": "v3",
            "snmp_cred": {"community": "x"},
        },
    )
    assert r.status_code == 422  # v3 needs user
    r = await client.patch(
        f"/api/v1/devices/{d['id']}",
        json={
            "snmp_enabled": True,
            "snmp_version": "v3",
            "snmp_cred": {"user": "monitor", "auth_key": "k" * 8},
        },
    )
    assert r.status_code == 200
    # disable is always allowed and keeps the cred stored
    r = await client.patch(
        f"/api/v1/devices/{d['id']}", json={"snmp_enabled": False}
    )
    assert r.status_code == 200
    assert r.json()["snmp_cred_set"] is True


async def test_v3_cred_roundtrip(client, session, key):
    d = await _device(client)
    r = await _enable(
        client,
        d["id"],
        snmp_version="v3",
        snmp_cred={
            "user": "monitor",
            "auth_key": "authpass1",
            "priv_key": "privpass1",
            "auth_proto": "sha256",
            "priv_proto": "aes256",
        },
    )
    assert r.status_code == 200, r.text
    row = await _orm_device(session, d["id"])
    assert json.loads(decrypt_str(row.snmp_cred_enc)) == {
        "user": "monitor",
        "auth_key": "authpass1",
        "priv_key": "privpass1",
        "auth_proto": "sha256",
        "priv_proto": "aes256",
    }


async def test_v3_context_field_roundtrips_and_reaches_transport(key):
    """`context` is stored in the cred blob and feeds ContextData on v3 —
    agents that scope data behind a named context (snmpsim does) drop
    empty-context requests entirely."""
    from dataclasses import replace

    from app.services.secrets import encrypt_str

    dev = Device(
        name="ctx-dev",
        snmp_version="v3",
        snmp_port=161,
        snmp_cred_enc=encrypt_str(
            json.dumps({"user": "u", "context": "cust-ctx"})
        ),
    )
    t = snmp_svc._target(dev, "10.0.0.9", timeout=1.0)
    ctx = snmp_svc._context(t)
    assert str(ctx.contextName) == "cust-ctx"
    # a VLAN pass overrides it; no cred context -> empty
    t_vlan = replace(t, vlan=10)
    assert str(snmp_svc._context(t_vlan).contextName) == "vlan-10"
    dev.snmp_cred_enc = encrypt_str(json.dumps({"user": "u"}))
    t2 = snmp_svc._target(dev, "10.0.0.9", timeout=1.0)
    assert str(snmp_svc._context(t2).contextName) == ""


async def test_encrypted_blob_roundtrips_through_backup_text(
    client, session, key
):
    """The *_enc blob is opaque text — a dump/restore cycle (or a row copy)
    keeps it decryptable under the same master key."""
    d = await _device(client)
    await _enable(client, d["id"])
    row = await _orm_device(session, d["id"])
    blob = row.snmp_cred_enc
    # restore == the same blob value lands on a row again and opens
    clone = Device(name="restored", snmp_cred_enc=blob)
    session.add(clone)
    await session.commit()
    assert decrypt_str(clone.snmp_cred_enc) == '{"community": "public"}'


# --- API endpoints ----------------------------------------------------------------


async def test_snmp_test_endpoint(client, session, key, monkeypatch):
    d = await _device(client)
    await _enable(client, d["id"])
    pid = await _prefix(client)
    await _ip(client, pid, "10.80.0.5", device_id=d["id"])

    async def _test(dev, host, *, timeout):
        assert host == "10.80.0.5"
        return _up("sw-core-1", "FakeOS Switch 1.0")

    monkeypatch.setattr(snmp_svc, "test_device", _test)
    r = await client.post(f"/api/v1/devices/{d['id']}/snmp/test")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body == {
        "up": True,
        "sys_name": "sw-core-1",
        "sys_descr": "FakeOS Switch 1.0",
        "error": None,
    }


async def test_snmp_test_no_ip_is_data_not_500(client, key):
    d = await _device(client)
    await _enable(client, d["id"])
    r = await client.post(f"/api/v1/devices/{d['id']}/snmp/test")
    assert r.status_code == 200
    body = r.json()
    assert body["up"] is False
    assert "no linked IP" in body["error"]


async def test_snmp_poll_endpoint(client, session, key, monkeypatch):
    d = await _device(client)
    await _enable(client, d["id"])
    pid = await _prefix(client)
    await _ip(client, pid, "10.80.0.5", device_id=d["id"])
    _mock_poll(
        monkeypatch,
        ifs=[{"if_index": 1, "name": "Gi0/1", "oper": "up",
              "admin": "up", "speed_mbps": 1000, "mac": None}],
    )
    r = await client.post(f"/api/v1/devices/{d['id']}/snmp/poll")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["up"] is True
    assert body["interfaces_created"] == 1
    ifaces = (
        await client.get(f"/api/v1/devices/{d['id']}/interfaces")
    ).json()
    assert ifaces[0]["source"] == "snmp"
    assert ifaces[0]["oper_status"] == "up"
    assert ifaces[0]["if_index"] == 1
    assert ifaces[0]["snmp_seen_at"] is not None


# --- IF-MIB parsing (mocked at _walk) -------------------------------------------


# canned varbind rows for one 2-port switch: ifIndex 1 up/10G, 2 down/1G
IF_TABLE = {
    snmp_svc.OID_IF_NAME: [
        (f"{snmp_svc.OID_IF_NAME}.1", "Gi1/0/1"),
        (f"{snmp_svc.OID_IF_NAME}.2", "Gi1/0/2"),
    ],
    snmp_svc.OID_IF_DESCR: [
        (f"{snmp_svc.OID_IF_DESCR}.1", "GigabitEthernet1/0/1"),
        (f"{snmp_svc.OID_IF_DESCR}.2", "GigabitEthernet1/0/2"),
    ],
    snmp_svc.OID_IF_OPER: [
        (f"{snmp_svc.OID_IF_OPER}.1", 1),
        (f"{snmp_svc.OID_IF_OPER}.2", 2),
    ],
    snmp_svc.OID_IF_ADMIN: [
        (f"{snmp_svc.OID_IF_ADMIN}.1", 1),
        (f"{snmp_svc.OID_IF_ADMIN}.2", 2),
    ],
    snmp_svc.OID_IF_SPEED: [
        (f"{snmp_svc.OID_IF_SPEED}.1", 4_294_967_295),  # saturated
        (f"{snmp_svc.OID_IF_SPEED}.2", 1_000_000_000),
    ],
    snmp_svc.OID_IF_HSPEED: [
        (f"{snmp_svc.OID_IF_HSPEED}.1", 10_000),
        # no ifHighSpeed row for if2 — must fall back to ifSpeed
    ],
    snmp_svc.OID_IF_PHYS: [
        (f"{snmp_svc.OID_IF_PHYS}.1", "aabbccddee01"),
        (f"{snmp_svc.OID_IF_PHYS}.2", ""),
    ],
}


async def test_walk_if_mib_parses_columns(session, key, monkeypatch):
    async def _walk(t, prefix):
        return list(IF_TABLE.get(prefix, []))

    monkeypatch.setattr(snmp_svc, "_walk", _walk)
    d = Device(name="sw", snmp_version="v2c",
               snmp_cred_enc="unused")
    session.add(d)
    await session.commit()
    # bypass _cred — monkeypatch the target builder so the fake blob
    # doesn't need to decrypt
    monkeypatch.setattr(
        snmp_svc, "_target",
        lambda dev, host, *, timeout: snmp_svc.SnmpTarget(
            host=host, port=161, version="v2c", cred={"community": "x"}
        ),
    )
    rows = await snmp_svc.walk_if_mib(d, "10.80.0.5")
    by_idx = {r["if_index"]: r for r in rows}
    assert set(by_idx) == {1, 2}
    p1, p2 = by_idx[1], by_idx[2]
    assert p1["name"] == "Gi1/0/1"  # ifName wins over ifDescr
    assert p1["oper"] == "up" and p1["admin"] == "up"
    assert p1["speed_mbps"] == 10_000  # ifHighSpeed (Mbps)
    assert p1["mac"] == "AA:BB:CC:DD:EE:01"
    assert p2["oper"] == "down" and p2["admin"] == "down"
    assert p2["speed_mbps"] == 1000  # ifSpeed bps -> Mbps fallback
    assert p2["mac"] is None  # empty ifPhysAddress isn't a MAC


async def test_bridge_macs_parse_and_vlan_passes(session, key, monkeypatch):
    """dot1d FDB + basePort→ifIndex map, plus a per-VLAN community pass."""
    calls: list[str] = []

    async def _walk(t, prefix):
        calls.append(prefix if t.vlan is None else f"{prefix}@v{t.vlan}")
        if prefix == snmp_svc.OID_DOT1D_BASE_IF:
            return [(f"{prefix}.7", 101)]  # basePort 7 -> ifIndex 101
        if prefix == snmp_svc.OID_DOT1D_FDB_PORT and t.vlan is None:
            # index = the learned MAC's 6 arcs
            return [(f"{prefix}.170.187.204.238.0.9", 7)]
        if prefix == snmp_svc.OID_DOT1Q_VLAN_NAME:
            return [(f"{prefix}.10", "users")]
        if prefix == snmp_svc.OID_DOT1D_FDB_PORT and t.vlan == 10:
            return [(f"{prefix}.170.187.204.238.0.10", 7)]
        return []

    monkeypatch.setattr(snmp_svc, "_walk", _walk)
    monkeypatch.setattr(
        snmp_svc, "_target",
        lambda dev, host, *, timeout: snmp_svc.SnmpTarget(
            host=host, port=161, version="v2c", cred={"community": "x"}
        ),
    )
    d = Device(name="sw", snmp_version="v2c", snmp_cred_enc="unused")
    session.add(d)
    await session.commit()
    out = await snmp_svc.walk_bridge_macs(d, "10.80.0.5")
    assert out == {
        101: ["AA:BB:CC:EE:00:09", "AA:BB:CC:EE:00:0A"],
    }
    assert any(c.endswith("@v10") for c in calls)


# --- the enrichment poll --------------------------------------------------------


def _ifrow(idx, name, oper="up", admin="up", speed=1000, mac=None):
    return {
        "if_index": idx,
        "name": name,
        "oper": oper,
        "admin": admin,
        "speed_mbps": speed,
        "mac": mac,
    }


async def test_poll_creates_snmp_interfaces(
    client, session, key, monkeypatch
):
    d = await _device(client)
    await _enable(client, d["id"])
    pid = await _prefix(client)
    await _ip(client, pid, "10.80.0.5", device_id=d["id"])
    _mock_poll(
        monkeypatch,
        ifs=[_ifrow(1, "Gi0/1", "up", "up", 1000, "AA:BB:CC:DD:EE:01"),
             _ifrow(2, "Gi0/2", "down", "up", 10000)],
    )
    dev = await _orm_device(session, d["id"])
    res = await snmp_svc.poll_device(session, dev)
    await session.commit()
    assert res["up"] is True
    assert res["interfaces_seen"] == 2
    assert res["interfaces_created"] == 2

    ifaces = (
        (
            await session.execute(
                select(DeviceInterface).where(
                    DeviceInterface.device_id == d["id"]
                )
            )
        )
        .scalars()
        .all()
    )
    by_idx = {i.if_index: i for i in ifaces}
    assert set(by_idx) == {1, 2}
    assert all(i.source == "snmp" for i in ifaces)
    assert by_idx[1].oper_status == "up"
    assert by_idx[2].oper_status == "down"
    assert by_idx[2].speed_mbps == 10000
    assert by_idx[1].mac_address == "AA:BB:CC:DD:EE:01"
    assert all(i.snmp_seen_at is not None for i in ifaces)
    # device stamps
    await session.refresh(dev)
    assert dev.snmp_sys_name == "sw-core-1"
    assert dev.snmp_last_ok_at is not None
    assert dev.snmp_last_error is None


async def test_poll_updates_observed_state_no_churn(
    client, session, key, monkeypatch
):
    d = await _device(client)
    await _enable(client, d["id"])
    pid = await _prefix(client)
    await _ip(client, pid, "10.80.0.5", device_id=d["id"])
    _mock_poll(monkeypatch, ifs=[_ifrow(1, "Gi0/1")])
    dev = await _orm_device(session, d["id"])
    await snmp_svc.poll_device(session, dev)
    await session.commit()

    # second poll: oper flips + speed renegotiates — bulk update path
    _mock_poll(
        monkeypatch,
        ifs=[_ifrow(1, "Gi0/1", "down", "up", 100)],
    )
    res = await snmp_svc.poll_device(session, dev)
    await session.commit()
    assert res["interfaces_created"] == 0
    assert res["interfaces_updated"] == 1
    i = (
        await session.execute(
            select(DeviceInterface).where(
                DeviceInterface.device_id == d["id"]
            )
        )
    ).scalar_one()
    assert i.oper_status == "down" and i.speed_mbps == 100
    # observed churn must not write changelog update entries
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
    assert logs == []


async def test_manual_interface_protected_but_observed(
    client, session, key, monkeypatch
):
    d = await _device(client)
    await _enable(client, d["id"])
    pid = await _prefix(client)
    await _ip(client, pid, "10.80.0.5", device_id=d["id"])
    # a hand-drawn port with the device's reported name
    r = await client.post(
        f"/api/v1/devices/{d['id']}/interfaces",
        json={"name": "Gi0/1", "kind": "sfp"},
    )
    assert r.status_code == 201
    manual_id = r.json()["id"]

    _mock_poll(monkeypatch, ifs=[_ifrow(9, "Gi0/1", "up", "up", 25000)])
    dev = await _orm_device(session, d["id"])
    res = await snmp_svc.poll_device(session, dev)
    await session.commit()
    assert res["interfaces_created"] == 0  # name match — no duplicate
    i = await session.get(DeviceInterface, manual_id)
    assert i.source == "manual"  # ownership never moves
    assert i.kind.value == "sfp"  # documented kind preserved
    assert i.if_index == 9  # ...but observed state lands on it
    assert i.oper_status == "up"
    assert i.speed_mbps == 25000
    assert i.snmp_seen_at is not None


async def test_unpollable_ports_never_deleted(
    client, session, key, monkeypatch
):
    """A port the device stops reporting keeps its stale snmp_seen_at —
    nothing is deleted on a later poll."""
    d = await _device(client)
    await _enable(client, d["id"])
    pid = await _prefix(client)
    await _ip(client, pid, "10.80.0.5", device_id=d["id"])
    _mock_poll(
        monkeypatch, ifs=[_ifrow(1, "Gi0/1"), _ifrow(2, "Gi0/2")]
    )
    dev = await _orm_device(session, d["id"])
    await snmp_svc.poll_device(session, dev)
    await session.commit()

    _mock_poll(monkeypatch, ifs=[_ifrow(1, "Gi0/1")])
    await snmp_svc.poll_device(session, dev)
    await session.commit()
    ifaces = (
        (
            await session.execute(
                select(DeviceInterface).where(
                    DeviceInterface.device_id == d["id"]
                )
            )
        )
        .scalars()
        .all()
    )
    assert {i.if_index for i in ifaces} == {1, 2}  # Gi0/2 still there


# --- bridge-MAC -> connected_interface_id ---------------------------------------


async def test_bridge_mac_fills_connected_interface(
    client, session, key, monkeypatch
):
    d = await _device(client)
    await _enable(client, d["id"])
    pid = await _prefix(client)
    poll_ip = await _ip(client, pid, "10.80.0.5", device_id=d["id"])
    host_ip = await _ip(
        client, pid, "10.80.0.50", mac_address="aa:bb:cc:00:00:01"
    )
    _mock_poll(
        monkeypatch,
        ifs=[_ifrow(5, "Gi0/5")],
        bridge={5: ["AA:BB:CC:00:00:01"]},
    )
    dev = await _orm_device(session, d["id"])
    res = await snmp_svc.poll_device(session, dev)
    await session.commit()
    assert res["links_applied"] == 1
    assert res["macs_learned"] == 1

    ip = await session.get(IPAddress, host_ip["id"])
    iface = (
        await session.execute(
            select(DeviceInterface).where(
                DeviceInterface.device_id == d["id"]
            )
        )
    ).scalar_one()
    assert ip.connected_interface_id == iface.id
    # the write is ORM-level — changelog sees it
    log = (
        (
            await session.execute(
                select(ChangeLog).where(
                    ChangeLog.object_type == "IPAddress",
                    ChangeLog.object_id == ip.id,
                    ChangeLog.action == "update",
                )
            )
        )
        .scalars()
        .all()
    )
    assert any(
        c["field"] == "connected_interface_id"
        for e in log
        for c in e.changes
    )


async def test_manual_link_never_overwritten(
    client, session, key, monkeypatch
):
    d = await _device(client)
    await _enable(client, d["id"])
    pid = await _prefix(client)
    await _ip(client, pid, "10.80.0.5", device_id=d["id"])
    # a manually-modelled port the IP already links to
    r = await client.post(
        f"/api/v1/devices/{d['id']}/interfaces", json={"name": "uplink"}
    )
    manual_if = r.json()["id"]
    host_ip = await _ip(
        client,
        pid,
        "10.80.0.51",
        mac_address="aa:bb:cc:00:00:02",
        connected_interface_id=manual_if,
    )
    _mock_poll(
        monkeypatch,
        ifs=[_ifrow(7, "Gi0/7")],
        bridge={7: ["AA:BB:CC:00:00:02"]},  # bridge says: behind Gi0/7
    )
    dev = await _orm_device(session, d["id"])
    res = await snmp_svc.poll_device(session, dev)
    await session.commit()
    assert res["links_applied"] == 0
    assert res["links_skipped"] == 1
    ip = await session.get(IPAddress, host_ip["id"])
    assert ip.connected_interface_id == manual_if  # manual wins


async def test_scan_sourced_link_can_be_overwritten(
    client, session, key, monkeypatch
):
    """Lower-ranked sources lose to snmp under may_write."""
    d = await _device(client)
    await _enable(client, d["id"])
    pid = await _prefix(client)
    await _ip(client, pid, "10.80.0.5", device_id=d["id"])
    r = await client.post(
        f"/api/v1/devices/{d['id']}/interfaces", json={"name": "old-port"}
    )
    host_ip = await _ip(
        client,
        pid,
        "10.80.0.52",
        mac_address="aa:bb:cc:00:00:03",
        connected_interface_id=r.json()["id"],
    )
    # scan-sourced rows lose to snmp under may_write (rank 0 < 1)
    ip_row = await session.get(IPAddress, host_ip["id"])
    ip_row.source = "scan"
    await session.commit()
    _mock_poll(
        monkeypatch,
        ifs=[_ifrow(8, "Gi0/8")],
        bridge={8: ["AA:BB:CC:00:00:03"]},
    )
    dev = await _orm_device(session, d["id"])
    res = await snmp_svc.poll_device(session, dev)
    await session.commit()
    assert res["links_applied"] == 1
    ip = await session.get(IPAddress, host_ip["id"])
    new_if = (
        await session.execute(
            select(DeviceInterface).where(
                DeviceInterface.device_id == d["id"],
                DeviceInterface.if_index == 8,
            )
        )
    ).scalar_one()
    assert ip.connected_interface_id == new_if.id


async def test_fills_connected_toggle_off_writes_no_links(
    client, session, key, monkeypatch
):
    d = await _device(client)
    await _enable(client, d["id"])
    pid = await _prefix(client)
    await _ip(client, pid, "10.80.0.5", device_id=d["id"])
    host_ip = await _ip(
        client, pid, "10.80.0.53", mac_address="aa:bb:cc:00:00:04"
    )
    _mock_poll(
        monkeypatch,
        ifs=[_ifrow(3, "Gi0/3")],
        bridge={3: ["AA:BB:CC:00:00:04"]},
    )
    dev = await _orm_device(session, d["id"])
    res = await snmp_svc.poll_device(session, dev, fills_connected=False)
    await session.commit()
    assert res["links_applied"] == 0
    ip = await session.get(IPAddress, host_ip["id"])
    assert ip.connected_interface_id is None


# --- failure modes ----------------------------------------------------------------


async def test_unreachable_device_stamps_error_no_writes(
    client, session, key, monkeypatch
):
    d = await _device(client)
    await _enable(client, d["id"])
    pid = await _prefix(client)
    await _ip(client, pid, "10.80.0.5", device_id=d["id"])
    _mock_poll(monkeypatch, test=_down("requestTimedOut"))
    dev = await _orm_device(session, d["id"])
    res = await snmp_svc.poll_device(session, dev)
    await session.commit()
    assert res["up"] is False
    assert res["interfaces_created"] == 0
    await session.refresh(dev)
    assert dev.snmp_last_error == "requestTimedOut"
    assert dev.snmp_last_ok_at is None
    # no partial writes — zero interfaces
    n = await session.scalar(
        select(func.count()).select_from(DeviceInterface).where(
            DeviceInterface.device_id == d["id"]
        )
    )
    assert n == 0


async def test_error_text_never_contains_credentials(
    client, session, key, monkeypatch
):
    """An auth failure's error must not echo the community/password."""
    d = await _device(client)
    await _enable(client, d["id"])
    pid = await _prefix(client)
    await _ip(client, pid, "10.80.0.5", device_id=d["id"])
    _mock_poll(monkeypatch, test=_down("authorizationError"))
    dev = await _orm_device(session, d["id"])
    res = await snmp_svc.poll_device(session, dev)
    await session.commit()
    await session.refresh(dev)
    assert "public" not in (dev.snmp_last_error or "")
    assert "public" not in str(res)


# --- scheduling / the lane --------------------------------------------------------


async def test_due_device_ids_gates_on_enable_cred_and_interval(
    client, session, key
):
    now = datetime.now(timezone.utc)
    ready = await _device(client)
    await _enable(client, ready["id"])

    disabled = await _device(client)
    r = await client.patch(
        f"/api/v1/devices/{disabled['id']}",
        json={"snmp_version": "v2c", "snmp_cred": {"community": "x"}},
    )
    assert r.status_code == 200  # configured but not enabled

    fresh = await _device(client)  # polled a minute ago
    await _enable(client, fresh["id"])
    row = await _orm_device(session, fresh["id"])
    row.snmp_last_ok_at = now - timedelta(minutes=1)
    await session.commit()

    due = await snmp_svc.due_device_ids(session, now, 60)
    assert ready["id"] in due  # never polled -> due
    assert disabled["id"] not in due
    assert fresh["id"] not in due  # inside the interval


async def test_global_kill_switch_enqueues_nothing(
    client, session, sf, key, monkeypatch
):
    """snmp_enabled=0 -> snmp_tick is a no-op; nothing reaches the pool."""
    from app.worker import snmp as worker_snmp

    monkeypatch.setattr(worker_snmp, "SessionLocal", sf)
    enqueued = []

    class _Pool:
        async def enqueue_job(self, name, *a, **kw):
            enqueued.append((name, a, kw))

    async def _pool():
        return _Pool()

    monkeypatch.setattr(worker_snmp, "get_arq_pool", _pool)
    # default runtime value is off
    res = await worker_snmp.snmp_tick({})
    assert res == {"skipped": "snmp disabled"}
    assert enqueued == []


async def test_tick_batches_due_devices_into_one_job(
    client, session, sf, key, monkeypatch
):
    from app.worker import snmp as worker_snmp

    monkeypatch.setattr(worker_snmp, "SessionLocal", sf)
    d = await _device(client)
    await _enable(client, d["id"])
    await runtime_settings.patch(session, {"snmp_enabled": True})
    await session.commit()

    enqueued = []

    class _Pool:
        async def enqueue_job(self, name, ids, _job_id=None):
            enqueued.append((name, ids, _job_id))
            return object()

    async def _pool():
        return _Pool()

    monkeypatch.setattr(worker_snmp, "get_arq_pool", _pool)
    # attempt stamps persist in real redis across tests and RESTART
    # IDENTITY recycles device ids — clear them so pacing can't hide us
    from app.core.redis import get_redis

    r = get_redis()
    await r.delete(worker_snmp.ATTEMPT_HASH)
    res = await worker_snmp.snmp_tick({})
    assert res["due"] == 1
    assert enqueued == [
        ("run_snmp_poll", [d["id"]], worker_snmp.POLL_JOB_ID)
    ]


# --- RBAC -------------------------------------------------------------------------


async def _mkuser(session, username: str, role: UserRole) -> User:
    u = User(
        username=username, password_hash=hash_password(PASSWORD), role=role
    )
    session.add(u)
    await session.commit()
    return u


async def test_snmp_endpoints_require_write_perm(
    client, session, key, monkeypatch
):
    settings = get_settings()
    settings.ipambox_allow_insecure = False
    cookie_secure = settings.ipambox_cookie_secure
    settings.ipambox_cookie_secure = False
    try:
        await _mkuser(session, "snmp-admin", UserRole.ADMIN)
        await _mkuser(session, "snmp-viewer", UserRole.VIEWER)
        await _mkuser(session, "snmp-eng", UserRole.OPERATOR)
        r = await client.post(
            "/api/v1/auth/login",
            json={"username": "snmp-admin", "password": PASSWORD},
        )
        assert r.status_code == 200
        d = await _device(client)  # setup runs as admin
        await _enable(client, d["id"])

        r = await client.post(
            "/api/v1/auth/login",
            json={"username": "snmp-viewer", "password": PASSWORD},
        )
        assert r.status_code == 200
        assert (
            await client.post(f"/api/v1/devices/{d['id']}/snmp/test")
        ).status_code == 403
        assert (
            await client.post(f"/api/v1/devices/{d['id']}/snmp/poll")
        ).status_code == 403
        assert (
            await client.patch(
                f"/api/v1/devices/{d['id']}",
                json={"snmp_enabled": False},
            )
        ).status_code == 403

        r = await client.post(
            "/api/v1/auth/login",
            json={"username": "snmp-eng", "password": PASSWORD},
        )
        assert r.status_code == 200
        # operator holds DATA_WRITE — the poll path reaches the service
        _mock_poll(monkeypatch, test=_down("no-ip-here"))
        r = await client.post(f"/api/v1/devices/{d['id']}/snmp/poll")
        assert r.status_code == 200
    finally:
        settings.ipambox_allow_insecure = True
        settings.ipambox_cookie_secure = cookie_secure
        from app.core.redis import get_redis

        r = get_redis()
        for pattern in ("ipam:session:*", "ipam:loginfails:*", "ipam:lockout:*"):
            async for k in r.scan_iter(pattern):
                await r.delete(k)
        await r.aclose()
