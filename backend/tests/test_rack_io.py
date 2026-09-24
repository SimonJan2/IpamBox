"""V5C: /racks export.csv + bundle export.xlsx + smart /racks/import.

A rack is a tree — group -> racks -> devices (-> carriers -> children ->
interfaces -> cables). The flat CSV exports the filtered rack list; the
xlsx bundle round-trips the whole tree between installs by name. Covers
filter parity, sheet order, matching, on_existing modes, replace_devices
(unrack never deletes), group_id override, placement conflicts, wiring,
dry-run/force semantics, Hebrew headers, RBAC, changelog.
"""

import io
import json

import openpyxl
import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.redis import get_redis
from app.core.security import hash_password
from app.models.user import User, UserRole
from app.services.rack_io import RACK_EXPORT_COLUMNS

PASSWORD = "io-test-pw1"


# ------------------------------------------------------------------ helpers


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


async def _site(client: AsyncClient, name="DC-1") -> dict:
    r = await client.post("/api/v1/sites", json={"name": name})
    assert r.status_code == 201, r.text
    return r.json()


async def _group(client: AsyncClient, name="Row A", **kw) -> dict:
    r = await client.post("/api/v1/rack-groups", json={"name": name, **kw})
    assert r.status_code == 201, r.text
    return r.json()


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


async def _iface(client: AsyncClient, device_id: int, name="eth0", **kw) -> dict:
    r = await client.post(
        f"/api/v1/devices/{device_id}/interfaces",
        json={"name": name, **kw},
    )
    assert r.status_code == 201, r.text
    return r.json()


async def _cable(client: AsyncClient, a_id: int, b_id: int, **kw) -> dict:
    r = await client.post(
        "/api/v1/cables",
        json={"a_interface_id": a_id, "b_interface_id": b_id, **kw},
    )
    assert r.status_code == 201, r.text
    return r.json()


def _csv(text: str) -> bytes:
    return text.encode("utf-8")


def _bundle(sheets: dict[str, tuple[list[str], list[list]]]) -> bytes:
    """{sheet_name: (headers, rows)} -> multi-sheet xlsx bytes."""
    wb = openpyxl.Workbook()
    first = True
    for name, (headers, rows) in sheets.items():
        ws = wb.active if first else wb.create_sheet()
        first = False
        ws.title = name
        ws.append(headers)
        for row in rows:
            ws.append(row)
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def _read_xlsx(payload: bytes) -> dict[str, list[list]]:
    wb = openpyxl.load_workbook(io.BytesIO(payload), read_only=True)
    return {
        ws.title: [list(r) for r in ws.iter_rows(values_only=True)]
        for ws in wb.worksheets
    }


async def _import(
    client: AsyncClient, payload: bytes, filename="racks.xlsx", **params
) -> dict:
    r = await client.post(
        "/api/v1/racks/import",
        content=payload,
        params={"filename": filename, **params},
    )
    assert r.status_code == 200, r.text
    return r.json()


def _by_sheet(resp: dict) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for r in resp["rows"]:
        out.setdefault(r["sheet"], []).append(r)
    return out


async def _wipe(session: AsyncSession) -> None:
    """The 'empty install' half of a round-trip. expunge drops the stale
    identity-map rows so recreated rows can reuse ids safely."""
    await session.execute(
        text(
            "TRUNCATE cables, device_interfaces, devices, racks, "
            "rack_groups, sites RESTART IDENTITY CASCADE"
        )
    )
    await session.commit()
    session.expunge_all()


# ------------------------------------------------------------------- export


