"""Custom lists: CRUD + rows + IP resolution + workbook list-target import."""
import io

import pytest
import pytest_asyncio
from sqlalchemy import select

from app.core.config import get_settings
from app.core.redis import get_redis
from app.models.custom_list import CustomList, CustomListRow
from app.models.ip_address import IPAddress
from app.models.user import UserRole
from app.schemas.import_batch import ListTarget, PreviewOptions
from app.services.workbook.listparse import extract_list_table, pick_key_column
from app.services.workbook.plan import DbState, _Planner
from app.services.workbook.reader import SheetMatrix
from tests.test_rbac import login, mkuser


def _matrix(name, rows):
    return SheetMatrix(name=name, rows=rows)


def _preview_of(result, sheet):
    return next(s for s in result["sheets"] if s["sheet"] == sheet)


COLS = [{"key": "c0", "label": "Name"}, {"key": "c1", "label": "IP", "type": "ip"}]


async def _mklist(client, name="שרתים בייצור", **kw):
    r = await client.post(
        "/api/v1/lists",
        json={"name": name, "columns": COLS, "key_column": "c0", **kw},
    )
    assert r.status_code == 201, r.text
    return r.json()


class TestListCRUD:
    async def test_create_get_slug(self, client):
        lst = await _mklist(client)
        assert lst["slug"].startswith("שרתים-בייצור")
        assert lst["row_count"] == 0
        got = await client.get(f"/api/v1/lists/{lst['id']}")
        assert got.status_code == 200 and got.json()["name"] == "שרתים בייצור"

    async def test_duplicate_name_gets_unique_slug(self, client):
        a = await _mklist(client, name="dup")
        b = await _mklist(client, name="dup")
        assert a["slug"] != b["slug"]

    async def test_index_lists_row_counts(self, client):
        lst = await _mklist(client)
        await client.post(
            f"/api/v1/lists/{lst['id']}/rows", json={"data": {"c0": "a"}}
        )
        items = (await client.get("/api/v1/lists")).json()["items"]
        assert items[0]["row_count"] == 1

    async def test_patch_columns_and_key(self, client):
        lst = await _mklist(client)
        r = await client.patch(
            f"/api/v1/lists/{lst['id']}",
            json={"columns": COLS + [{"key": "c2", "label": "Owner", "type": "owner"}]},
        )
        assert r.status_code == 200
        assert [c["label"] for c in r.json()["columns"]] == ["Name", "IP", "Owner"]

    async def test_key_column_must_exist(self, client):
        r = await client.post(
            "/api/v1/lists",
            json={"name": "x", "columns": COLS, "key_column": "c9"},
        )
        assert r.status_code == 422

    async def test_delete_cascades_rows(self, client, session):
        lst = await _mklist(client)
        rr = await client.post(
            f"/api/v1/lists/{lst['id']}/rows", json={"data": {"c0": "a"}}
        )
        assert rr.status_code == 201
        r = await client.delete(f"/api/v1/lists/{lst['id']}")
        assert r.status_code == 204
        left = (
            await session.execute(select(CustomListRow))
        ).scalars().all()
        assert left == []


