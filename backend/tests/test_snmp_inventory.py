"""V8.3 SNMP inventory sync — a managed switch teaches IpamBox its
VLANs, SVI subnets, and ARP neighbors through preview -> review -> apply.

No live SNMP: pysnmp is mocked at the module boundary (``_walk`` for the
new walkers; ``test_device``/``walk_*`` for the sync pipeline), the same
convention test_snmp.py uses. Canned walks stand in for the switch.
"""
import ipaddress

import pytest
from httpx import AsyncClient
from sqlalchemy import func, select

from app.core.config import get_settings
from app.core.security import hash_password
from app.models.device import Device
from app.models.import_batch import ImportBatch, ImportBatchStatus
from app.models.ip_address import IPAddress, IPStatus
from app.models.prefix import Prefix
from app.models.user import User, UserRole
from app.models.vlan import VLAN
from app.models.vrf import VRF
from app.services import ranges, snmp_inventory
from app.services import snmp as snmp_svc

PASSWORD = "inv-test-pw1"


@pytest.fixture
def key(monkeypatch):
    """Provision a master key on the cached settings object."""
    s = get_settings()
    monkeypatch.setattr(s, "ipambox_secret_key", "inv-test-key")
    monkeypatch.setattr(s, "ipambox_secret_key_file", "")
    return s


@pytest.fixture
async def auth_on():
    """Turn auth on for a test, restore insecure mode after."""
    from app.core.redis import get_redis

    settings = get_settings()
    settings.ipambox_allow_insecure = False
    r = get_redis()
    try:
        yield
    finally:
        settings.ipambox_allow_insecure = True
        for pattern in ("ipam:session:*", "ipam:loginfails:*", "ipam:lockout:*"):
            async for k in r.scan_iter(pattern):
                await r.delete(k)
        await r.aclose()


# --- helpers (same shapes as test_snmp.py) ------------------------------------


async def _device(client: AsyncClient, **kw) -> dict:
    r = await client.post("/api/v1/devices", json={"name": "sw1", **kw})
    assert r.status_code == 201, r.text
    return r.json()


async def _vrf_id(client: AsyncClient) -> int:
    vrfs = (await client.get("/api/v1/vrfs")).json()
    return (vrfs["items"] if isinstance(vrfs, dict) else vrfs)[0]["id"]


