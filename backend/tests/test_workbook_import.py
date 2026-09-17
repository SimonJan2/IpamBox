"""Workbook import: normalizer/parser unit tests (no DB) + API e2e."""
import pytest

from app.schemas.import_batch import PreviewOptions
from app.services.workbook import normalize as nz
from app.services.workbook.classify import classify_sheet
from app.services.workbook.parsers import (
    parse_assets,
    parse_certificates,
    parse_circuits,
    parse_servers,
    parse_site_sheet,
    parse_sites_master,
)
from app.services.workbook.plan import DbState, _Planner
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
        assert r["blocks"] == {(10, 1)}

    def test_non10x_block_range(self):
        """Integration Site's '172,20-21' fragments -> octet-pair blocks,
        no 10.x site_number."""
        sm = _matrix("רשימת אתרים", [
            ["Name", "Code", "type", "Subet range", "", "", "", "Subet", "הערות"],
            ["Integration Site", "INT", "", "172", "20-21", "1", "", "255.255.255.0", ""],
        ])
        recs, _ = parse_sites_master(sm, 0)
        r = recs[0]
        assert r["name"] == "Integration Site" and r["code"] == "INT"
        assert r["site_number"] is None
        assert r["blocks"] == {(172, 20), (172, 21)}

    def test_anonymous_rows_kept(self):
        """Nameless master rows (10.22/35/37/39) become 'Site N' instead of
        being dropped — notes survive too."""
        sm = _matrix("רשימת אתרים", [
            ["Name", "Code", "type", "Subet range", "", "", "", "Subet", "הערות"],
            ["", "", "", "10", "35", "1", "0/24", "255.255.255.0", "ישן"],
            ["", "", "", "", "", "", "", "", ""],
        ])
        recs, _ = parse_sites_master(sm, 0)
        assert len(recs) == 1
        r = recs[0]
        assert r["name"] == "Site 10.35" and r["site_number"] == 35
        assert r["synthetic_name"] is True
        assert r["cidr"] == "10.35.1.0/24" and r["notes"] == "ישן"

    def test_anonymous_row_uses_former_name(self):
        """'היה "מטה ארצי" בעבר' -> 'מטה ארצי (לשעבר)' — the historical name,
        suffixed so it can't collide with the real מטה ארצי site."""
        sm = _matrix("רשימת אתרים", [
            ["Name", "Code", "type", "Subet range", "", "", "", "Subet", "הערות"],
            ["Mattar", "MTR", "גדול", "10", "20", ".0.", "0/24", "255.255.255.0", ""],
            ["", "", "", "10", "37", "1", "0/24", "255.255.255.0", 'היה "מטה ארצי" בעבר'],
        ])
        recs, _ = parse_sites_master(sm, 0)
        assert recs[1]["name"] == "מטה ארצי (לשעבר)"
        assert recs[1]["synthetic_name"] is True
        assert recs[1]["name"] != recs[0]["name"]

    def test_duplicate_notes_column(self):
        """The real header has 'הערות' twice — first non-empty wins."""
        sm = _matrix("רשימת אתרים", [
            ["Name", "Code", "type", "Subet range", "", "", "", "Subet", "הערות", "", "", "", "הערות"],
            ["Tarkumia", "TAR", "בינוני", "10", "32", ".0.", "0/24", "255.255.255.0", "לא פעיל", "", "", "", ""],
        ])
        recs, _ = parse_sites_master(sm, 0)
        assert recs[0]["notes"] == "לא פעיל"
        assert recs[0]["is_active"] is False


class TestCircuitsParser:
    def test_legacy_bezeq_layout(self):
        """קוי בזק ישן (029) — bandwidth/contact map to real fields, the
        rest of the legacy columns land in notes, not /dev/null."""
        sm = _matrix("קוי בזק ישן", [
            ["#", "סוג אתר", "מאתר", "כמות קווים", "לריכוז קווים", "רוחב פס",
             "מובטח", "סוג הקו", "מועד חיבור", "קוד בבזק", "הערות + איש קשר", "VPI/VCI"],
            ["1", "אתר", "אלנבי", "2", "כן", "512", "כן", "נתונים",
             "1/1/2000", "12345", "יוסי 03-5551234", "0/35"],
        ])
        recs, _ = parse_circuits(sm, 0)
        assert len(recs) == 1
        r = recs[0]
        assert r["site_name"] == "אלנבי" and r["bezeq_circuit_id"] == "12345"
        assert r["bw_down"] == "512" and r["contact"] == "יוסי 03-5551234"
        assert "כמות קווים: 2" in r["notes"]
        assert "VPI/VCI: 0/35" in r["notes"]
        assert "מועד חיבור: 1/1/2000" in r["notes"]

    def test_quoted_header_alias(self):
        """'שם לקוח באפל'' (trailing gershayim) still hits the alias."""
        sm = _matrix("קוי-SDH-IPVPN", [
            ["סביבת חיבור", "מאתר", "שם לקוח באפל'", "קוד בבזק"],
            ["Lev", "Alenbi", "ClientX", "999"],
        ])
        recs, _ = parse_circuits(sm, 0)
        assert recs[0]["app_client_name"] == "ClientX"