class TestRows:
    async def test_row_crud_and_merge_update(self, client):
        lst = await _mklist(client)
        r = await client.post(
            f"/api/v1/lists/{lst['id']}/rows",
            json={"data": {"c0": "SRV1", "c1": "10.0.0.1"}},
        )
        row = r.json()
        # partial data merge: c0 kept, c1 replaced, null deletes a key
        r = await client.patch(
            f"/api/v1/lists/{lst['id']}/rows/{row['id']}",
            json={"data": {"c1": "10.0.0.2"}},
        )
        assert r.status_code == 200
        assert r.json()["data"] == {"c0": "SRV1", "c1": "10.0.0.2"}
        assert r.json()["manually_edited"] is True
        r = await client.patch(
            f"/api/v1/lists/{lst['id']}/rows/{row['id']}",
            json={"data": {"c1": None}},
        )
        assert r.json()["data"] == {"c0": "SRV1"}

    async def test_row_wrong_list_404(self, client):
        a = await _mklist(client, name="a")
        b = await _mklist(client, name="b")
        rr = await client.post(
            f"/api/v1/lists/{a['id']}/rows", json={"data": {"c0": "x"}}
        )
        row = rr.json()
        r = await client.patch(
            f"/api/v1/lists/{b['id']}/rows/{row['id']}", json={"data": {}}
        )
        assert r.status_code == 404

    async def test_rows_search_folds_hebrew(self, client):
        lst = await _mklist(client)
        await client.post(
            f"/api/v1/lists/{lst['id']}/rows",
            json={"data": {"c0": "עלמך"}},
        )
        items = (
            await client.get(f"/api/v1/lists/{lst['id']}/rows?q=עלמכ")
        ).json()
        assert items["total"] == 1  # final mem folded to base mem

    async def test_reorder(self, client):
        lst = await _mklist(client)
        ids = []
        for v in ("a", "b", "c"):
            rr = await client.post(
                f"/api/v1/lists/{lst['id']}/rows", json={"data": {"c0": v}}
            )
            ids.append(rr.json()["id"])
        r = await client.post(
            f"/api/v1/lists/{lst['id']}/rows/reorder",
            json={"ids": [ids[2], ids[0], ids[1]]},
        )
        assert r.status_code == 204
        items = (await client.get(f"/api/v1/lists/{lst['id']}/rows")).json()
        assert [i["data"]["c0"] for i in items["items"]] == ["c", "a", "b"]

    async def test_reorder_rejects_foreign_rows(self, client):
        a = await _mklist(client, name="a")
        b = await _mklist(client, name="b")
        ra = await client.post(
            f"/api/v1/lists/{a['id']}/rows", json={"data": {"c0": "x"}}
        )
        rb = await client.post(
            f"/api/v1/lists/{b['id']}/rows", json={"data": {"c0": "y"}}
        )
        r = await client.post(
            f"/api/v1/lists/{a['id']}/rows/reorder",
            json={"ids": [ra.json()["id"], rb.json()["id"]]},
        )
        assert r.status_code == 422

    async def test_ip_cells_resolve(self, client, session):
        lst = await _mklist(client)
        await client.post(
            f"/api/v1/lists/{lst['id']}/rows",
            json={"data": {"c0": "SRV1", "c1": "10.9.9.9"}},
        )
        # nothing in ip_addresses yet -> unresolved
        page = (await client.get(f"/api/v1/lists/{lst['id']}/rows")).json()
        assert page["resolved"] == {}
        # create the address, re-fetch -> resolved with live status
        from app.models.ip_address import IPStatus
        from app.models.prefix import Prefix, PrefixStatus
        from app.models.vrf import VRF

        vrf = (await session.execute(select(VRF))).scalars().first()
        p = Prefix(prefix="10.9.9.0/24", vrf_id=vrf.id, status=PrefixStatus.ACTIVE)
        session.add(p)
        await session.flush()
        session.add(
            IPAddress(
                address="10.9.9.9", address_int=168364297,
                prefix_id=p.id, vrf_id=vrf.id, status=IPStatus.ACTIVE,
                hostname="srv1",
            )
        )
        await session.commit()
        page = (await client.get(f"/api/v1/lists/{lst['id']}/rows")).json()
        assert page["resolved"]["10.9.9.9"]["hostname"] == "srv1"
        assert page["resolved"]["10.9.9.9"]["status"] == "active"

    async def test_resolve_handles_ips_above_int32(self, client):
        # address_int is Numeric(39,0); an expanding IN() over plain ints
        # binds as int4 and overflows asyncpg for IPv4 >= 128.0.0.0.
        lst = await _mklist(client)
        await client.post(
            f"/api/v1/lists/{lst['id']}/rows",
            json={"data": {"c0": "SRV2", "c1": "170.0.0.5"}},
        )
        r = await client.get(f"/api/v1/lists/{lst['id']}/rows")
        assert r.status_code == 200, r.text
        assert r.json()["resolved"] == {}


