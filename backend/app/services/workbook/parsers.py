"""Per-family sheet parsers -> normalized record dicts.

Every parser takes (SheetMatrix, header_row_idx) and returns
(records, warnings). Records carry `sheet`/`row` for the report; unparsed
cell values land in custom_fields rather than being dropped.
"""
import re

from app.services.workbook import normalize as nz

# canonical field -> header aliases (normalized via norm_header)
_SITE_COLS = {
    "ip": {"ip address", "ip", "כתובת", "כתובת ip"},
    "end": {"end ip", "end", "endip"},
    "mask": {"subnet mask", "subnet", "subet", "mask"},
    "gateway": {"defult gatway", "default gateway", "gatway", "gateway", "dg"},
    "vlan": {"vlan/lan", "vlan", "lan"},
    "node": {"node name", "server name", "hostname", "host"},
    "counter": {"counter/location", "location", "מס דלפק באפלקציה"},
    "mac": {"mac"},
    "model": {"model"},
    "description": {"description", "discription", "desc", "תיאור"},
    "serial": {"serial number", "serial", "s.n", "sn"},
    "switch": {"switch"},
    "port": {"port"},
    "under_site": {"מוגדר תחת אתר"},
    "notes": {"הערות", "remarks", "הערה"},
    "env": {"env"},
    "lev_dr": {"lev/dr"},
}

# positional fallback for headerless site sheets (100_* style)
_SITE_POSITIONAL = ["ip", "end", "mask", "vlan", "node", "mac", "model", "description"]


def _map_columns(header_row) -> dict[str, list[int]]:
    """canonical field -> column indexes (multi-index for duplicated blocks)."""
    mapping: dict[str, list[int]] = {}
    for i, cell in enumerate(header_row):
        h = nz.norm_header(cell)
        if not h:
            continue
        for canon, aliases in _SITE_COLS.items():
            if h in aliases:
                mapping.setdefault(canon, []).append(i)
                break
    # many sheets leave the 'end ip' header cell blank — the canonical layout
    # always places it immediately right of the IP column
    if "ip" in mapping and "end" not in mapping:
        ip_i = mapping["ip"][0]
        if ip_i + 1 < len(header_row) and not nz.clean(header_row[ip_i + 1]):
            mapping["end"] = [ip_i + 1]
    return mapping


def _positional_columns(sheet) -> dict[str, list[int]]:
    """Headerless sheet: find the IP-fragment column, map the canonical
    layout starting there (100_* has a leading empty col)."""
    frag_re = re.compile(r"^\d{1,3}\.\d{1,3}(?:\.\d{1,3})?\.?$")
    best, best_n = -1, 0
    for ci in range(4):
        n = sum(
            1
            for r in sheet.rows[:30]
            if ci < len(r) and frag_re.match(nz.clean(r[ci]))
        )
        if n > best_n:
            best, best_n = ci, n
    if best < 0:
        return {}
    cols: dict[str, list[int]] = {}
    offset = 0
    # a column left of the IP column is always empty decoration in this file
    for name in _SITE_POSITIONAL:
        cols[name] = [best + offset]
        offset += 1
    return cols


def _blocks(mapping: dict[str, list[int]]) -> list[dict[str, int]]:
    """Split duplicated column groups (031-style runaway): each block starts
    at an 'ip' column and runs until the next 'ip' column."""
    ip_cols = sorted(mapping.get("ip", []))
    if not ip_cols:
        return []
    if len(ip_cols) == 1:
        return [{k: v[0] for k, v in mapping.items() if v}]
    blocks = []
    for bi, start in enumerate(ip_cols):
        end = ip_cols[bi + 1] if bi + 1 < len(ip_cols) else 10**9
        block = {}
        for k, idxs in mapping.items():
            inside = [i for i in idxs if start <= i < end]
            if inside:
                block[k] = inside[0]
        blocks.append(block)
    return blocks