class TestCertificatesParser:
    def test_extra_column_kept(self):
        sm = _matrix("תוקף תעודות", [
            ["platform", "target", "server", "cert", "expiry"],
            ["f5", "vs1", "srv1", "cert1", "47149", "מבוטל"],
        ])
        recs, _ = parse_certificates(sm, 0)
        assert recs[0]["cert_name"] == "cert1"
        assert recs[0]["notes"] == "מבוטל"


class TestAssetsParser:
    def test_unmapped_named_cols_to_notes(self):
        sm = _matrix("תוכנות וחומרות", [
            ["סוג", "חברה", "דגם", "logs", "service company"],
            ["חומרה", "HP", "dl380", "splunk", "bezeq"],
        ])
        recs, _ = parse_assets(sm, 0)
        assert "logs: splunk" in recs[0]["notes"]
        assert "service company: bezeq" in recs[0]["notes"]


class TestServersParser:
    def test_host_no_ip_record(self):
        sm = _matrix("שרתים בייצור", [
            ["Name", "Guest OS", "IP Address", "Cert", "License"],
            ["SRV-NOIP", "Linux", "", "certX", "licY"],
        ])
        recs, _ = parse_servers(sm, 0)
        assert recs[0]["kind"] == "host_no_ip"
        assert recs[0]["hostname"] == "SRV-NOIP"
        assert recs[0]["custom_fields"]["guest_os"] == "Linux"


# ---------------------------------------------------------------------------
# planner-level tests — DbState() is in-memory, no DB needed
# ---------------------------------------------------------------------------


def _plan(sheets):
    return _Planner(DbState(), PreviewOptions()).build(sheets)


def _preview_of(result, sheet):
    return next(s for s in result["sheets"] if s["sheet"] == sheet)


def _site_key_by_name(result, name):
    return next(s["key"] for s in result["plan"]["sites"] if s["name"] == name)


_MASTER_HEAD = ["Name", "Code", "type", "Subet range", "", "", "", "Subet", "הערות"]


def _master_row(name, code, *frags, notes=""):
    # subnet fragments occupy cols 3-6 (between 'type' and 'Subet')
    frags = list(frags) + [""] * (4 - len(frags))
    return [name, code, "", *frags, "255.255.255.0", notes]