class TestExtract:
    def test_headers_and_types(self):
        sm = _matrix("שרתים בייצור", [
            ["Name", "Guest OS", "IP Address", "Expires"],
            ["SRV1", "Windows", "10.1.1.1", "03/08/27"],
            ["SRV2", "Linux", "10.1.1.2", "04/08/27"],
            ["SRV3", "Linux", "10.1.1.3, 169.254.1.1", "05/08/27"],
        ])
        cols, rows = extract_list_table(sm, 0)
        assert [c["label"] for c in cols] == ["Name", "Guest OS", "IP Address", "Expires"]
        assert cols[2]["type"] == "ip" and cols[2]["multi"] is True
        assert cols[3]["type"] == "date"
        assert cols[1]["type"] == "select"  # 2 distinct values
        assert rows[2]["data"]["c2"] == "10.1.1.3, 169.254.1.1"
        assert pick_key_column(cols, rows) == "c0"

    def test_headerless_positional(self):
        sm = _matrix("raw", [["a", "1"], ["b", "2"], ["c", "3"]])
        cols, rows = extract_list_table(sm, -1)
        assert cols[0]["label"] == "Column 1"
        assert len(rows) == 3

    def test_blank_header_gets_positional_label(self):
        sm = _matrix("s", [
            ["Name", "IP", ""],
            ["SRV1", "10.0.0.1", "רומן"],
        ])
        cols, _ = extract_list_table(sm, 0)
        assert cols[2]["label"] == "Column 3"

    def test_dup_headers_deduped(self):
        sm = _matrix("s", [["Notes", "x", "Notes"], ["a", "b", "c"]])
        cols, _ = extract_list_table(sm, 0)
        assert [c["label"] for c in cols] == ["Notes", "x", "Notes (2)"]


class TestPlanListTarget:
    def _plan(self, sheets, list_sheets):
        return _Planner(
            DbState(), PreviewOptions(list_sheets=list_sheets)
        ).build(sheets)

    def test_list_only_sheet_bypasses_family(self):
        """also_ipam=False: a servers sheet produces ONLY list rows — no
        addresses or assets leak into the plan."""
        sm = _matrix("שרתים בייצור", [
            ["Name", "Guest OS", "IP Address"],
            ["SRV1", "Windows", "10.55.1.1"],
            ["SRV2", "Linux", "10.55.1.2"],
        ])
        result = self._plan(
            [sm],
            {"שרתים בייצור": ListTarget(also_ipam=False)},
        )
        assert result["plan"]["addresses"] == []
        assert result["plan"]["assets"] == []
        cl = result["plan"]["custom_lists"]
        assert len(cl) == 1 and cl[0]["name"] == "שרתים בייצור"
        assert len(cl[0]["rows"]) == 2
        assert cl[0]["key_column"] == "c0"
        prev = _preview_of(result, "שרתים בייצור")
        assert prev["list_name"] == "שרתים בייצור"

    def test_also_ipam_feeds_both(self):
        sm = _matrix("שרתים בייצור", [
            ["Name", "Guest OS", "IP Address"],
            ["SRV1", "Windows", "10.55.1.1"],
        ])
        result = self._plan(
            [sm],
            {"שרתים בייצור": ListTarget(also_ipam=True)},
        )
        assert len(result["plan"]["custom_lists"]) == 1
        assert len(result["plan"]["addresses"]) == 1  # IPAM still gets it

    def test_key_column_by_label(self):
        sm = _matrix("s", [
            ["IP", "Name"],
            ["10.0.0.1", "SRV1"],
        ])
        result = self._plan(
            [sm], {"s": ListTarget(key_column="Name", also_ipam=False)}
        )
        assert result["plan"]["custom_lists"][0]["key_column"] == "c1"


