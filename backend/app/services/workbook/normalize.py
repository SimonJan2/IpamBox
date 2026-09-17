"""Cell-level normalizers for the Network_Address workbook.

Pure functions — unit-tested without a DB. Everything here is tolerant:
unparseable values produce warnings/raw passthroughs, never exceptions.
"""
import ipaddress
import re
from datetime import date, datetime, timedelta

# ---------------------------------------------------------------------------
# text
# ---------------------------------------------------------------------------

_WS_RE = re.compile(r"\s+")
_STARS_RE = re.compile(r"\*+")

# Hebrew final letters -> base form, for case/accent-insensitive search.
_FINALS = str.maketrans({"ך": "כ", "ם": "מ", "ן": "נ", "ף": "פ", "ץ": "צ"})


def clean(v) -> str:
    """Cell -> stripped single-line string; gershayim and star-runs fixed."""
    if v is None:
        return ""
    if isinstance(v, (int, float)):
        if isinstance(v, float) and v.is_integer():
            v = int(v)
        return str(v).strip()
    s = str(v)
    s = s.replace('""', '"').replace("''", "'")
    s = _STARS_RE.sub(" ", s)
    return _WS_RE.sub(" ", s).strip()


def fold_hebrew(v: str) -> str:
    """Fold Hebrew final letters to base form (ך->כ …) for loose matching."""
    return (v or "").translate(_FINALS)


_HDR_EDGE = "'\"׳״`"


def norm_header(v) -> str:
    """Header cell -> lowercase, single-spaced, for signature matching.
    Edge quotes/apostrophes are stripped — real headers like
    'שם לקוח באפל'' carry a trailing gershayim that must not break aliases."""
    s = _WS_RE.sub(" ", clean(v)).strip().lower()
    return s.strip(_HDR_EDGE).strip()


# ---------------------------------------------------------------------------
# IP addresses — split-octet assembly
# ---------------------------------------------------------------------------

_OCTET = r"(?:\d{1,3})"
_IP_FULL_RE = re.compile(rf"^{_OCTET}(?:\.{_OCTET}){{3}}$")
# "10.2.1." / "10.192.10" / "10.86.01" — a partial base awaiting a last octet
_IP_BASE_RE = re.compile(rf"^{_OCTET}(?:\.{_OCTET}){{1,2}}\.?$")
_IP_RANGE_RE = re.compile(r"^(\d{1,3})\s*-\s*(\d{1,3})$")


def _clean_octets(s: str) -> str | None:
    """Strip leading zeros per-octet; None if any octet > 255 or non-numeric."""
    parts = s.split(".")
    out = []
    for p in parts:
        if not p.isdigit():
            return None
        n = int(p)
        if n > 255:
            return None
        out.append(str(n))
    return ".".join(out)


def assemble_ip(base: str, last: str = "") -> str | None:
    """Combine a base column ('10.2.1.' / '10.192.10' / '10.0.0') with the
    'end ip' column ('81' / '101-200' handled elsewhere) into a full IPv4.

    Returns a canonical dotted string, or None when the pair can't form a
    valid address (placeholders like '10.x.252.' included).
    """
    base = clean(base)
    last = clean(last)
    if not base and not last:
        return None
    if _IP_FULL_RE.match(base):
        c = _clean_octets(base)
        if c:
            try:
                return str(ipaddress.ip_address(c))
            except ValueError:
                return None
        return None
    if not _IP_BASE_RE.match(base):
        return None
    if not last or not last.isdigit() or int(last) > 255:
        return None
    merged = (base.rstrip(".") + "." + last).strip(".")
    if merged.count(".") != 3:
        return None
    c = _clean_octets(merged)
    if not c:
        return None
    try:
        return str(ipaddress.ip_address(c))
    except ValueError:
        return None


def split_multi_ip(cell: str) -> tuple[list[str], list[str]]:
    """'10.10.10.12, 169.254.161.144, 10.192.10.67' -> (valid, link_local).

    Splits on commas/whitespace; each token validated. Link-local addresses
    are separated out (they don't belong in site prefixes but are kept for
    custom_fields).
    """
    valid, linklocal = [], []
    for tok in re.split(r"[,\s;/]+", clean(cell)):
        if not tok:
            continue
        c = _clean_octets(tok)
        if not c:
            continue
        try:
            ip = ipaddress.ip_address(c)
        except ValueError:
            continue
        (linklocal if ip.is_link_local else valid).append(str(ip))
    return valid, linklocal


def parse_range_end(base: str, end: str) -> tuple[str, str] | None:
    """'10.79.1.' + '101-200' -> ('10.79.1.101', '10.79.1.200')."""
    m = _IP_RANGE_RE.match(clean(end))
    if not m:
        return None
    lo, hi = assemble_ip(base, m.group(1)), assemble_ip(base, m.group(2))
    if lo and hi:
        return lo, hi
    return None


def second_octet(ip: str) -> int | None:
    try:
        return int(str(ip).split(".")[1])
    except (IndexError, ValueError):
        return None


def mask_to_prefixlen(mask: str) -> int | None:
    """'255.255.255.0' -> 24; dotted masks only, None when unparseable."""
    mask = clean(mask)
    if not mask:
        return None
    try:
        return ipaddress.IPv4Network(f"0.0.0.0/{mask}").prefixlen
    except ValueError:
        return None