async def test_racks_csv_column_order_and_filename(client: AsyncClient):
    site = await _site(client)
    group = await _group(client)
    rack = await _rack(
        client, name="R-EXP", site_id=site["id"], group_id=group["id"],
        room="101", description="d", notes="n",
    )
    await _racked(client, rack["id"], name="srv1", u_position=1, watts=100)

    r = await client.get("/api/v1/racks/export.csv")
    assert r.status_code == 200
    body = r.content
    assert body.startswith(b"\xef\xbb\xbf")
    lines = body.decode("utf-8-sig").splitlines()
    header = lines[0].split(",")
    assert header == RACK_EXPORT_COLUMNS
    rec = dict(zip(header, lines[1].split(",")))
    assert rec["name"] == "R-EXP"
    assert rec["site"] == "DC-1" and rec["group"] == "Row A"
    assert rec["group_position"] == "1"
    assert rec["device_count"] == "1" and rec["used_u"] == "1"
    assert rec["free_u"] == str(rack["height_u"] - 1)
    assert rec["power_w"] == "100"
    assert "racks.csv" in r.headers["content-disposition"]


async def test_racks_csv_filter_parity(client: AsyncClient):
    site = await _site(client)
    a = await _rack(client, name="alpha", site_id=site["id"], room="lab")
    await _rack(client, name="beta", room="dc")
    r3 = await _rack(client, name="gamma", room="dc")
    await _racked(client, r3["id"], name="srv", u_position=1)
    await _racked(client, r3["id"], name="srv2", u_position=2)

    for params in (
        {"q": "alp"},
        {"site_id": str(site["id"])},
        {"room": "dc"},
        {"occupancy": "empty"},
        {"occupancy": "partial"},
        {"min_free_u": str(r3["height_u"] - 1)},
        {"ungrouped": "true"},
    ):
        listed = (
            await client.get("/api/v1/racks", params=params)
        ).json()["items"]
        r = await client.get("/api/v1/racks/export.csv", params=params)
        assert "racks-filtered.csv" in r.headers["content-disposition"]
        got = [l.split(",")[0] for l in r.content.decode("utf-8-sig").splitlines()[1:]]
        assert got == [str(x["id"]) for x in listed]


async def test_bundle_sheet_order_and_contents(client: AsyncClient):
    site = await _site(client)
    group = await _group(client)
    rack = await _rack(client, name="R-B", site_id=site["id"], group_id=group["id"])
    await _rack(client, name="R-OTHER")  # ungrouped, no devices
    d1 = await _racked(client, rack["id"], name="sw1", u_position=1)
    d2 = await _racked(client, rack["id"], name="srv1", u_position=3)
    i1 = await _iface(client, d1["id"], "swp1")
    i2 = await _iface(client, d2["id"], "eth0")
    await _cable(client, i1["id"], i2["id"], kind="cat6", label="L1")

    r = await client.get("/api/v1/racks/export.xlsx")
    assert r.status_code == 200
    wb = _read_xlsx(r.content)
    assert list(wb) == ["groups", "racks", "devices", "interfaces", "cables"]
    assert [row[1] for row in wb["groups"][1:]] == ["Row A"]
    assert {row[1] for row in wb["racks"][1:]} == {"R-B", "R-OTHER"}
    dev_headers = wb["devices"][0]
    devs = {dict(zip(dev_headers, row))["name"] for row in wb["devices"][1:]}
    assert devs == {"sw1", "srv1"}
    iface_rows = {
        (row[0], row[1]) for row in wb["interfaces"][1:]
    }
    assert iface_rows == {("sw1", "swp1"), ("srv1", "eth0")}
    assert list(wb["cables"][0]) == [
        "a_device", "a_interface", "b_device", "b_interface",
        "kind", "color", "label", "length_m",
    ]
    assert wb["cables"][1][:4] == ["sw1", "swp1", "srv1", "eth0"]


async def test_bundle_filtered_view_scopes_set(client: AsyncClient):
    group = await _group(client)
    in_rack = await _rack(client, name="in", group_id=group["id"])
    await _rack(client, name="out")
    await _racked(client, in_rack["id"], name="kept", u_position=1)

    r = await client.get(
        "/api/v1/racks/export.xlsx", params={"group_id": group["id"]}
    )
    wb = _read_xlsx(r.content)
    assert [row[1] for row in wb["racks"][1:]] == ["in"]
    assert "racks-filtered.xlsx" in r.headers["content-disposition"]