# ---------------------------------------------------------------------------
# e2e: upload -> preview with list target -> commit -> rows + merge re-import
# ---------------------------------------------------------------------------


def _servers_xlsx(rows_v1=True):
    import openpyxl

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "שרתים בייצור"
    ws.append(["Name", "Guest OS", "IP Address"])
    if rows_v1:
        ws.append(["SRV1", "Windows", "10.55.1.1"])
        ws.append(["SRV2", "Linux", "10.55.1.2"])
    else:
        # v2: SRV1 vanished, SRV2's OS changed, SRV3 is new
        ws.append(["SRV2", "RHEL", "10.55.1.2"])
        ws.append(["SRV3", "Linux", "10.55.1.3"])
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


async def _upload(client, payload, filename="t.xlsx"):
    r = await client.post(
        f"/api/v1/imports/workbook?filename={filename}",
        content=payload,
        headers={"content-type": "application/octet-stream"},
    )
    assert r.status_code == 201, r.text
    return r.json()["batch"]["id"]


async def test_import_as_list_e2e(client):
    batch_id = await _upload(client, _servers_xlsx())
    r = await client.post(
        f"/api/v1/imports/{batch_id}/preview",
        json={
            "list_sheets": {
                "שרתים בייצור": {"name": "שרתים בייצור", "also_ipam": False}
            }
        },
    )
    assert r.status_code == 200, r.text
    sheet = next(
        s for s in r.json()["sheets"] if s["sheet"] == "שרתים בייצור"
    )
    assert sheet["list_name"] == "שרתים בייצור"

    r = await client.post(f"/api/v1/imports/{batch_id}/commit", json={})
    assert r.status_code == 200, r.text

    lists = (await client.get("/api/v1/lists")).json()["items"]
    lst = next(l for l in lists if l["name"] == "שרתים בייצור")
    assert lst["row_count"] == 2
    assert lst["source_sheet"] == "שרתים בייצור"
    assert lst["key_column"] == "c0"
    rows = (await client.get(f"/api/v1/lists/{lst['id']}/rows")).json()
    assert {r["data"]["c0"] for r in rows["items"]} == {"SRV1", "SRV2"}


async def test_reimport_merges_by_key(client):
    """v2 workbook: SRV2 edited, SRV3 added, SRV1 missing -> merge keeps
    SRV1, updates SRV2, creates SRV3; a UI pin survives."""
    batch_id = await _upload(client, _servers_xlsx())
    await client.post(
        f"/api/v1/imports/{batch_id}/preview",
        json={"list_sheets": {"שרתים בייצור": {"also_ipam": False}}},
    )
    await client.post(f"/api/v1/imports/{batch_id}/commit", json={})
    lst = (await client.get("/api/v1/lists")).json()["items"][0]
    rows = (await client.get(f"/api/v1/lists/{lst['id']}/rows")).json()["items"]
    srv1 = next(r for r in rows if r["data"]["c0"] == "SRV1")
    await client.patch(
        f"/api/v1/lists/{lst['id']}/rows/{srv1['id']}", json={"pinned": True}
    )

    batch2 = await _upload(client, _servers_xlsx(rows_v1=False))
    r = await client.post(
        f"/api/v1/imports/{batch2}/preview",
        json={"list_sheets": {"שרתים בייצור": {"also_ipam": False}}},
    )
    details = [r["detail"] for r in r.json()["rows"]]
    assert any("missing from source" in d for d in details)
    await client.post(f"/api/v1/imports/{batch2}/commit", json={})

    rows = (await client.get(f"/api/v1/lists/{lst['id']}/rows")).json()["items"]
    by_name = {r["data"]["c0"]: r for r in rows}
    assert set(by_name) == {"SRV1", "SRV2", "SRV3"}
    assert by_name["SRV1"]["id"] == srv1["id"]          # kept, not re-created
    assert by_name["SRV1"]["pinned"] is True           # pin survived
    assert by_name["SRV3"]["data"]["c2"] == "10.55.1.3"


