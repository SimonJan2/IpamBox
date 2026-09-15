"""Workbook import: normalizer/parser unit tests (no DB) + API e2e."""
import pytest

from app.services.workbook import normalize as nz
from app.services.workbook.classify import classify_sheet
from app.services.workbook.parsers import parse_site_sheet, parse_sites_master
from app.services.workbook.reader import SheetMatrix


class TestNormalize:
    def test_assemble_ip_variants(self):
        assert nz.assemble_ip("10.2.1.", "81") == "10.2.1.81"
        assert nz.assemble_ip("10.192.10", "60") == "10.192.10.60"
        assert nz.assemble_ip("10.86.01", "1") == "10.86.1.1"  # leading zero
        assert nz.assemble_ip("10.10.1.81", "") == "10.10.1.81"
        assert nz.assemble_ip("10.x.252.", "9") is None       # placeholder
        assert nz.assemble_ip("10.2.1.", "") is None
        assert nz.assemble_ip("10.2.1.", "300") is None
        assert nz.assemble_ip("", "") is None

    def test_split_multi_ip_linklocal(self):
        valid, ll = nz.split_multi_ip("10.10.10.12, 169.254.161.144, 10.192.10.67")
        assert valid == ["10.10.10.12", "10.192.10.67"]
        assert ll == ["169.254.161.144"]

    def test_parse_range_end(self):
        assert nz.parse_range_end("10.79.1.", "101-200") == ("10.79.1.101", "10.79.1.200")
        assert nz.parse_range_end("10.79.1.", "5") is None

    def test_norm_mac(self):
        assert nz.norm_mac("00-02-E3-30-C3-DF") == "00:02:E3:30:C3:DF"
        assert nz.norm_mac("00022e333585") == "00:02:2E:33:35:85"   # bare hex
        assert nz.norm_mac("0002.2e33.3585") == "00:02:2E:33:35:85"  # cisco
        assert nz.norm_mac("00-of-fe-47-913-10") is None            # garbage
        assert nz.norm_mac("") is None

    def test_excel_date(self):
        from datetime import date, datetime
        assert nz.excel_date(47149) == date(2029, 1, 31)
        assert nz.excel_date(datetime(2030, 5, 1, 12, 0)) == date(2030, 5, 1)
        assert nz.excel_date("3/08/27") == date(2027, 8, 3)
        assert nz.excel_date("n/a") is None
        assert nz.excel_date(None) is None

    def test_status_of(self):
        assert nz.status_of("פעיל") == "active"
        assert nz.status_of("פעיל, הר חוצבים") == "active"
        assert nz.status_of("לא פעיל") == "offline"
        assert nz.status_of("בהקמה") == "reserved"
        assert nz.status_of("בוטל") == "skip"
        assert nz.status_of("שער גייטפאס כניסות") is None  # description, not status
        assert nz.status_of("") is None

    def test_clean(self):
        assert nz.clean('נתב""ג') == 'נתב"ג'
        assert nz.clean("Rafiah    ***********") == "Rafiah"
        assert nz.clean("  a\nb  ") == "a b"
        assert nz.clean(42.0) == "42"

    def test_fold_hebrew(self):
        assert nz.fold_hebrew("עלמך") == "עלמכ"  # final mem -> mem
        assert nz.fold_hebrew("אלנבי") == "אלנבי"

    def test_second_octet_and_mask(self):
        assert nz.second_octet("10.2.1.5") == 2
        assert nz.second_octet("bad") is None
        assert nz.mask_to_prefixlen("255.255.255.0") == 24
        assert nz.mask_to_prefixlen("") is None
        assert nz.network_of("10.2.1.4", "255.255.255.0") == "10.2.1.0/24"


def _matrix(name, rows):
    return SheetMatrix(name=name, rows=rows)