def _is_header_echo(row, block: dict[str, int]) -> bool:
    ip_idx = block.get("ip")
    if ip_idx is None or ip_idx >= len(row):
        return False
    return nz.norm_header(row[ip_idx]) in _SITE_COLS["ip"]


def parse_site_sheet(sheet, hidx: int) -> tuple[list[dict], list[str]]:
    warnings: list[str] = []
    if hidx >= 0:
        mapping = _map_columns(sheet.rows[hidx])
    else:
        mapping = _positional_columns(sheet)
    if "ip" not in mapping:
        return [], ["no IP column recognized"]

    blocks = _blocks(mapping)
    if len(blocks) > 1:
        warnings.append(f"{len(blocks)} duplicated column blocks detected — all parsed")

    header_names = (
        {i: nz.clean(c) for i, c in enumerate(sheet.rows[hidx]) if nz.clean(c)}
        if hidx >= 0
        else {}
    )
    used_idx = {i for b in blocks for i in b.values()}

    records: list[dict] = []
    start = hidx + 1 if hidx >= 0 else 0
    prev_base = ""
    for ri, row in enumerate(sheet.rows[start:], start=start + 1):
        if not any(nz.clean(c) for c in row):
            continue
        for bi, block in enumerate(blocks):
            if _is_header_echo(row, block):
                continue
            rec = _site_row(sheet.name, ri, row, block, header_names, used_idx, prev_base)
            if rec is None:
                continue
            # only IP-shaped bases carry forward to continuation rows
            nb = rec.pop("_base", None)
            if nb and re.match(r"^\d{1,3}\.\d{1,3}", nb):
                prev_base = nb
            records.append(rec)
    return records, warnings


def _site_row(sheet, ri, row, block, header_names, used_idx, prev_base):
    def cell(field):
        idx = block.get(field)
        return row[idx] if idx is not None and idx < len(row) else None

    base = nz.clean(cell("ip")) or prev_base  # carry-forward base (016/018)
    end = nz.clean(cell("end"))
    ip = nz.assemble_ip(base, end)
    rng = nz.parse_range_end(base, end)
    if ip is None and rng is None:
        raw_ip = nz.clean(cell("ip"))
        if raw_ip or end:
            octs = raw_ip.rstrip(".").split(".")
            if all(o.isdigit() for o in octs) and len(octs) == 3:
                # 3-octet fragment w/o a last octet — a subnet declaration
                return {
                    "sheet": sheet, "row": ri, "kind": "subnet",
                    "network_base": raw_ip.rstrip("."),
                    "mask": nz.clean(cell("mask")),
                    "description": nz.clean(cell("description")) or None,
                    "_base": base,
                }
            if re.match(r"^\d{1,3}\.", raw_ip):
                return {
                    "sheet": sheet, "row": ri, "kind": "invalid",
                    "detail": f"unparseable address: {raw_ip!r} + {end!r}",
                    "_base": base,
                }
            # non-IP text in the IP column — section header / label row;
            # don't carry it forward as the base for continuation rows
            return {
                "sheet": sheet, "row": ri, "kind": "skip",
                "detail": f"non-IP row: {raw_ip[:60] or end[:60]!r}",
                "_base": prev_base,
            }
        return None

    cf: dict = {}
    # unmapped, non-empty named columns -> custom_fields (junk cols dropped
    # when the header is empty and no mapped sibling uses the slot)
    for i, v in enumerate(row):
        s = nz.clean(v)
        if not s or i in used_idx or i in (block.get("ip"), block.get("end")):
            continue
        name = header_names.get(i)
        if name:
            cf[name[:64]] = s[:255]
        elif s.lower() in ("yes", "no ping"):
            continue  # known junk markers
    for f in ("env", "lev_dr", "gateway"):
        s = nz.clean(cell(f))
        if s:
            cf[f] = s

    mac_raw = nz.clean(cell("mac"))
    # only treat a field as a status when it actually contains a known
    # status keyword — plain Hebrew descriptions are not statuses
    status_text = ""
    for f in ("notes", "description"):
        s = nz.clean(cell(f))
        if s and nz.status_of(s) is not None:
            status_text = s
            break
    rec = {
        "sheet": sheet,
        "row": ri,
        "kind": "range" if rng else "address",
        "address": ip,
        "range": rng,
        "mask": nz.clean(cell("mask")),
        "vlan_vid": None,
        "vlan_name": None,
        "hostname": nz.clean(cell("node"))[:255] or None,
        "mac": nz.norm_mac(mac_raw),
        "mac_raw": mac_raw if nz.norm_mac(mac_raw) is None and mac_raw else None,
        "model": nz.clean(cell("model"))[:255] or None,
        "description": nz.clean(cell("description")) or None,
        "serial": nz.clean(cell("serial"))[:128] or None,
        "switch": nz.clean(cell("switch"))[:255] or None,
        "port": nz.clean(cell("port"))[:64] or None,
        "counter": nz.clean(cell("counter"))[:255] or None,
        "under_site": nz.clean(cell("under_site")) or None,
        "notes": nz.clean(cell("notes")) or None,
        "status_text": status_text,
        "custom_fields": cf,
        "_base": base,
    }
    vid, vname = nz.parse_vlan(nz.clean(cell("vlan")))
    rec["vlan_vid"], rec["vlan_name"] = vid, vname
    return rec


