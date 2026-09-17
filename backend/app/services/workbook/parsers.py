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
    "node": {"node name", "server name", "hostname", "host", "name"},
    "counter": {"counter/location", "location", "מס דלפק באפלקציה"},
    "mac": {"mac", "mac address", "mac-address", "mac add"},
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


_FRAG_RE = re.compile(r"^\d{1,3}(?:\.\d{1,3}){1,3}\.?$")
_MASK_RE = re.compile(r"^255\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
_VLANISH_RE = re.compile(r"^(vlan\s*\d*|loopback|\d+\s*bit|lan|mgmt|users?)$", re.I)
_MACISH_RE = re.compile(r"^[0-9A-Fa-f]{2}([:\-.][0-9A-Fa-f]{2,4}){2,5}$")


_MODELISH_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_./+\-]{1,30}$")


def _col_class(values: list[str]) -> str:
    """Dominant content class of a column sample."""
    vals = [v for v in values if v]
    if not vals:
        return "empty"
    def frac(pred):
        return sum(1 for v in vals if pred(v)) / len(vals)
    if frac(lambda v: bool(_MASK_RE.match(v))) > 0.5:
        return "mask"
    if frac(lambda v: bool(_MACISH_RE.match(v))) > 0.5:
        return "mac"
    if frac(lambda v: bool(_VLANISH_RE.match(v))) > 0.5:
        return "vlan"
    if frac(lambda v: bool(_FRAG_RE.match(v))) > 0.5:
        return "ip"
    # short ASCII tokens (hostnames, model names) vs free text/Hebrew notes
    if frac(lambda v: bool(_MODELISH_RE.match(v))) > 0.5:
        return "modelish"
    return "text"


_ENDISH_RE = re.compile(r"^\d{1,3}$")


def _positional_columns(sheet) -> dict[str, list[int]]:
    """Headerless sheet: locate the IP column, then assign the remaining
    canonical fields by column CONTENT, not fixed offsets — sheets deviate
    from the canonical layout (034 drops the VLAN column, 031 adds a pad
    column, 063 carries full IPs)."""
    def _is_ipfrag(v: str) -> bool:
        # a mask column (255.x.x.x) must never be mistaken for the IP column
        return bool(_FRAG_RE.match(v)) and not _MASK_RE.match(v)

    best, best_score = -1, -1.0
    for ci in range(4):
        frag = sum(
            1
            for r in sheet.rows[:30]
            if ci < len(r) and _is_ipfrag(nz.clean(r[ci]))
        )
        if frag == 0:
            continue
        # the 'end ip' slot sits directly right: a column of bare last
        # octets is the signature of the split-base layout
        end_n = sum(
            1
            for r in sheet.rows[:30]
            if ci + 1 < len(r) and _ENDISH_RE.match(nz.clean(r[ci + 1]))
        )
        score = frag + min(end_n, frag) * 0.5
        if score > best_score:
            best, best_score = ci, score
    if best < 0:
        return {}

    cols: dict[str, list[int]] = {"ip": [best]}
    # the 'end ip' slot sits directly right — but only claim it when the
    # column really holds bare octets; on full-IP sheets (063) that column
    # may be a mask and must stay available for content classification
    if best + 1 < 12:
        nxt = [nz.clean(r[best + 1]) for r in sheet.rows[:30] if best + 1 < len(r)]
        filled = [v for v in nxt if v]
        if not filled or sum(1 for v in filled if _ENDISH_RE.match(v)) / len(filled) > 0.5:
            cols["end"] = [best + 1]

    # classify the next columns by content and fill canonical slots in order
    classes = {}
    for ci in range(best + 2, min(best + 9, 12)):
        sample = [
            nz.clean(r[ci]) for r in sheet.rows[:30] if ci < len(r)
        ]
        classes[ci] = _col_class(sample)

    taken = {best} | set(cols.get("end", []))
    def take(*want: str) -> int | None:
        for ci in sorted(classes):
            if ci in taken or classes[ci] not in want:
                continue
            taken.add(ci)
            return ci
        return None

    for field, want in (
        ("mask", ("mask",)), ("vlan", ("vlan",)),
        ("node", ("modelish", "text")), ("mac", ("mac",)),
        ("model", ("modelish",)), ("description", ("text", "modelish")),
    ):
        ci = take(*want)
        if ci is not None:
            cols[field] = [ci]
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
        if "ip" not in mapping:
            # blank 'IP Address' header cell (035/037): keep the named
            # columns, take ip/end positionally
            pos = _positional_columns(sheet)
            for f in ("ip", "end"):
                if f in pos:
                    mapping[f] = pos[f]
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
    # unmapped, non-empty columns -> custom_fields. Named columns keep their
    # header as the key; unnamed ones pile into a deduped 'extra' string so
    # real data (ISP names, serial blobs, notes) survives instead of
    # vanishing — 'yes'/'no ping' are known junk markers.
    extra: list[str] = []
    for i, v in enumerate(row):
        s = nz.clean(v)
        if not s or i in used_idx or i in (block.get("ip"), block.get("end")):
            continue
        name = header_names.get(i)
        if name:
            cf[name[:64]] = s[:255]
        elif s.lower() in ("yes", "no ping"):
            continue  # known junk markers
        elif s not in extra:
            extra.append(s)
    if extra:
        cf["extra"] = " | ".join(extra)[:1000]
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
    if vname and (
        _MASK_RE.match(vname) or _FRAG_RE.match(vname)
        or re.match(r"(?i)^(loopback\d*|\d+\s*bit)$", vname)
        or (" " in vname and re.search(r"[֐-׿]", vname))
    ):
        # link-type labels ('loopback', '30bit'), stray masks and Hebrew
        # note sentences are not VLANs — keep the raw text instead of
        # fabricating a VLAN record
        cf.setdefault("vlan_raw", vname)
        vid, vname = None, None
    rec["vlan_vid"], rec["vlan_name"] = vid, vname
    return rec