async def test_group_export_member_set_and_single_rack(client: AsyncClient):
    group = await _group(client, name="Row X")
    r1 = await _rack(client, name="gx-1", group_id=group["id"],
                     group_position=1)
    r2 = await _rack(client, name="gx-2", group_id=group["id"],
                     group_position=2)
    await _rack(client, name="not-member")
    await _racked(client, r1["id"], name="d1", u_position=1)
    await _racked(client, r2["id"], name="d2", u_position=2)

    r = await client.get(f"/api/v1/rack-groups/{group['id']}/export.xlsx")
    assert r.status_code == 200
    assert "Row X.xlsx" in r.headers["content-disposition"]
    wb = _read_xlsx(r.content)
    assert [row[1] for row in wb["groups"][1:]] == ["Row X"]
    assert [row[1] for row in wb["racks"][1:]] == ["gx-1", "gx-2"]
    assert {row[1] for row in wb["devices"][1:]} == {"d1", "d2"}

    # single-rack bundle carries its group row
    r = await client.get(f"/api/v1/racks/{r1['id']}/export.xlsx")
    assert "gx-1.xlsx" in r.headers["content-disposition"]
    wb = _read_xlsx(r.content)
    assert [row[1] for row in wb["groups"][1:]] == ["Row X"]
    assert [row[1] for row in wb["racks"][1:]] == ["gx-1"]


async def test_empty_rack_exports_structure(client: AsyncClient):
    await _rack(client, name="empty-rack")
    r = await client.get("/api/v1/racks/export.xlsx")
    wb = _read_xlsx(r.content)
    assert list(wb) == ["groups", "racks", "devices"]
    assert [row[1] for row in wb["racks"][1:]] == ["empty-rack"]
    assert len(wb["devices"]) == 1  # header only — structure, not nothing


# ------------------------------------------------------------------- import


async def test_flat_racks_csv_import(client: AsyncClient):
    payload = _csv("name,site,room,height_u\nR-CSV,DC-1,lab,24\n")
    r = await _import(client, payload, "racks.csv")
    by = _by_sheet(r)
    assert by["racks"][0]["action"] == "create"
    assert r["counts"]["create"] >= 1
    # site named in the file is created too (empty-install contract)
    assert by["sites"][0]["action"] == "create"
    await _import(client, payload, "racks.csv", dry_run=False)
    racks = (await client.get("/api/v1/racks")).json()["items"]
    assert racks[0]["name"] == "R-CSV" and racks[0]["height_u"] == 24


