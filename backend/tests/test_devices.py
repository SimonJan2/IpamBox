"""Device entity: /devices CRUD, multi-IP health rollup, unrack semantics,
rack-delete survival, RBAC, changelog, and the 0022 data migration."""

import os
import subprocess

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.redis import get_redis
from app.core.security import hash_password
from app.models.ip_address import IPAddress, IPStatus
from app.models.user import User, UserRole
from app.services.devices import device_health

PASSWORD = "device-test-pw1"


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


async def _rack(client: AsyncClient, **kw) -> dict:
    body = {"name": "R1", "height_u": 12, "width": 19, **kw}
    r = await client.post("/api/v1/racks", json=body)
    assert r.status_code == 201, r.text
    return r.json()


async def _device(client: AsyncClient, **kw) -> dict:
    body = {"name": "srv", **kw}
    r = await client.post("/api/v1/devices", json=body)
    assert r.status_code == 201, r.text
    return r.json()


async def _racked(client: AsyncClient, rack_id: int, **kw) -> dict:
    body = {"name": "srv", "u_position": 1, "u_height": 1, "face": "front", **kw}
    r = await client.post(f"/api/v1/racks/{rack_id}/devices", json=body)
    assert r.status_code == 201, r.text
    return r.json()


async def _prefix(client: AsyncClient, cidr: str = "10.50.0.0/24") -> int:
    vrfs = (await client.get("/api/v1/vrfs")).json()
    vrf = (vrfs["items"] if isinstance(vrfs, dict) else vrfs)[0]
    r = await client.post(
        "/api/v1/prefixes", json={"prefix": cidr, "vrf_id": vrf["id"]}
    )
    assert r.status_code == 201, r.text
    return r.json()["id"]


async def _ip(
    client: AsyncClient, prefix_id: int, addr: str, **kw
) -> dict:
    r = await client.post(
        "/api/v1/addresses", json={"address": addr, "prefix_id": prefix_id, **kw}
    )
    assert r.status_code == 201, r.text
    return r.json()


# --------------------------------------------------------------------- CRUD


async def test_device_crud_unracked(client: AsyncClient):
    d = await _device(
        client,
        name="srv-1",
        manufacturer="Dell",
        model="R650",
        serial_number="SN-1",
        watts=400,
    )
    assert d["rack_id"] is None and d["u_position"] is None
    assert d["health"] is None and d["ips"] == []

    got = (await client.get(f"/api/v1/devices/{d['id']}")).json()
    assert got["name"] == "srv-1" and got["serial_number"] == "SN-1"

    r = await client.patch(
        f"/api/v1/devices/{d['id']}", json={"notes": "spare", "pinned": True}
    )
    assert r.status_code == 200 and r.json()["notes"] == "spare"

    # attribute patch on an unracked device is fine, placement keys are not
    r = await client.patch(
        f"/api/v1/devices/{d['id']}", json={"u_position": 5}
    )
    assert r.status_code == 422

    assert (await client.delete(f"/api/v1/devices/{d['id']}")).status_code == 204
    assert (await client.get(f"/api/v1/devices/{d['id']}")).status_code == 404


async def test_device_list_q_and_filters(client: AsyncClient):
    rack = await _rack(client)
    await _device(client, name="alpha", model="R650")
    await _device(client, name="beta", serial_number="SN-BETA")
    await _racked(client, rack["id"], name="gamma", u_position=3)

    all_items = (await client.get("/api/v1/devices")).json()["items"]
    assert len(all_items) == 3

    unracked = (
        await client.get("/api/v1/devices", params={"unracked": True})
    ).json()["items"]
    assert {d["name"] for d in unracked} == {"alpha", "beta"}

    by_rack = (
        await client.get("/api/v1/devices", params={"rack_id": rack["id"]})
    ).json()["items"]
    assert [d["name"] for d in by_rack] == ["gamma"]

    by_q = (await client.get("/api/v1/devices", params={"q": "sn-beta"})).json()[
        "items"
    ]
    assert [d["name"] for d in by_q] == ["beta"]

    by_model = (await client.get("/api/v1/devices", params={"q": "r650"})).json()[
        "items"
    ]
    assert [d["name"] for d in by_model] == ["alpha"]