_RANGE_FRAG_RE = re.compile(r"^(\d{1,3})\s*-\s*(\d{1,3})$")
# 'היה "מטה ארצי" בעבר' — "was X formerly" — the only identity an anonymous
# master row carries
_FORMER_RE = re.compile(r"היה\s+[\"'״]?([^\"'״]+?)[\"'״]?\s+בעבר")


def _leftover_bits(row, header_row, used: set[int]) -> list[str]:
    """'header: value' strings for named columns no field claimed — keeps
    legacy/extra columns (VPI/VCI, כמות קווים, logs …) in notes instead of
    dropping them. '#' row-number columns are skipped."""
    out = []
    for ci, c in enumerate(row):
        if ci in used:
            continue
        s = nz.clean(c)
        h = nz.clean(header_row[ci]) if ci < len(header_row) else ""
        if s and h and h != "#":
            out.append(f"{h}: {s}")
    return out


def _master_blocks(frags: list[str], cidr: str) -> set[tuple[int, int]]:
    """(first, second) octet pairs a master row declares — lets sheet->site
    matching work outside the 10.x plan (e.g. Integration Site's 172.20-21.x).
    A lone leading fragment or a '0'/'x' second fragment means the '10' prefix
    was simply omitted ('46,0,x' -> 10.46)."""
    if cidr:
        a, b = cidr.split(".")[:2]
        return {(int(a), int(b))}
    if not frags or not frags[0].isdigit():
        return set()
    if frags[0] == "10":
        if len(frags) >= 2 and frags[1].isdigit():
            return {(10, int(frags[1]))}
        if len(frags) == 1 or frags[1] in ("0", "x"):
            return {(10, 10)}
        return set()
    if len(frags) == 1 or frags[1] in ("0", "x"):
        return {(10, int(frags[0]))}
    m = _RANGE_FRAG_RE.match(frags[1])
    if m:
        lo, hi = int(m.group(1)), int(m.group(2))
        return {(int(frags[0]), n) for n in range(lo, min(hi, lo + 64) + 1)}
    if frags[1].isdigit():
        return {(int(frags[0]), int(frags[1]))}
    return set()