class TestPlanSiteResolution:
    def test_non10x_sheet_matches_declared_block(self):
        """INTEGRATION: mostly 172.20/21.x + a few 10.10.x -> Integration
        Site via its master-declared blocks, not Eilat (site 10)."""
        sheets = [
            _matrix("רשימת אתרים", [
                _MASTER_HEAD,
                _master_row("Eilat Airport", "ELTA", "10", "10", ".0.", "0/24"),
                _master_row("Integration Site", "INT", "172", "20-21", "1"),
            ]),
            _matrix("INTEGRATION", [
                ["IP Address", "end ip", "Subnet mask", "Node Name"],
                ["172.20.1.", "1", "255.255.255.0", "a"],
                ["172.20.1.", "2", "255.255.255.0", "b"],
                ["172.21.1.", "3", "255.255.255.0", "c"],
                ["10.10.1.", "4", "255.255.255.0", "d"],
            ]),
        ]
        result = _plan(sheets)
        p = _preview_of(result, "INTEGRATION")
        assert p["site_name"] == "Integration Site" and p["matched_by"] == "octet"
        integ_key = _site_key_by_name(result, "Integration Site")
        assert all(a["vrf_key"] == integ_key for a in result["plan"]["addresses"])

    def test_under_site_ignores_digits_in_names(self):
        """'טרמינל 3 כניסה' must NOT reassign rows to site 3 — under_site
        matches names/codes; only a bare number counts."""
        sheets = [
            _matrix("רשימת אתרים", [
                _MASTER_HEAD,
                _master_row("Alenbi Mitanim", "ALNM", "10", "3", ".0.", "0/24"),
                _master_row("Natbag - USERS", "", "10", "193"),
            ]),
            _matrix("NTBG USers", [
                ["IP Address", "end ip", "Subnet mask", "Node Name", "מוגדר תחת אתר"],
                ["10.193.1.", "50", "255.255.255.0", "FW1", "טרמינל 3 כניסה"],
                ["10.193.1.", "51", "255.255.255.0", "FW2", "3"],  # bare number -> moves
            ]),
        ]
        result = _plan(sheets)
        natbag = _site_key_by_name(result, "Natbag - USERS")
        alenbi = _site_key_by_name(result, "Alenbi Mitanim")
        by_ip = {a["address"]: a["vrf_key"] for a in result["plan"]["addresses"]}
        assert by_ip["10.193.1.50"] == natbag
        assert by_ip["10.193.1.51"] == alenbi

    def test_under_site_matches_name(self):
        sheets = [
            _matrix("רשימת אתרים", [
                _MASTER_HEAD,
                _master_row("Alenbi", "ALNB", "10", "2", ".0.", "0/24"),
                _master_row("Ovda", "OVDA", "10", "29", ".0.", "0/24"),
            ]),
            _matrix("אלנבי", [
                ["IP Address", "end ip", "Subnet mask", "מוגדר תחת אתר"],
                ["10.2.1.", "50", "255.255.255.0", "Ovda"],
            ]),
        ]
        result = _plan(sheets)
        ovda = _site_key_by_name(result, "Ovda")
        assert result["plan"]["addresses"][0]["vrf_key"] == ovda

    def test_planned_site_name_match(self):
        """LEV_DR has no 10.x addresses — on a fresh DB it can only match a
        site planned earlier in the batch (code LEV -> Natbag)."""
        sheets = [
            _matrix("רשימת אתרים", [
                _MASTER_HEAD,
                _master_row("Natbag - SERVERS", "LEV", "10", "192", ".0.", "0/24"),
            ]),
            _matrix("LEV_DR 172.17.x.x", [
                ["IP Address", "end ip", "Subnet mask"],
                ["172.17.1.", "5", "255.255.255.0"],
            ]),
        ]
        result = _plan(sheets)
        p = _preview_of(result, "LEV_DR 172.17.x.x")
        assert p["site_name"] == "Natbag - SERVERS" and p["matched_by"] == "name"

    def test_word_boundary_no_substring(self):
        """'int' is a substring of 'maintenence' — word-boundary matching
        must NOT bind that sheet to Integration Site."""
        sheets = [
            _matrix("רשימת אתרים", [
                _MASTER_HEAD,
                _master_row("Integration Site", "INT", "172", "20-21", "1"),
            ]),
            _matrix("Maintenence REHVT", [
                ["IP Address", "end ip", "Subnet mask"],
                ["172.30.1.", "5", "255.255.255.0"],
            ]),
        ]
        result = _plan(sheets)
        p = _preview_of(result, "Maintenence REHVT")
        assert p["site_name"] == "Imported (unmatched)"

    def test_duplicate_site_number_conflict(self):
        """Mashapan TA + MATPASH share number 200 — merge + conflict, not
        a silent identity loss."""
        sheets = [
            _matrix("רשימת אתרים", [
                _MASTER_HEAD,
                _master_row("Mashapan TA", "", "10", "200", "248", "56"),
                _master_row("MATPASH", "", "10", "200"),
            ]),
        ]
        result = _plan(sheets)
        conflicts = [r for r in result["rows"] if r["action"] == "conflict"]
        assert any("MATPASH" in r["detail"] and "Mashapan" in r["detail"] for r in conflicts)
        sites200 = [s for s in result["plan"]["sites"] if s.get("site_number") == 200]
        assert len(sites200) == 1

    def test_same_code_different_number_conflict(self):
        """Tarkumia twice with code TAR (sites 32 + 51) — merges but is
        reported as a conflict, not a clean duplicate."""
        sheets = [
            _matrix("רשימת אתרים", [
                _MASTER_HEAD,
                _master_row("Tarkumia", "TAR", "10", "32", ".0.", "0/24", notes="לא פעיל"),
                _master_row("Tarkumia", "TAR", "10", "51", ".0.", "0/24"),
            ]),
        ]
        result = _plan(sheets)
        conflicts = [r for r in result["rows"] if r["action"] == "conflict"]
        assert any("Tarkumia" in r["detail"] for r in conflicts)

    def test_inactive_site_warning(self):
        sheets = [
            _matrix("רשימת אתרים", [
                _MASTER_HEAD,
                _master_row("Tarkumia", "TAR", "10", "32", ".0.", "0/24", notes="לא פעיל"),
            ]),
            _matrix("TRANSIT+ROTANDA", [
                ["IP Address", "end ip", "Subnet mask"],
                ["10.32.1.", "5", "255.255.255.0"],
            ]),
        ]
        result = _plan(sheets)
        p = _preview_of(result, "TRANSIT+ROTANDA")
        assert p["site_name"] == "Tarkumia"
        assert any("inactive" in w for w in p["warnings"])
        assert any("doesn't resemble" in w for w in p["warnings"])

    def test_anonymous_site_takes_sheet_title(self):
        """A sheet octet-matching a synthesized 'Site 35' claims its title —
        ג'למה becomes the site's real name."""
        sheets = [
            _matrix("רשימת אתרים", [
                _MASTER_HEAD,
                _master_row("", "", "10", "35"),
            ]),
            _matrix("ג'למה", [
                ["IP Address", "end ip", "Subnet mask"],
                ["10.35.1.", "5", "255.255.255.0"],
            ]),
        ]
        result = _plan(sheets)
        p = _preview_of(result, "ג'למה")
        assert p["site_name"] == "ג'למה" and p["matched_by"] == "octet"
        assert any(s["name"] == "ג'למה" for s in result["plan"]["sites"])
        assert not any(s["name"] == "Site 35" for s in result["plan"]["sites"])

    def test_holding_site_warning(self):
        sheets = [
            _matrix("רשימת אתרים", [_MASTER_HEAD]),
            _matrix("Nowhere Land", [
                ["IP Address", "end ip", "Subnet mask"],
                ["172.99.1.", "5", "255.255.255.0"],
            ]),
        ]
        result = _plan(sheets)
        p = _preview_of(result, "Nowhere Land")
        assert p["site_name"] == "Imported (unmatched)"
        assert any("no site match" in w for w in p["warnings"])

    def test_host_no_ip_becomes_asset(self):
        sheets = [
            _matrix("רשימת אתרים", [
                _MASTER_HEAD,
                _master_row("Natbag - SERVERS", "LEV", "10", "192", ".0.", "0/24"),
            ]),
            _matrix("שרתים בייצור", [
                ["Name", "Guest OS", "IP Address", "Cert", "License"],
                ["SRV-NOIP", "Linux", "", "certX", "licY"],
                ["SRV-IP", "Win", "10.192.1.5", "", ""],
            ]),
        ]
        result = _plan(sheets)
        assets = [a for a in result["plan"]["assets"] if a.get("category") == "server"]
        assert len(assets) == 1
        assert assets[0]["model"] == "SRV-NOIP"
        assert "certX" in (assets[0]["notes"] or "")

    def test_mask_raw_preserved_on_fallback(self):
        sheets = [
            _matrix("רשימת אתרים", [
                _MASTER_HEAD,
                _master_row("Alenbi", "ALNB", "10", "2", ".0.", "0/24"),
            ]),
            _matrix("אלנבי", [
                ["IP Address", "end ip", "Subnet mask", "Node Name"],
                ["10.2.1.", "50", "edge-meches", "SRV1"],
            ]),
        ]
        result = _plan(sheets)
        addr = result["plan"]["addresses"][0]
        assert addr["address"] == "10.2.1.50"
        assert addr["custom_fields"]["mask_raw"] == "edge-meches"