async def _prefix(client: AsyncClient, cidr: str = "10.80.0.0/24") -> int:
    r = await client.post(
        "/api/v1/prefixes",
        json={"prefix": cidr, "vrf_id": await _vrf_id(client)},
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


def _up(name="sw-core-1", descr="FakeOS 1.0"):
    return {"up": True, "sys_name": name, "sys_descr": descr, "error": None}


def _mock_inv(monkeypatch, *, vlans=(), ip_ifs=(), arp=(), test=None):
    """Point every inventory primitive at canned data."""

    async def _test(dev, host, *, timeout):
        return test if test is not None else _up()

    async def _vlans(dev, host, *, timeout):
        return [dict(v) for v in vlans]

    async def _ipifs(dev, host, *, timeout):
        return [dict(v) for v in ip_ifs]

    async def _arp(dev, host, *, timeout):
        return [dict(v) for v in arp]

    monkeypatch.setattr(snmp_svc, "test_device", _test)
    monkeypatch.setattr(snmp_svc, "walk_vlans", _vlans)
    monkeypatch.setattr(snmp_svc, "walk_ip_interfaces", _ipifs)
    monkeypatch.setattr(snmp_svc, "walk_arp", _arp)


async def _switch(client, mgmt="10.80.0.5"):
    """An SNMP-ready device whose polled address is linked."""
    d = await _device(client)
    r = await _enable(client, d["id"])
    assert r.status_code == 200, r.text
    pid = await _prefix(client)
    await _ip(client, pid, mgmt, device_id=d["id"])
    return d, pid


def _rows(body, section=None, action=None):
    rows = body["rows"]
    if section is not None:
        rows = [r for r in rows if r["section"] == section]
    if action is not None:
        rows = [r for r in rows if r["action"] == action]
    return {r["key"]: r for r in rows}


# --- the new walkers (mocked at _walk) -------------------------------------------


def _target_patch(monkeypatch):
    monkeypatch.setattr(
        snmp_svc,
        "_target",
        lambda dev, host, *, timeout: snmp_svc.SnmpTarget(
            host=host, port=161, version="v2c", cred={"community": "x"}
        ),
    )


async def _bare_device(session) -> Device:
    d = Device(name="sw", snmp_version="v2c", snmp_cred_enc="unused")
    session.add(d)
    await session.commit()
    return d


async def test_walk_vlans_parses_names_and_ports(session, key, monkeypatch):
    """dot1qVlanStaticName + egress bitmaps (static and timeMark.vid
    current-table) resolved through dot1dBasePortIfIndex."""
    table = {
        snmp_svc.OID_DOT1Q_VLAN_NAME: [
            (f"{snmp_svc.OID_DOT1Q_VLAN_NAME}.1", "default"),
            (f"{snmp_svc.OID_DOT1Q_VLAN_NAME}.10", "users"),
            (f"{snmp_svc.OID_DOT1Q_VLAN_NAME}.20", "servers"),
        ],
        # static egress: index = vid, value = PortList bitmap
        snmp_svc.OID_DOT1Q_VLAN_EGRESS: [
            (f"{snmp_svc.OID_DOT1Q_VLAN_EGRESS}.10", b"\xC0"),  # ports 1,2
            (f"{snmp_svc.OID_DOT1Q_VLAN_EGRESS}.20", b"\x40"),  # port 2
        ],
        # current egress: index = timeMark.vid (last arc is the VID)
        snmp_svc.OID_DOT1Q_VLAN_CUR_EGRESS: [
            (f"{snmp_svc.OID_DOT1Q_VLAN_CUR_EGRESS}.0.30", b"\x80"),
        ],
        snmp_svc.OID_DOT1D_BASE_IF: [
            (f"{snmp_svc.OID_DOT1D_BASE_IF}.1", 101),
            (f"{snmp_svc.OID_DOT1D_BASE_IF}.2", 102),
        ],
    }

    async def _walk(t, prefix):
        return list(table.get(prefix, []))

    monkeypatch.setattr(snmp_svc, "_walk", _walk)
    _target_patch(monkeypatch)
    d = await _bare_device(session)
    out = await snmp_svc.walk_vlans(d, "10.80.0.5")
    by_vid = {v["vid"]: v for v in out}
    assert set(by_vid) == {1, 10, 20, 30}
    assert by_vid[10] == {"vid": 10, "name": "users", "ports": [101, 102]}
    assert by_vid[20]["ports"] == [102]
    assert by_vid[1]["ports"] == []
    # VLAN 30 exists only in the current table — still reported, unnamed
    assert by_vid[30] == {"vid": 30, "name": None, "ports": [101]}


async def test_walk_ip_interfaces_rfc4293(session, key, monkeypatch):
    """ipAddressTable + ipAddressPrefixTable containment, plus ifName /
    ifPhysAddress enrichment."""
    table = {
        # index = atype.len.addr — the InetAddress length arc is part of
        # the canonical encoding (RFC 4001): 1 = ipv4, 4 = octet count
        snmp_svc.OID_IP_ADDR_IFINDEX: [
            (f"{snmp_svc.OID_IP_ADDR_IFINDEX}.1.4.10.80.0.1", 501),
            (f"{snmp_svc.OID_IP_ADDR_IFINDEX}.1.4.192.168.9.1", 502),
        ],
        # index = ifIndex.atype.len.prefix
        snmp_svc.OID_IP_PREFIX_LEN: [
            (f"{snmp_svc.OID_IP_PREFIX_LEN}.501.1.4.10.80.0.0", 24),
            (f"{snmp_svc.OID_IP_PREFIX_LEN}.502.1.4.192.168.9.0", 30),
        ],
        snmp_svc.OID_IF_NAME: [
            (f"{snmp_svc.OID_IF_NAME}.501", "Vlan80"),
        ],
        snmp_svc.OID_IF_PHYS: [
            (f"{snmp_svc.OID_IF_PHYS}.501", "aabbcc000001"),
        ],
    }

    async def _walk(t, prefix):
        return list(table.get(prefix, []))

    monkeypatch.setattr(snmp_svc, "_walk", _walk)
    _target_patch(monkeypatch)
    d = await _bare_device(session)
    out = await snmp_svc.walk_ip_interfaces(d, "10.80.0.5")
    by_addr = {i["address"]: i for i in out}
    assert by_addr["10.80.0.1"] == {
        "if_index": 501, "address": "10.80.0.1", "prefix_len": 24,
        "name": "Vlan80", "mac": "AA:BB:CC:00:00:01",
    }
    assert by_addr["192.168.9.1"]["prefix_len"] == 30
    assert by_addr["192.168.9.1"]["name"] is None


async def test_walk_ip_interfaces_legacy_ipadent(session, key, monkeypatch):
    """v4-only agents: ipAddrTable's index IS the address; the mask is an
    IpAddress value, not a length."""

    async def _walk(t, prefix):
        if prefix == snmp_svc.OID_IP_ADDR_IFINDEX:
            return []  # no RFC 4293 table on this agent
        if prefix == snmp_svc.OID_IPADENT_IFINDEX:
            return [(f"{prefix}.10.80.0.1", 501)]
        if prefix == snmp_svc.OID_IPADENT_NETMASK:
            return [(f"{prefix}.10.80.0.1", "255.255.255.0")]
        return []

    monkeypatch.setattr(snmp_svc, "_walk", _walk)
    _target_patch(monkeypatch)
    d = await _bare_device(session)
    out = await snmp_svc.walk_ip_interfaces(d, "10.80.0.5")
    assert out == [{
        "if_index": 501, "address": "10.80.0.1", "prefix_len": 24,
        "name": None, "mac": None,
    }]


async def test_walk_arp_both_tables_dedupe(session, key, monkeypatch):
    """ipNetToPhysical (ifIndex.atype.addr index) and legacy
    ipNetToMedia (ifIndex.addr index) merge by address — the modern
    table wins."""

    async def _walk(t, prefix):
        if prefix == snmp_svc.OID_N2P_PHYS:
            # index = ifIndex.atype.len.addr (InetAddress len arc: 4)
            return [(f"{prefix}.501.1.4.10.80.0.22", "aabbcc112233")]
        if prefix == snmp_svc.OID_N2M_PHYS:
            return [
                (f"{prefix}.501.10.80.0.22", "0000000000aa"),  # loses
                (f"{prefix}.501.10.80.0.33", "112233445566"),
            ]
        return []

    monkeypatch.setattr(snmp_svc, "_walk", _walk)
    _target_patch(monkeypatch)
    d = await _bare_device(session)
    out = await snmp_svc.walk_arp(d, "10.80.0.5")
    assert out == [
        {"ip": "10.80.0.22", "mac": "AA:BB:CC:11:22:33", "if_index": 501},
        {"ip": "10.80.0.33", "mac": "11:22:33:44:55:66", "if_index": 501},
    ]


# --- preview classification -----------------------------------------------------


async def test_preview_classifies_rows(client, session, key, monkeypatch):
    """VLAN exists/conflict/create, subnet exists/create + gateway fill,
    no cross-VRF prefix matching, ARP create/exists/update/conflict."""
    d, pid = await _switch(client)
    vrf = await _vrf_id(client)

    # a second VRF with a prefix the switch also reports — must NOT match
    # across VRFs (overlap rules are per-VRF).
    vrf2 = VRF(name="cust")
    session.add(vrf2)
    await session.flush()
    session.add(Prefix(prefix="10.99.0.0/24", vrf_id=vrf2.id))
    await session.commit()

    # VLANs: 10 exists with the same name; 20 exists under another name
    # (conflict); 30 is new (create).
    await client.post("/api/v1/vlans", json={"vid": 10, "name": "users"})
    await client.post("/api/v1/vlans", json={"vid": 20, "name": "legacy"})

    # ARP neighbors against the existing /24 (.22 is NOT seeded — it
    # becomes the discovered-create row):
    await _ip(
        client, pid, "10.80.0.23", mac_address="AA:BB:CC:00:00:23"
    )                                                            # -> exists
    await _ip(client, pid, "10.80.0.24")                          # mac-less manual -> conflict
    await _ip(
        client, pid, "10.80.0.25", mac_address="AA:BB:CC:00:00:25"
    )                                                            # -> conflict
    # a scan-owned row SNMP may enrich (snmp outranks scan)
    scan_row = IPAddress(
        address="10.80.0.26",
        address_int=int(ipaddress.ip_address("10.80.0.26")),
        prefix_id=pid, vrf_id=vrf, status=IPStatus.ACTIVE, source="scan",
    )
    session.add(scan_row)
    await session.commit()

    _mock_inv(
        monkeypatch,
        vlans=[
            {"vid": 10, "name": "users", "ports": [1, 2]},
            {"vid": 20, "name": "servers", "ports": [3]},
            {"vid": 30, "name": "voice", "ports": [4]},
        ],
        ip_ifs=[
            {"if_index": 501, "address": "10.80.0.1",
             "prefix_len": 24, "name": "Vlan80",
             "mac": "AA:BB:CC:00:00:01"},
            {"if_index": 502, "address": "10.90.0.1",
             "prefix_len": 24, "name": "Vlan30", "mac": None},
            {"if_index": 503, "address": "10.99.0.1",
             "prefix_len": 24, "name": "Vlan99", "mac": None},
        ],
        arp=[
            {"ip": "10.80.0.22", "mac": "AA:BB:CC:11:22:33",
             "if_index": 501},
            {"ip": "10.80.0.23", "mac": "AA:BB:CC:00:00:23",
             "if_index": 501},
            {"ip": "10.80.0.24", "mac": "AA:BB:CC:00:00:24",
             "if_index": 501},
            {"ip": "10.80.0.25", "mac": "AA:BB:CC:FF:00:25",
             "if_index": 501},
            {"ip": "10.80.0.26", "mac": "AA:BB:CC:00:00:26",
             "if_index": 501},
            # the device's own SVI address must not become a neighbor
            {"ip": "10.80.0.1", "mac": "AA:BB:CC:00:00:01",
             "if_index": 501},
        ],
    )
    r = await client.post(
        f"/api/v1/devices/{d['id']}/snmp/inventory-preview",
        json={"vrf_id": vrf},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["up"] is True
    assert body["committed"] is False

    vlans = _rows(body, "vlans")
    assert vlans["vlan:10"]["action"] == "exists"
    assert vlans["vlan:20"]["action"] == "conflict"
    assert vlans["vlan:20"]["diff"]["name"] == ["legacy", "servers"]
    assert vlans["vlan:30"]["action"] == "create"

    subs = _rows(body, "subnets")
    # the stored /24 has no gateway — observed SVI fills it (update)
    assert subs["sub:10.80.0.0/24"]["action"] == "update"
    assert subs["sub:10.80.0.0/24"]["diff"]["gateway"] == [
        None, "10.80.0.1",
    ]
    # new SVI -> create; the Vlan30 ifName links it to VLAN 30's vid
    assert subs["sub:10.90.0.0/24"]["action"] == "create"
    # 10.99.0.0/24 exists only in 'cust' — in Global it's a create, not a
    # match: no cross-VRF leakage.
    assert subs["sub:10.99.0.0/24"]["action"] == "create"

    addrs = _rows(body, "addresses")
    assert addrs["addr:10.80.0.22"]["action"] == "create"
    assert addrs["addr:10.80.0.23"]["action"] == "exists"
    # manual-owned, MAC-less: SNMP can't fill it -> reported, not written
    assert addrs["addr:10.80.0.24"]["action"] == "conflict"
    # MAC contradiction: always reported, never written
    assert addrs["addr:10.80.0.25"]["action"] == "conflict"
    assert addrs["addr:10.80.0.25"]["diff"]["mac_address"] == [
        "AA:BB:CC:00:00:25", "AA:BB:CC:FF:00:25",
    ]
    # scan-owned row: snmp outranks -> MAC fill is an update
    assert addrs["addr:10.80.0.26"]["action"] == "update"
    # the SVI's own address never lands as a neighbor row
    assert "addr:10.80.0.1" not in addrs


async def test_preview_writes_nothing(client, session, key, monkeypatch):
    """Dry-run guarantee: preview touches no table."""
    d, _pid = await _switch(client)
    vrf = await _vrf_id(client)
    _mock_inv(
        monkeypatch,
        vlans=[{"vid": 30, "name": "voice", "ports": []}],
        ip_ifs=[{"if_index": 502, "address": "10.90.0.1",
                 "prefix_len": 24, "name": "Vlan30", "mac": None}],
        arp=[{"ip": "10.90.0.44", "mac": "AA:BB:CC:00:00:44",
              "if_index": 502}],
    )
    before = {
        t: await session.scalar(select(func.count()).select_from(m))
        for t, m in (
            ("vlans", VLAN), ("prefixes", Prefix),
            ("ips", IPAddress), ("batches", ImportBatch),
        )
    }
    r = await client.post(
        f"/api/v1/devices/{d['id']}/snmp/inventory-preview",
        json={"vrf_id": vrf},
    )
    assert r.status_code == 200, r.text
    await session.commit()  # flush whatever the request (didn't) stage
    after = {
        t: await session.scalar(select(func.count()).select_from(m))
        for t, m in (
            ("vlans", VLAN), ("prefixes", Prefix),
            ("ips", IPAddress), ("batches", ImportBatch),
        )
    }
    assert before == after


async def test_preview_unreachable_is_data(client, session, key, monkeypatch):
    d, _pid = await _switch(client)
    vrf = await _vrf_id(client)
    _mock_inv(
        monkeypatch,
        test={"up": False, "sys_name": None, "sys_descr": None,
              "error": "requestTimedOut"},
    )
    r = await client.post(
        f"/api/v1/devices/{d['id']}/snmp/inventory-preview",
        json={"vrf_id": vrf},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["up"] is False
    assert body["error"] == "requestTimedOut"
    assert body["rows"] == []


async def test_preview_no_ip_is_data(client, key):
    d = await _device(client)
    await _enable(client, d["id"])
    vrf = await _vrf_id(client)
    r = await client.post(
        f"/api/v1/devices/{d['id']}/snmp/inventory-preview",
        json={"vrf_id": vrf},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["up"] is False
    assert "no linked IP" in body["error"]


# --- apply -----------------------------------------------------------------------


def _clean_walk():
    """A switch state where everything applies cleanly — used by the
    apply / re-preview tests."""
    return {
        "vlans": [{"vid": 30, "name": "voice", "ports": [4]}],
        "ip_ifs": [
            {"if_index": 502, "address": "10.90.0.1",
             "prefix_len": 24, "name": "Vlan30", "mac": None},
        ],
        "arp": [
            {"ip": "10.90.0.44", "mac": "AA:BB:CC:00:00:44",
             "if_index": 502},
            {"ip": "10.80.0.22", "mac": "AA:BB:CC:11:22:33",
             "if_index": 501},
        ],
    }


async def test_apply_commits_in_one_batch(client, session, key, monkeypatch):
    d, pid = await _switch(client)
    vrf = await _vrf_id(client)
    _mock_inv(monkeypatch, **_clean_walk())

    r = await client.post(
        f"/api/v1/devices/{d['id']}/snmp/inventory-apply",
        json={"vrf_id": vrf},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["committed"] is True
    assert body["batch_id"] is not None
    # vlan:30 + subnet 10.90.0.0/24 + two ARP neighbors
    assert body["counts"]["create"] == 4
    # batch row: kind='snmp', committed, carries the walk snapshot
    batch = await session.get(ImportBatch, body["batch_id"])
    assert batch.kind == "snmp"
    assert batch.status == ImportBatchStatus.COMMITTED
    assert batch.committed_at is not None
    assert batch.stats["snapshot"]["vlans"][0]["vid"] == 30
    assert batch.filename.startswith("snmp:")

    # VLAN 30 landed
    vlan = (
        await session.execute(select(VLAN).where(VLAN.vid == 30))
    ).scalar_one()
    assert vlan.name == "voice"

    # the SVI subnet landed, linked to the new VLAN, gateway set
    p = next(
        p for p in (await session.execute(select(Prefix))).scalars()
        if str(p.prefix) == "10.90.0.0/24"
    )
    assert str(p.gateway) == "10.90.0.1"
    assert p.vlan_id == vlan.id
    assert p.vrf_id == vrf
    # the gateway's managed technical row was mirrored in
    gw_row = (
        await session.execute(
            select(IPAddress).where(
                IPAddress.prefix_id == p.id,
                IPAddress.address == ipaddress.ip_address("10.90.0.1"),
            )
        )
    ).scalar_one()
    assert gw_row.custom_fields.get("technical") == "gateway"

    # ARP neighbors discovered with provenance
    rows = (
        await session.execute(
            select(IPAddress).where(IPAddress.source == "snmp")
        )
    ).scalars().all()
    by_addr = {str(r.address): r for r in rows}
    assert set(by_addr) == {"10.80.0.22", "10.90.0.44"}
    for row in rows:
        assert row.status == IPStatus.DISCOVERED
        assert row.import_batch_id == batch.id
        assert row.mac_address is not None
        assert row.last_seen is not None
    assert by_addr["10.80.0.22"].prefix_id == pid


async def test_apply_then_preview_is_all_exists(
    client, session, key, monkeypatch
):
    """Re-running preview after a successful apply reports every row as
    exists — the sync converged the model onto the switch's truth."""
    d, _pid = await _switch(client)
    vrf = await _vrf_id(client)
    _mock_inv(monkeypatch, **_clean_walk())
    r = await client.post(
        f"/api/v1/devices/{d['id']}/snmp/inventory-apply",
        json={"vrf_id": vrf},
    )
    assert r.status_code == 200, r.text

    _mock_inv(monkeypatch, **_clean_walk())
    r = await client.post(
        f"/api/v1/devices/{d['id']}/snmp/inventory-preview",
        json={"vrf_id": vrf},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    bad = [
        r for r in body["rows"]
        if r["action"] not in ("exists", "skip")
    ]
    assert bad == [], f"unconverged rows: {bad}"


async def test_apply_selections_deselect_rows(
    client, session, key, monkeypatch
):
    """Unchecked sections apply nothing; a deselected subnet takes its
    ARP rows down with it (there's no prefix to hold them)."""
    d, _pid = await _switch(client)
    vrf = await _vrf_id(client)
    _mock_inv(monkeypatch, **_clean_walk())
    r = await client.post(
        f"/api/v1/devices/{d['id']}/snmp/inventory-apply",
        json={
            "vrf_id": vrf,
            "selections": {
                "vlans": ["vlan:30"],
                "subnets": [],          # unchecked — nothing applies
                "addresses": ["addr:10.80.0.22"],
            },
        },
    )
    assert r.status_code == 200, r.text
    body = r.json()
    rows = _rows(body)
    assert rows["vlan:30"]["action"] == "create"
    assert rows["sub:10.90.0.0/24"]["action"] == "skip"
    # 10.80.0.22 was selected and applies under the existing /24
    assert rows["addr:10.80.0.22"]["action"] == "create"
    # 10.90.0.44's subnet wasn't applied -> skip, not create
    assert rows["addr:10.90.0.44"]["action"] == "skip"

    assert await session.scalar(
        select(func.count()).select_from(VLAN)
    ) == 1
    assert await session.scalar(
        select(func.count()).select_from(Prefix)
    ) == 1  # only the seeded /24
    created = (
        await session.execute(
            select(IPAddress).where(IPAddress.source == "snmp")
        )
    ).scalars().all()
    assert [str(a.address) for a in created] == ["10.80.0.22"]


async def test_apply_rollback_on_mid_plan_failure(
    client, session, key, monkeypatch
):
    """A failure mid-plan rolls the whole transaction back — the VLAN
    created earlier in the same tx must not survive — and records a
    FAILED batch for the audit trail."""
    d, _pid = await _switch(client)
    vrf = await _vrf_id(client)
    _mock_inv(monkeypatch, **_clean_walk())

    async def _boom(session, prefix):
        raise RuntimeError("forced mid-plan failure")

    monkeypatch.setattr(ranges, "sync_technical_addresses", _boom)

    r = await client.post(
        f"/api/v1/devices/{d['id']}/snmp/inventory-apply",
        json={"vrf_id": vrf},
    )
    assert r.status_code == 500
    await session.rollback()  # clear the session's failed-tx state
    assert await session.scalar(
        select(func.count()).select_from(VLAN)
    ) == 0
    assert await session.scalar(
        select(func.count()).select_from(Prefix)
    ) == 1  # only the seeded /24
    assert await session.scalar(
        select(func.count(IPAddress.id)).where(IPAddress.source == "snmp")
    ) == 0
    batches = (
        (await session.execute(select(ImportBatch))).scalars().all()
    )
    assert len(batches) == 1
    assert batches[0].kind == "snmp"
    assert batches[0].status == ImportBatchStatus.FAILED
    assert "RuntimeError" in batches[0].stats["commit_error"]


async def test_manual_row_survives_conflicting_pull(
    client, session, key, monkeypatch
):
    """may_write is honored: a manual row whose MAC contradicts the ARP
    entry is reported as a conflict and left byte-identical."""
    d, pid = await _switch(client)
    vrf = await _vrf_id(client)
    await _ip(client, pid, "10.80.0.50", mac_address="AA:BB:CC:00:00:50")
    _mock_inv(
        monkeypatch,
        arp=[{"ip": "10.80.0.50", "mac": "11:22:33:44:55:66",
              "if_index": 501}],
    )
    r = await client.post(
        f"/api/v1/devices/{d['id']}/snmp/inventory-apply",
        json={"vrf_id": vrf},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    row = _rows(body)["addr:10.80.0.50"]
    assert row["action"] == "conflict"
    assert row["diff"]["mac_address"] == [
        "AA:BB:CC:00:00:50", "11:22:33:44:55:66",
    ]
    stored = (
        await session.execute(
            select(IPAddress).where(IPAddress.address == ipaddress.ip_address("10.80.0.50"))
        )
    ).scalar_one()
    assert stored.mac_address == "AA:BB:CC:00:00:50"  # unchanged
    assert stored.source == "manual"


async def test_apply_updates_prefix_gateway_when_empty(
    client, session, key, monkeypatch
):
    """An existing prefix with no gateway gets the device's own SVI
    address filled (update) — and the managed technical row appears."""
    d, pid = await _switch(client)
    vrf = await _vrf_id(client)
    _mock_inv(
        monkeypatch,
        ip_ifs=[{"if_index": 501, "address": "10.80.0.1",
                 "prefix_len": 24, "name": "Vlan80",
                 "mac": "AA:BB:CC:00:00:01"}],
    )
    r = await client.post(
        f"/api/v1/devices/{d['id']}/snmp/inventory-apply",
        json={"vrf_id": vrf},
    )
    assert r.status_code == 200, r.text
    row = _rows(body := r.json())["sub:10.80.0.0/24"]
    assert row["action"] == "update"
    p = await session.get(Prefix, pid)
    assert str(p.gateway) == "10.80.0.1"
    gw = (
        await session.execute(
            select(IPAddress).where(
                IPAddress.prefix_id == pid,
                IPAddress.address == ipaddress.ip_address("10.80.0.1"),
            )
        )
    ).scalar_one()
    assert gw.custom_fields.get("technical") == "gateway"


# --- RBAC ------------------------------------------------------------------------


async def test_inventory_requires_write_perm(
    client, session, key, auth_on, monkeypatch
):
    admin = User(
        username="inv-admin",
        password_hash=hash_password(PASSWORD),
        role=UserRole.ADMIN,
    )
    viewer = User(
        username="inv-viewer",
        password_hash=hash_password(PASSWORD),
        role=UserRole.VIEWER,
    )
    session.add_all([admin, viewer])
    await session.commit()

    # build the switch as admin first — device writes need DATA_WRITE
    r = await client.post(
        "/api/v1/auth/login",
        json={"username": "inv-admin", "password": PASSWORD},
    )
    assert r.status_code == 200, r.text
    d, _pid = await _switch(client)
    vrf = await _vrf_id(client)
    _mock_inv(monkeypatch, **_clean_walk())

    # viewer: both endpoints are DATA_WRITE — same as the import routes
    r = await client.post(
        "/api/v1/auth/login",
        json={"username": "inv-viewer", "password": PASSWORD},
    )
    assert r.status_code == 200
    r = await client.post(
        f"/api/v1/devices/{d['id']}/snmp/inventory-preview",
        json={"vrf_id": vrf},
    )
    assert r.status_code == 403
    r = await client.post(
        f"/api/v1/devices/{d['id']}/snmp/inventory-apply",
        json={"vrf_id": vrf},
    )
    assert r.status_code == 403

    # back to admin via the shared cookie jar
    r = await client.post(
        "/api/v1/auth/login",
        json={"username": "inv-admin", "password": PASSWORD},
    )
    assert r.status_code == 200
    r = await client.post(
        f"/api/v1/devices/{d['id']}/snmp/inventory-preview",
        json={"vrf_id": vrf},
    )
    assert r.status_code == 200, r.text
    assert r.json()["up"] is True


async def test_inventory_needs_a_real_vrf(client, session, key, monkeypatch):
    d, _pid = await _switch(client)
    _mock_inv(monkeypatch, **_clean_walk())
    r = await client.post(
        f"/api/v1/devices/{d['id']}/snmp/inventory-preview",
        json={"vrf_id": 99999},
    )
    assert r.status_code == 404