def parse_sites_master(sheet, hidx: int) -> tuple[list[dict], list[str]]:
    header = [nz.norm_header(c) for c in sheet.rows[hidx]]
    idx = {h: i for i, h in enumerate(header) if h}

    def col(row, *names):
        for n in names:
            i = idx.get(n)
            if i is not None and i < len(row):
                s = nz.clean(row[i])
                if s:
                    return s
        return ""

    records = []
    for ri, row in enumerate(sheet.rows[hidx + 1 :], start=hidx + 2):
        name = col(row, "name")
        if not name:
            continue
        # subnet fragments live in the columns between 'type' and the mask
        # column ('subet'): '10','2','.0.','0/24' -> '10.2.0.0/24'
        i_type = idx.get("type")
        i_subet = idx.get("subet")
        lo = (i_type + 1) if i_type is not None else 3
        hi = i_subet if i_subet is not None else len(row)
        frags = [
            nz.clean(row[i])
            for i in range(lo, min(hi, len(row)))
            if nz.clean(row[i])
        ]
        cidr = ""
        if frags:
            joined = frags[0]
            for p in frags[1:]:
                joined += p if joined.endswith(".") or p.startswith(".") else "." + p
            if "/" not in joined:
                joined += "/24"
            if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2}$", joined):
                cidr = joined
        notes = col(row, "הערות")
        number = None
        if cidr:
            try:
                number = int(cidr.split(".")[1])
            except (IndexError, ValueError):
                pass
        records.append(
            {
                "sheet": sheet.name,
                "row": ri,
                "name": name[:255],
                "code": col(row, "code")[:16] or None,
                "size": col(row, "type")[:32] or None,
                "site_number": number,
                "cidr": cidr or None,
                "mask": col(row, "subet") or None,
                "notes": notes or None,
                "is_active": "לא פעיל" not in notes,
            }
        )
    return records, []