def network_of(ip: str, mask: str) -> str | None:
    """ip + dotted mask -> CIDR string ('10.2.1.4', '255.255.255.0' -> '10.2.1.0/24')."""
    plen = mask_to_prefixlen(mask)
    if plen is None:
        return None
    try:
        return str(ipaddress.ip_network(f"{ip}/{plen}", strict=False))
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# MAC addresses — lenient superset of schemas.ip_address._norm_mac
# ---------------------------------------------------------------------------

_MAC_CANON = re.compile(r"^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$")
_MAC_BARE = re.compile(r"^[0-9A-Fa-f]{12}$")              # 00022e333585
_MAC_CISCO = re.compile(r"^([0-9A-Fa-f]{4}\.){2}[0-9A-Fa-f]{4}$")  # 0002.2e33.3585
_MAC_BADDIES = re.compile(r"[G-Zg-z]")  # letters outside hex range = garbage


def norm_mac(v: str) -> str | None:
    """Normalize any common MAC form to AA:BB:CC:DD:EE:FF; None if invalid.

    Delimiter-separated forms must fully match after : - . -> : folding;
    bare/Cisco forms must be pure hex ('00-of-…' fails on the 'o')."""
    s = clean(v)
    if not s or _MAC_BADDIES.search(s):
        return None
    folded = s.replace("-", ":").replace(".", ":")
    if _MAC_CANON.match(folded):
        return folded.upper()
    if _MAC_BARE.match(s):
        return ":".join(s[i : i + 2].upper() for i in range(0, 12, 2))
    if _MAC_CISCO.match(s):
        h = s.replace(".", "")
        return ":".join(h[i : i + 2].upper() for i in range(0, 12, 2))
    return None


# ---------------------------------------------------------------------------
# dates — Excel serials + loose text dates
# ---------------------------------------------------------------------------

_EXCEL_EPOCH = date(1899, 12, 30)  # openpyxl's own epoch convention
_TEXT_DATE_RE = re.compile(r"^(\d{1,2})[/.\-](\d{1,2})[/.\-](\d{2,4})$")


def excel_date(v) -> date | None:
    """datetime/date passthrough; int/float serial (20000-80000) -> date;
    'd/m/yy' text -> date. None when unparseable."""
    if v is None or v == "":
        return None
    if isinstance(v, datetime):
        return v.date()
    if isinstance(v, date):
        return v
    if isinstance(v, (int, float)) and 20000 <= v <= 80000:
        return _EXCEL_EPOCH + timedelta(days=int(v))
    s = clean(v)
    m = _TEXT_DATE_RE.match(s)
    if m:
        d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        y += 2000 if y < 100 else 0
        try:
            return date(y, mo, d)
        except ValueError:
            return None
    return None


# ---------------------------------------------------------------------------
# status — Hebrew free-text -> IPStatus-ish strings
# ---------------------------------------------------------------------------

_STATUS_MAP = {
    "פעיל": "active",
    "לא פעיל": "offline",
    "בוטל": "skip",
    "בהקמה": "reserved",
    "פג תוקף": "offline",
    "תקין": "active",
    "מושבת": "offline",
}


def status_of(v: str) -> str | None:
    """Known status keyword in the text -> ipam status ('skip' for בוטל);
    None when the text is just a description (most Hebrew cell text)."""
    s = clean(v)
    if not s:
        return None
    key = fold_hebrew(s)
    # longest keyword first — 'לא פעיל' must win over 'פעיל'
    for heb in sorted(_STATUS_MAP, key=len, reverse=True):
        if fold_hebrew(heb) in key:
            return _STATUS_MAP[heb]
    if key.lower().startswith("new"):
        return "active"
    return None


def map_status(v: str) -> tuple[str, str | None]:
    """(ipam status, raw-or-None). Defaults to 'active' — sheet rows
    document intended allocation; unmatched text -> 'discovered' + raw."""
    st = status_of(v)
    if st is not None:
        return st, clean(v)
    s = clean(v)
    if not s:
        return "active", None
    return "discovered", s


# ---------------------------------------------------------------------------
# VLAN / misc
# ---------------------------------------------------------------------------


def parse_vlan(v: str) -> tuple[int | None, str | None]:
    """'VLAN2' -> (2, 'VLAN2'); 'wifi' -> (None, 'wifi')."""
    s = clean(v)
    if not s:
        return None, None
    m = re.search(r"(\d{1,4})", s)
    if m and 1 <= int(m.group(1)) <= 4094:
        return int(m.group(1)), s
    return None, s


def parse_site_number(v: str) -> int | None:
    s = clean(v)
    if not s:
        return None
    m = re.search(r"\d+", s)
    return int(m.group()) if m else None


def split_serial_blob(v: str) -> list[str]:
    """'   PCB Serial Number        : 31231187' -> ['31231187'];
    multi-line cells -> one serial per line."""
    out = []
    for line in str(v or "").splitlines():
        line = line.strip()
        if not line:
            continue
        _, _, tail = line.partition(":")
        out.append(clean(tail or line))
    return [s for s in out if s]