async def test_roundtrip_group_bundle(client: AsyncClient, session: AsyncSession):
    """The contract: export a group -> empty install -> same tree."""
    site = await _site(client)
    group = await _group(client, name="Row X", site_id=site["id"])
    r1 = await _rack(client, name="gx-1", group_id=group["id"],
                     group_position=1, site_id=site["id"], height_u=12)
    r2 = await _rack(client, name="gx-2", group_id=group["id"],
                     group_position=2, site_id=site["id"], height_u=12)
    carrier = await _racked(
        client, r1["id"], name="tray", u_position=1, slot_layout="halves"
    )
    child = await _device(
        client, name="psu", carrier_id=carrier["id"], slot=0
    )
    d2 = await _racked(
        client, r2["id"], name="srv2", u_position=4, u_height=2, face="rear"
    )
    i1 = await _iface(client, child["id"], "mgmt")
    i2 = await _iface(client, d2["id"], "eth0")
    await _cable(client, i1["id"], i2["id"], kind="dac", label="uplink")

    payload = (
        await client.get(f"/api/v1/rack-groups/{group['id']}/export.xlsx")
    ).content
    await _wipe(session)

    # dry-run writes nothing
    r = await _import(client, payload)
    assert not r["committed"]
    assert (await client.get("/api/v1/racks")).json()["items"] == []

    r = await _import(client, payload, dry_run=False)
    assert r["committed"]
    assert r["counts"]["error"] == 0, r["rows"]

    groups = (await client.get("/api/v1/rack-groups")).json()
    assert [g["name"] for g in groups] == ["Row X"]
    detail = (
        await client.get(f"/api/v1/rack-groups/{groups[0]['id']}")
    ).json()
    assert [x["name"] for x in detail["racks"]] == ["gx-1", "gx-2"]
    devs = {d["name"]: d for x in detail["racks"] for d in x["devices"]}
    assert devs["tray"]["u_position"] == 1
    assert devs["tray"]["slot_layout"] == "halves"
    assert devs["psu"]["carrier_id"] == devs["tray"]["id"]
    assert devs["psu"]["slot"] == 0
    assert devs["srv2"]["u_position"] == 4 and devs["srv2"]["face"] == "rear"

    # wiring rebuilt by name
    srv2_id = devs["srv2"]["id"]
    ifaces = (
        await client.get(f"/api/v1/devices/{srv2_id}/interfaces")
    ).json()
    assert ifaces[0]["name"] == "eth0" and ifaces[0]["peer"] is not None

    # re-import over the same data = all skip
    r = await _import(client, payload)
    assert set(x["action"] for x in r["rows"]) <= {"skip"}


async def test_import_on_existing_modes(client: AsyncClient, session: AsyncSession):
    site = await _site(client)
    rack = await _rack(client, name="R-M", site_id=site["id"], room="old")
    await _racked(client, rack["id"], name="keep", u_position=1)
    payload = _bundle({
        "racks": (["name", "site", "room"], [["R-M", "DC-1", "new"]]),
        "devices": (
            ["name", "rack", "u_position", "face"],
            [["added", "R-M", 5, "front"]],
        ),
    })
    # skip: rack untouched, devices suppressed
    r = await _import(client, payload, on_existing="skip", dry_run=False)
    assert r["committed"]
    got = (await client.get(f"/api/v1/racks/{rack['id']}")).json()
    assert got["room"] == "old" and len(got["devices"]) == 1

    # merge: rack attrs stay, device lands in a free U
    r = await _import(client, payload, on_existing="merge", dry_run=False)
    assert r["committed"]
    got = (await client.get(f"/api/v1/racks/{rack['id']}")).json()
    assert got["room"] == "old"
    assert {d["name"] for d in got["devices"]} == {"keep", "added"}

    # update: rack patched + device rows update/create per V5B rules
    r = await _import(client, payload, on_existing="update", dry_run=False)
    assert r["committed"]
    got = (await client.get(f"/api/v1/racks/{rack['id']}")).json()
    assert got["room"] == "new"


async def test_replace_devices_unracks_never_deletes(
    client: AsyncClient, session: AsyncSession
):
    rack = await _rack(client, name="R-R", height_u=12)
    await _racked(client, rack["id"], name="old1", u_position=1)
    await _racked(client, rack["id"], name="old2", u_position=3)
    payload = _bundle({
        "racks": (["name"], [["R-R"]]),
        "devices": (
            ["name", "rack", "u_position"],
            [["new1", "R-R", 1]],
        ),
    })
    r = await _import(
        client, payload, on_existing="update", replace_devices=True,
        dry_run=False,
    )
    assert r["committed"]
    got = (await client.get(f"/api/v1/racks/{rack['id']}")).json()
    assert [d["name"] for d in got["devices"]] == ["new1"]
    # the unracked occupants SURVIVE as inventory
    devices = (await client.get("/api/v1/devices")).json()["items"]
    survivors = {d["name"]: d["rack_id"] for d in devices}
    assert survivors == {"old1": None, "old2": None, "new1": rack["id"]}


