"""Sheet family detection by header signature (Hebrew + English variants)."""
import re

from app.services.workbook.normalize import clean, norm_header

# families in priority order — first match wins
_FAMILIES = (
    "sites_master",
    "circuits",
    "certificates",
    "services",
    "assets",
    "inventory",
    "servers",
    "site_sheet",
)

_IP_FRAG_RE = re.compile(r"^\d{1,3}\.\d{1,3}(?:\.\d{1,3})?\.?$")


def _has(headers: list[str], *needles: str) -> bool:
    return all(any(n in h for h in headers) for n in needles)


def _looks_like_header(row: list) -> list[str]:
    return [norm_header(c) for c in row]


def classify_sheet(sheet) -> tuple[str, int, list[str]]:
    """(family, header_row_index, warnings).

    header_row_index = index of the row carrying column headers (-1 when the
    sheet has none — headerless site sheets get positional mapping).
    """
    warnings: list[str] = []
    if sheet.n_rows == 0:
        return "empty", -1, warnings

    # scan the first rows for a recognized header signature (junk/note rows
    # often sit above the real header — e.g. 020, 099)
    for idx, row in enumerate(sheet.rows[:10]):
        h = _looks_like_header(row)
        joined = set(h)
        if not any(joined):
            continue
        if "name" in joined and "code" in joined and (
            "type" in joined or _has(h, "subet")
        ):
            return "sites_master", idx, warnings
        if _has(h, "קוד בבזק") or (_has(h, "סוג הקו") and _has(h, "כתובת wan")):
            return "circuits", idx, warnings
        if joined and h[0] == "software" and len(joined) <= 3:
            return "certificates", idx, warnings
        if _has(h, "שם השירות") or _has(h, "מי הגורם שנהנה מהשירות"):
            return "services", idx, warnings
        if _has(h, "דגם") and _has(h, "חברה"):
            return "assets", idx, warnings
        if (_has(h, "serial number") and _has(h, "device")) or (
            _has(h, "hostname") and _has(h, "serial")
        ):
            return "inventory", idx, warnings
        if _has(h, "guest os"):
            return "servers", idx, warnings
        if any(x in joined for x in ("ip address", "ip", "כתובת", "כתובת ip")):
            return "site_sheet", idx, warnings

    # headerless fallback: 3+ rows with an IP-fragment column -> site_sheet
    frag_counts = [0] * 8
    for row in sheet.rows[:25]:
        for ci, cell in enumerate(row[:8]):
            if _IP_FRAG_RE.match(clean(cell)):
                frag_counts[ci] += 1
    if max(frag_counts, default=0) >= 3:
        warnings.append("no header row found — positional column mapping assumed")
        return "site_sheet", -1, warnings

    return "unknown", -1, warnings