async def test_device_create_placed_directly(client: AsyncClient):
    rack = await _rack(client)
    d = await _device(
        client, name="placed", rack_id=rack["id"], u_position=5, u_height=2
    )
    assert d["rack_id"] == rack["id"] and d["u_position"] == 5
    detail = (await client.get(f"/api/v1/racks/{rack['id']}")).json()
    assert [x["name"] for x in detail["devices"]] == ["placed"]

    # racked create without u_position is rejected
    r = await client.post(
        "/api/v1/devices", json={"name": "bad", "rack_id": rack["id"]}
    )
    assert r.status_code == 422


async def test_device_patch_rehomes_between_racks(client: AsyncClient):
    r1 = await _rack(client, name="R1")
    r2 = await _rack(client, name="R2")
    d = await _racked(client, r1["id"], u_position=2)

    r = await client.patch(
        f"/api/v1/devices/{d['id']}", json={"rack_id": r2["id"], "u_position": 7}
    )
    assert r.status_code == 200, r.text
    assert r.json()["rack_id"] == r2["id"] and r.json()["u_position"] == 7

    # no longer in r1, now in r2
    assert (await client.get(f"/api/v1/racks/{r1['id']}")).json()["devices"] == []
    assert (await client.get(f"/api/v1/racks/{r2['id']}")).json()["devices"][0][
        "id"
    ] == d["id"]

    # collision on the target rack is still enforced
    other = await _racked(client, r2["id"], name="o2", u_position=9)
    r = await client.patch(
        f"/api/v1/devices/{other['id']}", json={"u_position": 7}
    )
    assert r.status_code == 409


# -------------------------------------------------------- multi-IP + health


async def test_multi_ip_health_rollup(client: AsyncClient):
    pid = await _prefix(client)
    d = await _device(client, name="db1")
    mgmt = await _ip(client, pid, "10.50.0.10", status="active", device_id=d["id"])
    svc = await _ip(client, pid, "10.50.0.11", status="dhcp", device_id=d["id"])
    ilo = await _ip(client, pid, "10.50.0.12", status="offline", device_id=d["id"])

    got = (await client.get(f"/api/v1/devices/{d['id']}")).json()
    assert got["ip_count"] == 3
    assert got["health"] == "offline"  # worst-of wins
    assert {i["id"] for i in got["ips"]} == {mgmt["id"], svc["id"], ilo["id"]}

    # the rack elevation dot follows the same rollup
    rack = await _rack(client)
    await client.patch(
        f"/api/v1/devices/{d['id']}",
        json={"rack_id": rack["id"], "u_position": 4},
    )
    rd = (await client.get(f"/api/v1/racks/{rack['id']}")).json()["devices"][0]
    assert rd["ip_status"] == "offline"
    assert rd["ip_address_id"] == ilo["id"]  # health IP = worst-status row

    # clearing the worst IP lifts the rollup to the next-worst
    await client.patch(f"/api/v1/addresses/{ilo['id']}", json={"status": "active"})
    rd = (await client.get(f"/api/v1/racks/{rack['id']}")).json()["devices"][0]
    assert rd["ip_status"] == "dhcp"


async def test_unrack_keeps_ip_links(client: AsyncClient):
    pid = await _prefix(client)
    rack = await _rack(client)
    d = await _racked(client, rack["id"], u_position=2)
    ip = await _ip(client, pid, "10.50.0.20", device_id=d["id"])

    assert (
        await client.delete(f"/api/v1/racks/{rack['id']}/devices/{d['id']}")
    ).status_code == 204
    got = (await client.get(f"/api/v1/devices/{d['id']}")).json()
    assert got["rack_id"] is None and got["u_position"] is None
    assert [i["id"] for i in got["ips"]] == [ip["id"]]

    addr = (await client.get(f"/api/v1/addresses/{ip['id']}")).json()
    assert addr["device_id"] == d["id"]
    assert addr["device_name"] == "srv"