async def test_group_id_override(client: AsyncClient):
    target = await _group(client, name="Target")
    other = await _group(client, name="Other")
    payload = _bundle({
        "groups": (["name"], [["File Group"]]),
        "racks": (
            ["name", "group", "group_position"],
            [["ovr-1", "File Group", 1], ["ovr-2", "", ""]],
        ),
    })
    r = await _import(client, payload, group_id=target["id"], dry_run=False)
    assert r["committed"]
    detail = (
        await client.get(f"/api/v1/rack-groups/{target['id']}")
    ).json()
    assert [x["name"] for x in detail["racks"]] == ["ovr-1", "ovr-2"]
    # the file's own group row was still created, just not joined
    names = {g["name"] for g in (await client.get("/api/v1/rack-groups")).json()}
    assert names == {"Target", "Other", "File Group"}


async def test_import_placement_conflict_reported_not_forced(
    client: AsyncClient,
):
    rack = await _rack(client, name="R-C", height_u=12)
    await _racked(client, rack["id"], name="occupant", u_position=5,
                  face="front")
    payload = _bundle({
        "racks": (["name"], [["R-C"]]),
        "devices": (
            ["name", "rack", "u_position", "face"],
            [["clash", "R-C", 5, "front"]],
        ),
    })
    r = await _import(client, payload, on_existing="merge")
    dev_rows = _by_sheet(r)["devices"]
    assert dev_rows[0]["action"] == "error"
    assert "conflict" in dev_rows[0]["detail"].lower() or "conflicts" in dev_rows[0]["detail"].lower()
    # errors refuse the commit without force
    r = await _import(
        client, payload, on_existing="merge", dry_run=False
    )
    assert not r["committed"]
    assert len((await client.get("/api/v1/devices")).json()["items"]) == 1
    # force commits only the clean rows
    r = await _import(
        client, payload, on_existing="merge", dry_run=False, force=True
    )
    assert r["committed"]
    assert len((await client.get("/api/v1/devices")).json()["items"]) == 1


async def test_unknown_sheet_warned_and_ignored(client: AsyncClient):
    payload = _bundle({
        "racks": (["name", "height_u"], [["R-OK", 12]]),
        "notes": (["foo", "bar"], [[1, 2]]),
    })
    r = await _import(client, payload)
    assert any(
        "notes" in w and "ignored" in w for w in r["warnings"]
    )
    assert _by_sheet(r)["racks"][0]["action"] == "create"


async def test_hebrew_and_alias_headers(client: AsyncClient):
    payload = _csv("שם ארון,אתר,גובה\nארון-א,אתר-א,24\n")
    r = await _import(client, payload, "racks.csv", dry_run=False)
    assert r["committed"]
    racks = (await client.get("/api/v1/racks")).json()["items"]
    assert racks[0]["name"] == "ארון-א" and racks[0]["height_u"] == 24

    # device sheet with aliased headers inside a bundle
    payload = _bundle({
        "racks": (["name"], [["RA"]]),
        "devices": (
            ["name", "rack", "u_position"],
            [["aliased", "RA", 2]],
        ),
    })
    r = await _import(client, payload, dry_run=False)
    assert r["committed"]
    dev = (await client.get("/api/v1/devices")).json()["items"][0]
    assert dev["name"] == "aliased" and dev["u_position"] == 2


async def test_import_rbac(client: AsyncClient, session: AsyncSession, auth_on):
    await _mkuser(session, "v", UserRole.VIEWER)
    payload = _csv("name\nR-RBAC\n")
    await _login(client, "v")
    r = await client.post(
        "/api/v1/racks/import",
        content=payload,
        params={"filename": "racks.csv"},
    )
    assert r.status_code == 403
    # export stays readable for viewers
    assert (await client.get("/api/v1/racks/export.csv")).status_code == 200


async def test_import_writes_changelog(client: AsyncClient):
    payload = _csv("name\nR-LOG\n")
    await _import(client, payload, "racks.csv", dry_run=False)
    log = (await client.get("/api/v1/changelog")).json()
    entries = log["items"] if isinstance(log, dict) else log
    assert any(
        "R-LOG" in (e.get("summary") or e.get("message") or "")
        or "R-LOG" in str(e)
        for e in entries
    )