def parse_sites_master(sheet, hidx: int) -> tuple[list[dict], list[str]]:
    header = [nz.norm_header(c) for c in sheet.rows[hidx]]
    idx = {h: i for i, h in enumerate(header) if h}

    def col(row, *names):
        # the header row can repeat a name ('הערות' twice) — scan all matches
        # so the first non-empty value wins instead of the last column's
        for n in names:
            for i, h in enumerate(header):
                if h == n and i < len(row):
                    s = nz.clean(row[i])
                    if s:
                        return s
        return ""

    records = []
    for ri, row in enumerate(sheet.rows[hidx + 1 :], start=hidx + 2):
        if not any(nz.clean(c) for c in row):
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
                # site_number is only meaningful inside the 10.x plan —
                # a non-10 CIDR must not claim a 10.{N} slot
                if cidr.split(".")[0] == "10":
                    number = int(cidr.split(".")[1])
            except (IndexError, ValueError):
                pass
        elif frags and frags[0].isdigit() and (
            frags[0] == "10" or len(frags) == 1 or frags[1] in ("0", "x")
        ):
            # partial subnet ('10,86' / ',87' / ',46,0,x' with no full CIDR)
            # — the site number IS the second octet in this address plan;
            # a lone leading fragment is that octet itself. A non-10 leading
            # fragment (Integration's '172,20-21,1') carries no site_number.
            if frags[0] == "10" and len(frags) >= 2 and frags[1].isdigit():
                number = int(frags[1])
            elif len(frags) == 1 or frags[1] in ("0", "x"):
                number = int(frags[0])
        name = col(row, "name")
        synthetic = False
        if not name:
            # nameless rows still carry a block + notes — keep them under a
            # synthesized name instead of losing the site (10.22/35/37/39).
            # 'היה "X" בעבר' notes carry the site's former name — use it,
            # suffixed so it can't collide with the real site that took over.
            former = _FORMER_RE.search(notes or "")
            if former:
                name = f"{former.group(1).strip()} (לשעבר)"
            elif number is not None:
                name = f"Site 10.{number}"
            elif cidr:
                name = f"Site {cidr.split('/')[0]}"
            else:
                continue
            synthetic = True
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
                "blocks": _master_blocks(frags, cidr),
                "synthetic_name": synthetic,
            }
        )
    return records, []


def parse_circuits(sheet, hidx: int) -> tuple[list[dict], list[str]]:
    header = [nz.norm_header(c) for c in sheet.rows[hidx]]
    aliases = {
        "env": {"סביבת חיבור"},
        "site_name": {"מאתר"},
        "site_type": {"סוג האתר", "סוג אתר"},
        "site_number": {"מספר אתר"},
        "site_code": {"קידומת האתר"},
        "line_type": {"סוג הקו"},
        "bezeq_circuit_id": {"קוד בבזק"},
        "node": {"צומת"},
        "bw_down": {"רוחב פס download", "רוחב פס"},
        "bw_up": {"רוחב פס upload"},
        "wan_ip": {"כתובת wan"},
        "app_client_num": {"מספר קוד באפלקציה"},
        "app_client_name": {"שם לקוח באפל", "שם לקוח באפלקציה"},
        "app_service_type": {"סוג שירות באפלקציה"},
        "contact": {"איש קשר וכתובת האתר", "איש קשר", "הערות + איש קשר"},
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
            "notes": " | ".join(
                b
                for b in (cell("notes"), *_leftover_bits(row, sheet.rows[hidx], set(idx.values())))
                if b
            )
            or None,
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
        extra = [nz.clean(row[i]) for i in range(5, len(row)) if nz.clean(row[i])]
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
                "notes": " | ".join(extra) or None,
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
                "notes": " | ".join(
                    b
                    for b in (cell("notes"), *_leftover_bits(row, sheet.rows[hidx], set(idx.values())))
                    if b
                )
                or None,
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
            for b in (
                nz.clean(cell("contact")),
                nz.clean(cell("sw_name")),
                *_leftover_bits(row, sheet.rows[hidx], set(idx.values())),
            )
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