def parse_circuits(sheet, hidx: int) -> tuple[list[dict], list[str]]:
    header = [nz.norm_header(c) for c in sheet.rows[hidx]]
    aliases = {
        "env": {"סביבת חיבור"},
        "site_name": {"מאתר"},
        "site_type": {"סוג האתר"},
        "site_number": {"מספר אתר"},
        "site_code": {"קידומת האתר"},
        "line_type": {"סוג הקו"},
        "bezeq_circuit_id": {"קוד בבזק"},
        "node": {"צומת"},
        "bw_down": {"רוחב פס download"},
        "bw_up": {"רוחב פס upload"},
        "wan_ip": {"כתובת wan"},
        "app_client_num": {"מספר קוד באפלקציה"},
        "app_client_name": {"שם לקוח באפל"},
        "app_service_type": {"סוג שירות באפלקציה"},
        "contact": {"איש קשר וכתובת האתר"},
        "notes": {"הערות"},
    }
    idx = {}
    for f, names in aliases.items():
        for i, h in enumerate(header):
            if h in names:
                idx[f] = i
                break

    records = []
    for ri, row in enumerate(sheet.rows[hidx + 1 :], start=hidx + 2):
        if not any(nz.clean(c) for c in row):
            continue

        def cell(f):
            i = idx.get(f)
            return nz.clean(row[i]) if i is not None and i < len(row) else ""

        bezeq_i = idx.get("bezeq_circuit_id")
        if bezeq_i is not None and bezeq_i < len(row) and nz.norm_header(row[bezeq_i]) == "קוד בבזק":
            continue
        wan = cell("wan_ip")
        rec = {
            "sheet": sheet.name,
            "row": ri,
            "env": cell("env")[:64] or None,
            "site_name": cell("site_name")[:255] or None,
            "site_number": nz.parse_site_number(cell("site_number")),
            "site_code": cell("site_code")[:16] or None,
            "line_type": cell("line_type").lower()[:32] or None,
            "bezeq_circuit_id": cell("bezeq_circuit_id")[:64] or None,
            "node": cell("node")[:64] or None,
            "bw_down": cell("bw_down")[:32] or None,
            "bw_up": cell("bw_up")[:32] or None,
            "wan_ip": wan if nz.assemble_ip(wan) else None,
            "app_client_num": cell("app_client_num")[:64] or None,
            "app_client_name": cell("app_client_name")[:255] or None,
            "app_service_type": cell("app_service_type")[:255] or None,
            "contact": cell("contact") or None,
            "status": cell("site_type")[:64] or None,
            "notes": cell("notes") or None,
        }
        if wan and rec["wan_ip"] is None:
            rec["notes"] = (rec["notes"] or "") + f" [wan_ip raw: {wan}]"
        # legacy format (029) and footer rows produce all-empty records
        if not any(rec[f] for f in ("bezeq_circuit_id", "site_name", "node", "wan_ip")):
            continue
        records.append(rec)
    return records, []


def parse_certificates(sheet, hidx: int) -> tuple[list[dict], list[str]]:
    """Positional 5-col layout: platform, target/VS, server, cert, expiry."""
    records = []
    for ri, row in enumerate(sheet.rows[hidx + 1 :], start=hidx + 2):
        vals = [row[i] if i < len(row) else None for i in range(5)]
        if not any(nz.clean(v) for v in vals):
            continue
        platform, target, server, cert, expiry = vals
        raw = nz.clean(expiry)
        records.append(
            {
                "sheet": sheet.name,
                "row": ri,
                "platform": nz.clean(platform)[:64] or None,
                "target": nz.clean(target)[:255] or None,
                "server_name": nz.clean(server)[:255] or None,
                "cert_name": nz.clean(cert)[:255] or None,
                "expires_on": nz.excel_date(expiry).isoformat()
                if nz.excel_date(expiry)
                else None,
                "serial_raw": raw[:64] or None,
            }
        )
    return records, []