class TestSiteSheetExtras:
    def test_mac_address_header_alias(self):
        """'MAC ADDRESS' (חיפה נמל / HAf old) is a mac column, not cf."""
        sm = _matrix("s", [
            ["IP Address", "end ip", "Subnet mask", "MAC ADDRESS"],
            ["10.2.1.", "81", "255.255.255.0", "00-02-E3-30-C3-DF"],
        ])
        recs, _ = parse_site_sheet(sm, 0)
        assert recs[0]["mac"] == "00:02:E3:30:C3:DF"

    def test_name_header_alias(self):
        """Bare 'Name' (Cellular) maps to the hostname field."""
        sm = _matrix("Cellular", [
            ["Name", "IP", "Mask"],
            ["FW_FE_Lev1", "10.129.67.211", "255.255.255.240"],
        ])
        recs, _ = parse_site_sheet(sm, 0)
        assert recs[0]["hostname"] == "FW_FE_Lev1"

    def test_unnamed_columns_preserved(self):
        """Non-empty unnamed columns pile into cf['extra'] instead of
        vanishing (Pelephone carrier, אתר סלולרי labels…)."""
        sm = _matrix("Cellular", [
            ["IP Address", "end ip", "Subnet mask", "Node Name", "", ""],
            ["10.129.67.", "209", "255.255.255.240", "FW1", "Pelephone", "אתר סלולרי"],
        ])
        recs, _ = parse_site_sheet(sm, 0)
        extra = recs[0]["custom_fields"]["extra"]
        assert "Pelephone" in extra and "אתר סלולרי" in extra

    def test_yes_no_ping_junk_still_dropped(self):
        sm = _matrix("s", [
            ["IP Address", "end ip", "Subnet mask", ""],
            ["10.2.1.", "81", "255.255.255.0", "yes"],
        ])
        recs, _ = parse_site_sheet(sm, 0)
        assert not recs[0]["custom_fields"]


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