class TestClassify:
    def test_site_sheet_header(self):
        sm = _matrix("x", [["IP Address", "end ip", "Subnet mask", "Node Name"]])
        fam, hidx, _ = classify_sheet(sm)
        assert (fam, hidx) == ("site_sheet", 0)

    def test_header_above_junk_row(self):
        sm = _matrix("x", [
            ["", "", "some note row"],
            ["IP Address", "end ip", "Subnet mask"],
        ])
        fam, hidx, _ = classify_sheet(sm)
        assert (fam, hidx) == ("site_sheet", 1)

    def test_circuits(self):
        sm = _matrix("x", [["סביבת חיבור", "מאתר", "קוד בבזק"]])
        fam, _, _ = classify_sheet(sm)
        assert fam == "circuits"

    def test_sites_master(self):
        sm = _matrix("x", [["Name", "Code", "type", "Subet range"]])
        fam, _, _ = classify_sheet(sm)
        assert fam == "sites_master"

    def test_headerless_ip_sniff(self):
        sm = _matrix("x", [["", "10.91.1.", "51", "255.255.255.0"],
                           ["", "10.91.1.", "254", "255.255.255.0"],
                           ["", "10.91.1.", "250", "255.255.255.0"]])
        fam, hidx, warns = classify_sheet(sm)
        assert fam == "site_sheet" and hidx == -1 and warns

    def test_empty_and_unknown(self):
        assert classify_sheet(_matrix("e", []))[0] == "empty"
        assert classify_sheet(_matrix("u", [["a", "b"], ["c", "d"]]))[0] == "unknown"


class TestSiteSheetParser:
    def test_split_octet_and_blank_end_header(self):
        sm = _matrix("s", [
            ["IP Address", "", "Subnet mask", "Node Name", "MAC"],
            ["10.2.1.", "81", "255.255.255.0", "SRV1", "00022e333585"],
        ])
        recs, _ = parse_site_sheet(sm, 0)
        assert recs[0]["address"] == "10.2.1.81"
        assert recs[0]["hostname"] == "SRV1"
        assert recs[0]["mac"] == "00:02:2E:33:35:85"

    def test_carry_forward_base(self):
        sm = _matrix("s", [
            ["IP", "End", "Server Name"],
            ["172.20.1.", "1", "fw2"],
            ["", "2", "sim"],
        ])
        recs, _ = parse_site_sheet(sm, 0)
        assert [r["address"] for r in recs] == ["172.20.1.1", "172.20.1.2"]

    def test_duplicated_column_blocks(self):
        sm = _matrix("s", [
            ["IP Address", "end ip", "Node Name", "IP Address", "end ip", "Node Name"],
            ["10.2.1.", "149", "GP05", "10.2.1.", "148", "GP03"],
        ])
        recs, warns = parse_site_sheet(sm, 0)
        assert len(recs) == 2
        assert {r["address"] for r in recs} == {"10.2.1.149", "10.2.1.148"}
        assert warns and "blocks" in warns[0]

    def test_subnet_declaration_and_section_row(self):
        sm = _matrix("s", [
            ["IP Address", "end ip", "Subnet mask", "Node Name"],
            ["10.84.1", "", "255.255.255.0", ""],
            ["מתפ\"ש (Matpash)", "", "", ""],
        ])
        recs, _ = parse_site_sheet(sm, 0)
        kinds = [r["kind"] for r in recs]
        assert kinds == ["subnet", "skip"]

    def test_range_row(self):
        sm = _matrix("s", [
            ["IP Address", "end ip", "Subnet mask", "Node Name"],
            ["10.79.1.", "101-200", "255.255.255.0", "DHCP"],
        ])
        recs, _ = parse_site_sheet(sm, 0)
        assert recs[0]["kind"] == "range"
        assert recs[0]["range"] == ("10.79.1.101", "10.79.1.200")