async def test_detect_reports_sheets(client: AsyncClient):
    payload = _bundle({
        "groups": (["name", "site"], [["Row A", "DC-1"]]),
        "racks": (["name", "site"], [["R-D", "DC-1"]]),
        "junk": (["x"], [[1]]),
    })
    r = await _import(client, payload, detect=True)
    fams = {s["name"]: s["family"] for s in r["sheets"]}
    assert fams == {"groups": "groups", "racks": "racks", "junk": None}
    assert r["warnings"]


async def test_import_interfaces_connected_ip(client: AsyncClient):
    """connected_ip resolves against existing addresses — regression for a
    missing await on the ip lookup (500ed on any bundle carrying the col)."""
    site = await _site(client)
    rack = await _rack(client, name="R-IP", site_id=site["id"])
    dev = await _racked(client, rack["id"], name="srv-ip", u_position=1)
    vrfs = (await client.get("/api/v1/vrfs")).json()
    vrf = (vrfs["items"] if isinstance(vrfs, dict) else vrfs)[0]
    p = await client.post(
        "/api/v1/prefixes",
        json={"prefix": "10.80.0.0/24", "vrf_id": vrf["id"]},
    )
    assert p.status_code == 201, p.text
    ip = await client.post(
        "/api/v1/addresses",
        json={
            "address": "10.80.0.10",
            "prefix_id": p.json()["id"],
            "device_id": dev["id"],
        },
    )
    assert ip.status_code == 201, ip.text

    payload = _bundle({
        "interfaces": (
            ["device", "name", "kind", "speed_mbps", "connected_ip"],
            [
                ["srv-ip", "eth0", "rj45", 1000, "10.80.0.10"],
                ["srv-ip", "eth1", "rj45", 1000, "10.80.0.99"],
            ],
        ),
    })
    r = await _import(client, payload, dry_run=False)
    assert r["committed"]
    ifaces = (
        await client.get(f"/api/v1/devices/{dev['id']}/interfaces")
    ).json()
    by = {i["name"]: i for i in ifaces}
    assert by["eth0"]["connected_ip"]["id"] == ip.json()["id"]
    assert by["eth1"]["connected_ip"] is None
    eth1 = [x for x in r["rows"] if "eth1" in x["detail"]][0]
    assert "linked ip skipped" in eth1["detail"]


async def test_bundle_union_mapping(client: AsyncClient):
    """The dialog sends ONE mapping dict covering every sheet's headers —
    each sheet must apply only the keys it owns, not 422 on the rest."""
    payload = _bundle({
        "groups": (["name"], [["Row A"]]),
        "racks": (
            ["name", "group", "group_position"],
            # position 0 is legal (model is 0-based) — a real export of a
            # group's first rack emits 0 and must round-trip
            [["R-M", "Row A", 0]],
        ),
        "devices": (["name", "rack", "u_position"], [["srv-m", "R-M", 3]]),
    })
    union = json.dumps({
        "name": "name", "group": "group", "group_position": "group_position",
        "rack": "rack", "u_position": "u_position",
    })
    r = await _import(client, payload, dry_run=False, mapping=union)
    assert r["committed"], r["rows"]
    grp = (await client.get("/api/v1/rack-groups")).json()[0]
    detail = (await client.get(f"/api/v1/rack-groups/{grp['id']}")).json()
    assert detail["racks"][0]["group_position"] == 0
    dev = (await client.get("/api/v1/devices")).json()["items"][0]
    assert dev["name"] == "srv-m" and dev["u_position"] == 3

    # a source that appears on NO sheet still 422s (typos stay loud)
    r = await client.post(
        "/api/v1/racks/import",
        content=payload,
        params={
            "filename": "racks.xlsx",
            "mapping": json.dumps({"nope": "name"}),
        },
    )
    assert r.status_code == 422