async def test_rack_delete_unracks_devices(client: AsyncClient):
    """THE behavior change: rack_devices used to cascade; devices survive."""
    pid = await _prefix(client)
    rack = await _rack(client)
    d = await _racked(client, rack["id"], u_position=2)
    ip = await _ip(client, pid, "10.50.0.21", device_id=d["id"])

    assert (await client.delete(f"/api/v1/racks/{rack['id']}")).status_code == 204
    got = (await client.get(f"/api/v1/devices/{d['id']}")).json()
    assert got["rack_id"] is None and got["u_position"] is None
    assert [i["id"] for i in got["ips"]] == [ip["id"]]


async def test_device_delete_unlinks_ips(client: AsyncClient):
    pid = await _prefix(client)
    d = await _device(client)
    ip = await _ip(client, pid, "10.50.0.30", device_id=d["id"])

    assert (await client.delete(f"/api/v1/devices/{d['id']}")).status_code == 204
    addr = (await client.get(f"/api/v1/addresses/{ip['id']}")).json()
    assert addr["device_id"] is None


async def test_device_rack_route_link_replaces_ip_set(client: AsyncClient):
    """The rack form's single Linked IP keeps replace semantics — patching
    ip_address_id makes it the device's whole set."""
    pid = await _prefix(client)
    rack = await _rack(client)
    d = await _racked(client, rack["id"], u_position=2)
    a = await _ip(client, pid, "10.50.0.40")
    b = await _ip(client, pid, "10.50.0.41")

    r = await client.patch(
        f"/api/v1/racks/{rack['id']}/devices/{d['id']}",
        json={"ip_address_id": a["id"]},
    )
    assert r.status_code == 200 and r.json()["ip_address_id"] == a["id"]

    r = await client.patch(
        f"/api/v1/racks/{rack['id']}/devices/{d['id']}",
        json={"ip_address_id": b["id"]},
    )
    assert r.json()["ip_address_id"] == b["id"]
    got = (await client.get(f"/api/v1/devices/{d['id']}")).json()
    assert [i["id"] for i in got["ips"]] == [b["id"]]


def test_health_ranking_unit():
    class _Ip:
        def __init__(self, id, status):
            self.id, self.status = id, status

    ips = [
        _Ip(1, IPStatus.ACTIVE),
        _Ip(2, IPStatus.RESERVED),
        _Ip(3, IPStatus.DISCOVERED),
        _Ip(4, IPStatus.DHCP),
    ]
    assert device_health(ips) == IPStatus.DISCOVERED
    assert device_health(ips + [_Ip(5, IPStatus.OFFLINE)]) == IPStatus.OFFLINE
    assert device_health([]) is None


# --------------------------------------------------------- placement matrix


async def test_face_collision_matrix_on_devices(client: AsyncClient):
    """front/rear share U space; 'both' collides with everything."""
    rack = await _rack(client)
    await _racked(client, rack["id"], name="f1", u_position=4, face="front")

    # rear may share the same U
    ok = await client.post(
        f"/api/v1/racks/{rack['id']}/devices",
        json={"name": "r1", "u_position": 4, "face": "rear"},
    )
    assert ok.status_code == 201, ok.text

    # same face overlaps -> conflict
    bad = await client.post(
        f"/api/v1/racks/{rack['id']}/devices",
        json={"name": "f2", "u_position": 4, "face": "front"},
    )
    assert bad.status_code == 409

    # 'both' collides with either side
    both = await client.post(
        f"/api/v1/racks/{rack['id']}/devices",
        json={"name": "b1", "u_position": 4, "face": "both"},
    )
    assert both.status_code == 409