class TestSitesMasterParser:
    def test_subnet_fragments_and_number(self):
        sm = _matrix("רשימת אתרים", [
            ["Name", "Code", "type", "Subet range", "", "", "", "Subet", "הערות"],
            ["Karni", "KARN", "בינוני", "10", "1", ".0.", "0/24", "255.255.255.0", "לא פעיל"],
        ])
        recs, _ = parse_sites_master(sm, 0)
        r = recs[0]
        assert r["name"] == "Karni" and r["code"] == "KARN"
        assert r["cidr"] == "10.1.0.0/24" and r["site_number"] == 1
        assert r["is_active"] is False


# ---------------------------------------------------------------------------
# API e2e — needs the test DB (skipped automatically when Postgres is absent)
# ---------------------------------------------------------------------------

pytestmark_api = pytest.mark.anyio


def _xlsx_bytes():
    """Small synthetic workbook: sites master + one site sheet + circuits."""
    import io
    import openpyxl

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "רשימת אתרים"
    ws.append(["Name", "Code", "type", "Subet range", "", "", "", "Subet", "הערות"])
    ws.append(["Alenbi", "ALNB", "גדול", "10", "2", ".0.", "0/24", "255.255.255.0", ""])
    ws2 = wb.create_sheet("אלנבי")
    ws2.append(["IP Address", "end ip", "Subnet mask", "Node Name", "MAC"])
    ws2.append(["10.2.1.", "81", "255.255.255.0", "SRV-ALB", "00022e333585"])
    ws2.append(["10.2.1.", "82", "255.255.255.0", "PRT-ALB", "bad-mac"])
    ws2.append(["10.2.1.", "81", "255.255.255.0", "DUP", ""])  # batch dup
    ws3 = wb.create_sheet("קוי-SDH")
    ws3.append(["סביבת חיבור", "מאתר", "מספר אתר", "סוג הקו", "קוד בבזק"])
    ws3.append(["Lev", "Alenbi", "2", "ipvpn", "828328469"])
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


async def test_import_e2e(client):
    payload = _xlsx_bytes()
    r = await client.post(
        "/api/v1/imports/workbook?filename=test.xlsx",
        content=payload,
        headers={"content-type": "application/octet-stream"},
    )
    assert r.status_code == 201, r.text
    body = r.json()
    batch_id = body["batch"]["id"]
    fams = {s["sheet"]: s["family"] for s in body["sheets"]}
    assert fams["רשימת אתרים"] == "sites_master"
    assert fams["אלנבי"] == "site_sheet"

    # preview already ran at upload — commit it
    r = await client.post(f"/api/v1/imports/{batch_id}/commit", json={"partial": True})
    assert r.status_code == 200, r.text
    counts = r.json()["counts"]
    assert counts.get("error", 0) == 0

    sites = (await client.get("/api/v1/sites")).json()
    alb = next(s for s in sites if s["name"] == "Alenbi")
    assert alb["code"] == "ALNB" and alb["site_number"] == 2

    addrs = (await client.get("/api/v1/addresses")).json()
    ips = {a["address"] for a in addrs}
    assert "10.2.1.81" in ips and "10.2.1.82" in ips
    bad_mac = next(a for a in addrs if a["address"] == "10.2.1.82")
    assert bad_mac["mac_address"] is None
    assert bad_mac["custom_fields"]["mac_raw"] == "bad-mac"

    circuits = (await client.get("/api/v1/imports")).json()
    assert circuits[0]["status"] == "committed"


async def test_import_rejects_non_xlsx(client):
    r = await client.post("/api/v1/imports/workbook", content=b"not a zip")
    assert r.status_code == 422


async def test_commit_twice_rejected(client):
    payload = _xlsx_bytes()
    r = await client.post("/api/v1/imports/workbook", content=payload)
    batch_id = r.json()["batch"]["id"]
    await client.post(f"/api/v1/imports/{batch_id}/commit", json={"partial": True})
    r = await client.post(f"/api/v1/imports/{batch_id}/commit", json={})
    assert r.status_code == 409