async def test_manually_edited_row_wins_conflict(client):
    batch_id = await _upload(client, _servers_xlsx())
    await client.post(
        f"/api/v1/imports/{batch_id}/preview",
        json={"list_sheets": {"שרתים בייצור": {"also_ipam": False}}},
    )
    await client.post(f"/api/v1/imports/{batch_id}/commit", json={})
    lst = (await client.get("/api/v1/lists")).json()["items"][0]
    rows = (await client.get(f"/api/v1/lists/{lst['id']}/rows")).json()["items"]
    srv1 = next(r for r in rows if r["data"]["c0"] == "SRV1")
    # user edits the OS cell — the sheet still says Windows
    await client.patch(
        f"/api/v1/lists/{lst['id']}/rows/{srv1['id']}",
        json={"data": {"c1": "Windows 2025"}},
    )

    batch2 = await _upload(client, _servers_xlsx())
    r = await client.post(
        f"/api/v1/imports/{batch2}/preview",
        json={"list_sheets": {"שרתים בייצור": {"also_ipam": False}}},
    )
    conflicts = [r for r in r.json()["rows"] if r["action"] == "conflict"]
    assert any("edited in-app" in c["detail"] for c in conflicts)
    await client.post(f"/api/v1/imports/{batch2}/commit", json={})

    rows = (await client.get(f"/api/v1/lists/{lst['id']}/rows")).json()["items"]
    srv1 = next(r for r in rows if r["data"]["c0"] == "SRV1")
    assert srv1["data"]["c1"] == "Windows 2025"  # manual value kept


@pytest_asyncio.fixture
async def auth_on():
    """Turn auth on for a test, restore insecure mode after, and flush
    session/lockout keys (mirrors the fixture in test_rbac)."""
    settings = get_settings()
    settings.ipambox_allow_insecure = False
    try:
        yield
    finally:
        settings.ipambox_allow_insecure = True
        r = get_redis()
        for pattern in ("ipam:session:*", "ipam:loginfails:*", "ipam:lockout:*"):
            async for key in r.scan_iter(pattern):
                await r.delete(key)
        await r.aclose()


class TestPermissions:
    """Viewer tier can read lists/rows but every mutation is 403."""

    async def test_viewer_read_only(self, client, session, auth_on):
        # seed straight through the session — auth is already on, so the
        # unauthenticated client can't write even for setup
        lst = CustomList(
            name="שרתים בייצור", slug="srv", columns=COLS, key_column="c0"
        )
        session.add(lst)
        await session.flush()
        row = CustomListRow(list_id=lst.id, data={"c0": "SRV1"})
        session.add(row)
        await session.commit()

        await mkuser(session, "list-viewer", UserRole.VIEWER)
        await login(client, "list-viewer")

        assert (await client.get("/api/v1/lists")).status_code == 200
        assert (
            await client.get(f"/api/v1/lists/{lst.id}/rows")
        ).status_code == 200
        for r in (
            await client.post("/api/v1/lists", json={"name": "nope"}),
            await client.patch(
                f"/api/v1/lists/{lst.id}", json={"name": "nope"}
            ),
            await client.post(
                f"/api/v1/lists/{lst.id}/rows", json={"data": {}}
            ),
            await client.patch(
                f"/api/v1/lists/{lst.id}/rows/{row.id}",
                json={"data": {"c0": "x"}},
            ),
            await client.delete(f"/api/v1/lists/{lst.id}/rows/{row.id}"),
            await client.delete(f"/api/v1/lists/{lst.id}"),
        ):
            assert r.status_code == 403, (r.status_code, r.text)