async def test_carrier_mount_via_devices_endpoint(client: AsyncClient):
    rack = await _rack(client)
    tray = await _racked(
        client, rack["id"], name="tray", u_position=6, slot_layout="halves"
    )
    r = await client.post(
        "/api/v1/devices",
        json={"name": "kid", "carrier_id": tray["id"], "slot": 1},
    )
    assert r.status_code == 201, r.text
    kid = r.json()
    assert kid["rack_id"] == rack["id"]
    assert kid["u_position"] == 6 and kid["face"] == "front"
    assert kid["carrier"]["id"] == tray["id"]

    # slot conflict with a sibling
    r = await client.post(
        "/api/v1/devices",
        json={"name": "kid2", "carrier_id": tray["id"], "slot": 1},
    )
    assert r.status_code == 409


# ---------------------------------------------------------------------- RBAC


async def test_devices_rbac(client: AsyncClient, session: AsyncSession, auth_on):
    await _mkuser(session, "v", UserRole.VIEWER)
    await _mkuser(session, "c", UserRole.CONTRIBUTOR)
    await _mkuser(session, "o", UserRole.OPERATOR)
    await _mkuser(session, "a", UserRole.ADMIN)

    await _login(client, "a")
    d = await _device(client, name="rbac-srv")

    # viewer: read only
    await _login(client, "v")
    assert (await client.get("/api/v1/devices")).status_code == 200
    assert (await client.get(f"/api/v1/devices/{d['id']}")).status_code == 200
    assert (await client.post("/api/v1/devices", json={"name": "x"})).status_code == 403
    assert (
        await client.patch(f"/api/v1/devices/{d['id']}", json={"name": "y"})
    ).status_code == 403
    assert (await client.delete(f"/api/v1/devices/{d['id']}")).status_code == 403

    # contributor: write but no delete
    await _login(client, "c")
    assert (
        await client.post("/api/v1/devices", json={"name": "by-contrib"})
    ).status_code == 201
    assert (
        await client.patch(f"/api/v1/devices/{d['id']}", json={"name": "renamed"})
    ).status_code == 200
    assert (await client.delete(f"/api/v1/devices/{d['id']}")).status_code == 403

    # operator: write + delete (data tier, same as other entity routers)
    await _login(client, "o")
    assert (await client.delete(f"/api/v1/devices/{d['id']}")).status_code == 204


# ----------------------------------------------------------------- changelog


async def test_device_changes_are_audited(client: AsyncClient):
    rack = await _rack(client)
    d = await _device(client, name="audited")
    await client.patch(
        f"/api/v1/devices/{d['id']}",
        json={"rack_id": rack["id"], "u_position": 3},
    )
    await client.patch(f"/api/v1/devices/{d['id']}", json={"rack_id": None})
    await client.delete(f"/api/v1/devices/{d['id']}")

    log = (
        await client.get("/api/v1/changelog", params={"object_type": "Device"})
    ).json()["items"]
    actions = [e["action"] for e in log]
    assert actions == ["delete", "update", "update", "create"]
    # the middle updates are the rack / unrack placement changes
    assert all(e["object_repr"] == "audited" for e in log)


async def test_ip_link_is_audited_on_address(client: AsyncClient):
    pid = await _prefix(client)
    d = await _device(client)
    ip = await _ip(client, pid, "10.50.0.60")
    await client.patch(
        f"/api/v1/addresses/{ip['id']}", json={"device_id": d["id"]}
    )
    log = (
        await client.get("/api/v1/changelog", params={"object_type": "IPAddress"})
    ).json()["items"]
    upd = [e for e in log if e["action"] == "update"]
    assert upd and "device_id" in str(upd[0]["changes"])


# -------------------------------------------------------------------- search