def parse_services(sheet, hidx: int) -> tuple[list[dict], list[str]]:
    header = [nz.norm_header(c) for c in sheet.rows[hidx]]
    aliases = {
        "seq": {"מס' סידורי"},
        "name": {"שם השירות"},
        "beneficiary": {"מי הגורם שנהנה מהשירות"},
        "site_code": {"שייך לקוד אתר"},
        "doc_path": {"מיקום קובץ/תיקייה מפורט"},
        "notes": {"תיאור קצר"},
        "test_info": {"בדיקת תקינות"},
    }
    idx = {}
    for f, names in aliases.items():
        for i, h in enumerate(header):
            if h in names:
                idx[f] = i
                break

    records = []
    for ri, row in enumerate(sheet.rows[hidx + 1 :], start=hidx + 2):
        if not any(nz.clean(c) for c in row):
            continue

        def cell(f):
            i = idx.get(f)
            return nz.clean(row[i]) if i is not None and i < len(row) else ""

        name = cell("name")
        if not name:
            continue
        records.append(
            {
                "sheet": sheet.name,
                "row": ri,
                "name": name[:255],
                "beneficiary": cell("beneficiary")[:255] or None,
                "site_code": cell("site_code")[:16] or None,
                "doc_path": cell("doc_path") or None,
                "test_info": cell("test_info") or None,
                "notes": cell("notes") or None,
            }
        )
    return records, []


def parse_assets(sheet, hidx: int) -> tuple[list[dict], list[str]]:
    """003 תוכנות וחומרות: סוג,חברה,דגם,שם התוכנה,ייעוד,גירסה,EOL,…"""
    header = [nz.norm_header(c) for c in sheet.rows[hidx]]
    aliases = {
        "kind": {"סוג"},
        "vendor": {"חברה"},
        "model": {"דגם"},
        "sw_name": {"שם התוכנה"},
        "purpose": {"ייעוד"},
        "version": {"גירסה"},
        "eol": {"eol"},
        "support": {"חברה תומכת"},
        "contact": {"שם איש סיסטם"},
    }
    idx = {}
    for f, names in aliases.items():
        for i, h in enumerate(header):
            if h in names:
                idx[f] = i
                break

    records = []
    for ri, row in enumerate(sheet.rows[hidx + 1 :], start=hidx + 2):
        if not any(nz.clean(c) for c in row):
            continue

        def cell(f):
            i = idx.get(f)
            return row[i] if i is not None and i < len(row) else None

        kind_raw = nz.clean(cell("kind"))
        eol_cell = cell("eol")
        notes_bits = [
            b
            for b in (nz.clean(cell("contact")), nz.clean(cell("sw_name")))
            if b
        ]
        records.append(
            {
                "sheet": sheet.name,
                "row": ri,
                "kind": "software" if "תוכנה" in kind_raw else "hardware",
                "category": kind_raw[:64] or None,
                "vendor": nz.clean(cell("vendor"))[:255] or None,
                "model": nz.clean(cell("model"))[:255] or None,
                "purpose": nz.clean(cell("purpose"))[:255] or None,
                "version": nz.clean(cell("version"))[:128] or None,
                "eol_on": nz.excel_date(eol_cell).isoformat()
                if nz.excel_date(eol_cell)
                else None,
                "support_status": nz.clean(cell("support"))[:128] or None,
                "serial_number": None,
                "site_name": None,
                "notes": " | ".join(notes_bits) or None,
            }
        )
    return records, []