class TestBulkRows:
    async def test_bulk_pin_color_delete(self, client):
        lst = await _mklist(client)
        ids = []
        for v in ("a", "b", "c"):
            rr = await client.post(
                f"/api/v1/lists/{lst['id']}/rows", json={"data": {"c0": v}}
            )
            ids.append(rr.json()["id"])

        r = await client.post(
            f"/api/v1/lists/{lst['id']}/rows/bulk",
            json={"ids": ids[:2], "action": "pin"},
        )
        assert r.status_code == 200 and r.json()["affected"] == 2
        rows = (await client.get(f"/api/v1/lists/{lst['id']}/rows")).json()[
            "items"
        ]
        by = {r["data"]["c0"]: r for r in rows}
        assert by["a"]["pinned"] and by["b"]["pinned"]
        assert not by["c"]["pinned"]

        r = await client.post(
            f"/api/v1/lists/{lst['id']}/rows/bulk",
            json={"ids": ids[:2], "action": "set_color", "row_color": "#ff0000"},
        )
        rows = (await client.get(f"/api/v1/lists/{lst['id']}/rows")).json()[
            "items"
        ]
        assert all(r["row_color"] == "#ff0000" for r in rows[:2])

        # stale ids are reported, not silently counted
        r = await client.post(
            f"/api/v1/lists/{lst['id']}/rows/bulk",
            json={"ids": [ids[0], 999999], "action": "delete"},
        )
        assert r.json()["affected"] == 1
        assert r.json()["not_found"] == [999999]

        r = await client.post(
            f"/api/v1/lists/{lst['id']}/rows/bulk",
            json={"ids": ids, "action": "bogus"},
        )
        assert r.status_code == 422


class TestCsvImport:
    async def test_csv_upload_to_list(self, client):
        payload = (
            "Name,OS,IP\nSRV1,Windows,10.7.7.1\nSRV2,Linux,10.7.7.2\n"
        ).encode("utf-8-sig")  # BOM like Excel writes
        batch_id = await _upload(client, payload, "prod servers.csv")
        r = await client.post(
            f"/api/v1/imports/{batch_id}/preview",
            json={
                "list_sheets": {
                    "prod servers": {"name": "prod servers", "also_ipam": False}
                }
            },
        )
        assert r.status_code == 200, r.text
        sheet = r.json()["sheets"][0]
        assert sheet["sheet"] == "prod servers"
        assert sheet["list_name"] == "prod servers"
        # inferred column types ride along for the wizard's chips
        types = {c["label"]: c["type"] for c in sheet["list_columns"]}
        assert types["IP"] == "ip"

        await client.post(f"/api/v1/imports/{batch_id}/commit", json={})
        lists = (await client.get("/api/v1/lists")).json()["items"]
        lst = next(l for l in lists if l["name"] == "prod servers")
        rows = (await client.get(f"/api/v1/lists/{lst['id']}/rows")).json()
        assert {r["data"]["c0"] for r in rows["items"]} == {"SRV1", "SRV2"}
        # IP cells resolve (10.7.7.x isn't in ip_addresses -> unresolved)
        assert rows["resolved"] == {}

    async def test_csv_cp1255_hebrew(self, client):
        # ANSI Hebrew (windows-1255) — Excel's non-UTF8 CSV export
        payload = "שם,תפקיד\nשרת-א,ממשק\n".encode("cp1255")
        batch_id = await _upload(client, payload, "hebrew.csv")
        r = await client.post(
            f"/api/v1/imports/{batch_id}/preview",
            json={"list_sheets": {"hebrew": {"also_ipam": False}}},
        )
        assert r.status_code == 200, r.text
        await client.post(f"/api/v1/imports/{batch_id}/commit", json={})
        lst = (await client.get("/api/v1/lists")).json()["items"][0]
        rows = (await client.get(f"/api/v1/lists/{lst['id']}/rows")).json()
        assert rows["items"][0]["data"]["c0"] == "שרת-א"