async def test_search_finds_devices(client: AsyncClient):
    await _device(client, name="qnap-iscsi-01", serial_number="QTSN77")
    body = (await client.get("/api/v1/search", params={"q": "qnap"})).json()
    assert body["devices"][0]["name"] == "qnap-iscsi-01"
    body = (await client.get("/api/v1/search", params={"q": "qtsn77"})).json()
    assert body["devices"][0]["serial_number"] == "QTSN77"


# ------------------------------------------------------------------ migration


def test_alembic_devices_data_migration():
    """0022 upgrade moves rack_devices -> devices preserving ids and IP
    links; downgrade rebuilds rack_devices with ip_address_id backfilled."""
    import asyncio

    import asyncpg

    from tests.conftest import TEST_DB_NAME, _base_dsn, _split_dsn, test_url

    scratch = f"{TEST_DB_NAME}_devices"

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

        # build the pre-0022 schema and seed real rack_devices
        alembic("upgrade", "0021_rack_groups")
        conn = await asyncpg.connect(
            url.replace("postgresql+asyncpg://", "postgresql://")
        )
        try:
            await conn.execute(
                """
                INSERT INTO racks (id, name, height_u, width)
                    VALUES (10, 'A-01', 42, 19);
                INSERT INTO prefixes (id, prefix, vrf_id)
                    SELECT 1, '10.60.0.0/24', id FROM vrfs LIMIT 1;
                INSERT INTO ip_addresses
                    (id, address, address_int, prefix_id, vrf_id, status)
                    SELECT 100, '10.60.0.5', 167772165, 1, id, 'active'
                    FROM vrfs LIMIT 1;
                INSERT INTO rack_devices
                    (id, rack_id, name, u_position, u_height, face,
                     ip_address_id, carrier_id, slot, slot_layout, watts)
                    VALUES
                    (50, 10, 'tray', 20, 1, 'front', NULL, NULL, NULL,
                     'halves', 50),
                    (51, 10, 'srv', 10, 2, 'front', 100, NULL, NULL, NULL, 400),
                    (52, 10, 'kid', 20, 1, 'front', NULL, 50, 0, NULL, 100);
                """
            )
        finally:
            await conn.close()

        alembic("upgrade", "head")
        rows = await fetch(
            "SELECT id, rack_id, name, u_position, carrier_id, slot, "
            "slot_layout, watts FROM devices ORDER BY id"
        )
        by_id = {r["id"]: dict(r) for r in rows}
        assert set(by_id) == {50, 51, 52}  # ids preserved
        assert by_id[52]["carrier_id"] == 50 and by_id[52]["slot"] == 0
        assert by_id[50]["slot_layout"] == "halves"
        linked = await fetch(
            "SELECT device_id FROM ip_addresses WHERE id = 100"
        )
        assert linked[0]["device_id"] == 51
        gone = await fetch(
            "SELECT count(*) AS n FROM information_schema.tables "
            "WHERE table_name='rack_devices'"
        )
        assert gone[0]["n"] == 0

        alembic("downgrade", "0021_rack_groups")
        rows = await fetch(
            "SELECT id, name, ip_address_id, carrier_id FROM rack_devices "
            "ORDER BY id"
        )
        by_id = {r["id"]: dict(r) for r in rows}
        assert set(by_id) == {50, 51, 52}
        assert by_id[51]["ip_address_id"] == 100
        assert by_id[52]["carrier_id"] == 50
        gone = await fetch(
            "SELECT count(*) AS n FROM information_schema.tables "
            "WHERE table_name='devices'"
        )
        assert gone[0]["n"] == 0

        # upgrade again cleanly for the next run
        alembic("upgrade", "head")
        conn = await asyncpg.connect(f"{root}/postgres{query}")
        try:
            await conn.execute(f'DROP DATABASE IF EXISTS "{scratch}"')
        finally:
            await conn.close()

    asyncio.run(_run())