def parse_inventory(sheet, hidx: int) -> tuple[list[dict], list[str]]:
    """105/106 serial-number lists -> hardware assets."""
    header = [nz.norm_header(c) for c in sheet.rows[hidx]]
    joined = set(header)
    records = []
    if "device" in joined:  # 105: Serial Number, Version, Device
        i_serial = header.index("serial number")
        i_ver = header.index("version") if "version" in joined else None
        i_dev = header.index("device")
        for ri, row in enumerate(sheet.rows[hidx + 1 :], start=hidx + 2):
            serial = nz.clean(row[i_serial] if i_serial < len(row) else None)
            if not serial:
                continue
            records.append(
                {
                    "sheet": sheet.name,
                    "row": ri,
                    "kind": "hardware",
                    "category": "switch",
                    "serial_number": serial[:128],
                    "model": nz.clean(row[i_ver] if i_ver is not None and i_ver < len(row) else None)[:255] or None,
                    "purpose": nz.clean(row[i_dev] if i_dev < len(row) else None)[:255] or None,
                    "vendor": None, "version": None, "eol_on": None,
                    "support_status": None, "site_name": None, "notes": None,
                }
            )
    else:  # 106: Site, Hostname, Serial Numbers (blob w/ 'PCB Serial : X')
        i_site = next((i for i, h in enumerate(header) if h.startswith("site")), 0)
        i_host = next((i for i, h in enumerate(header) if "hostname" in h), 1)
        i_ser = next((i for i, h in enumerate(header) if "serial" in h), 2)
        cur_site = ""
        for ri, row in enumerate(sheet.rows[hidx + 1 :], start=hidx + 2):
            site = nz.clean(row[i_site] if i_site < len(row) else None) or cur_site
            cur_site = site
            host = nz.clean(row[i_host] if i_host < len(row) else None)
            blob = row[i_ser] if i_ser < len(row) else None
            for serial in nz.split_serial_blob(blob):
                records.append(
                    {
                        "sheet": sheet.name,
                        "row": ri,
                        "kind": "hardware",
                        "category": "router",
                        "serial_number": serial[:128],
                        "model": host[:255] or None,
                        "purpose": host[:255] or None,
                        "site_name": site or None,
                        "vendor": None, "version": None, "eol_on": None,
                        "support_status": None, "notes": None,
                    }
                )
    return records, []


def parse_servers(sheet, hidx: int) -> tuple[list[dict], list[str]]:
    """002 שרתים בייצור: Name, Guest OS, IP Address(multi), Cert, License, owner."""
    header = [nz.norm_header(c) for c in sheet.rows[hidx]]
    i_name = header.index("name") if "name" in header else 0
    i_os = next((i for i, h in enumerate(header) if "guest os" in h), None)
    i_ip = next((i for i, h in enumerate(header) if h in _SITE_COLS["ip"]), None)
    i_cert = next((i for i, h in enumerate(header) if "cert" in h), None)
    i_lic = next((i for i, h in enumerate(header) if "license" in h), None)
    if i_ip is None:
        return [], ["no IP column in servers sheet"]

    records = []
    for ri, row in enumerate(sheet.rows[hidx + 1 :], start=hidx + 2):
        name = nz.clean(row[i_name] if i_name < len(row) else None)
        if not name:
            continue
        ips, linklocal = nz.split_multi_ip(nz.clean(row[i_ip] if i_ip < len(row) else None))
        cf = {}
        for f, i in (("guest_os", i_os), ("cert", i_cert), ("license", i_lic)):
            if i is not None and i < len(row):
                s = nz.clean(row[i])
                if s:
                    cf[f] = s
        # trailing unnamed column holds the owner name (רומן/אנגלינה…)
        last = nz.clean(row[-1]) if row else ""
        if last and last not in header and len(row) > max(i_ip or 0, i_cert or 0):
            cf["owner"] = last
        if linklocal:
            cf["other_ips"] = linklocal
        if not ips:
            records.append(
                {
                    "sheet": sheet.name, "row": ri, "kind": "host_no_ip",
                    "hostname": name[:255], "custom_fields": cf,
                }
            )
            continue
        for n, ip in enumerate(ips):
            records.append(
                {
                    "sheet": sheet.name,
                    "row": ri,
                    "kind": "address",
                    "address": ip,
                    "range": None,
                    "mask": "",
                    "vlan_vid": None,
                    "vlan_name": None,
                    "hostname": name[:255] + (f" (ip{n + 1})" if n else ""),
                    "mac": None, "mac_raw": None, "model": None,
                    "description": None, "serial": None, "switch": None,
                    "port": None, "counter": None, "under_site": None,
                    "notes": None, "status_text": "",
                    "custom_fields": dict(cf),
                }
            )
    return records, []


PARSERS = {
    "sites_master": parse_sites_master,
    "circuits": parse_circuits,
    "certificates": parse_certificates,
    "services": parse_services,
    "assets": parse_assets,
    "inventory": parse_inventory,
    "servers": parse_servers,
    "site_sheet": parse_site_sheet,
}
