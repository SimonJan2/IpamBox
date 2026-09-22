"""Custom-list extraction: turn any sheet into {columns, rows} for a list.

Unlike the family parsers this keeps the sheet's own shape — every column
becomes a column def with a positional key ("c0"…) and an inferred type;
every data row becomes a {key: value} dict. Types are inferred by sampling
cell content so IP cells resolve live and date cells get expiry badges.
"""
import ipaddress
import re
from datetime import date, datetime

from app.services.workbook import normalize as nz

_MULTI_IP_RE = re.compile(r"[,\s;/]+")
_NUM_RE = re.compile(r"^-?\d+(?:\.\d+)?$")
_URL_RE = re.compile(r"^(?:https?://|www\.)", re.I)
_OWNER_HDRS = {
    "owner", "אחראי", "אחראית", "בעלים", "responsible", "ממלא", "מבצע",
}
_SELECT_MAX_OPTIONS = 12


def _cell_text(v) -> str:
    """Raw cell -> stored string. Dates iso-format; everything else cleans."""
    if isinstance(v, datetime):
        return v.date().isoformat()
    if isinstance(v, date):
        return v.isoformat()
    return nz.clean(v)


def _is_ip_token(t: str) -> bool:
    try:
        ipaddress.ip_address(t)
        return True
    except ValueError:
        return False


def _infer_type(header: str, raws: list, texts: list[str]) -> tuple[str, dict]:
    """(type, extra) for one column — extra carries options/multi."""
    vals = [t for t in texts if t]
    if not vals:
        return "text", {}
    if nz.fold_hebrew(header).strip().lower() in _OWNER_HDRS:
        return "owner", {}

    def frac(pred) -> float:
        return sum(1 for v in vals if pred(v)) / len(vals)

    # ip: single or comma-separated host values (10.10.10.12, 169.254.1.1)
    def _ips(v: str) -> list[str]:
        return [t for t in _MULTI_IP_RE.split(v) if t and _is_ip_token(t)]

    ip_hits = sum(1 for v in vals if _ips(v))
    if ip_hits / len(vals) > 0.6:
        multi = any(len(_ips(v)) > 1 for v in vals)
        return "ip", {"multi": True} if multi else {}

    # date: raw date/datetime cells, or text/serial the excel_date parser takes
    date_hits = sum(
        1 for r, t in zip(raws, texts)
        if t and (isinstance(r, (date, datetime)) or nz.excel_date(r) is not None)
    )
    if date_hits / len(vals) > 0.6:
        return "date", {}
    if frac(lambda v: bool(_NUM_RE.match(v))) > 0.8:
        return "number", {}
    if frac(lambda v: bool(_URL_RE.match(v))) > 0.6:
        return "url", {}
    # few distinct short values -> select (owners, statuses, env names);
    # requires at least one repeated value so unique-id columns stay text
    distinct = sorted(set(vals))
    if len(vals) >= 3 and len(distinct) < len(vals) and len(
        distinct
    ) <= _SELECT_MAX_OPTIONS and all(len(v) <= 40 for v in distinct):
        return "select", {"options": distinct}
    return "text", {}


def _sniff_header_row(row: list, more_rows: bool) -> bool:
    """Row 0 of an unrecognized sheet looks like headers when every cell is
    a short text label — no IP/number/date values (those are data). A
    single-column or empty row never qualifies, so truly headerless sheets
    keep their first row as data."""
    if not more_rows:
        return False
    cells = [nz.clean(c) for c in row]
    cells = [c for c in cells if c]
    if len(cells) < 2:
        return False
    for v in cells:
        if len(v) > 60:
            return False
        if _is_ip_token(v) or _NUM_RE.match(v) or nz.excel_date(v) is not None:
            return False
    return True


def extract_list_table(sheet, hidx: int) -> tuple[list[dict], list[dict]]:
    """SheetMatrix -> (column defs, row dicts).

    columns: [{key, label, type, options?, multi?}] — key is the column's
    positional index so re-imports map by label, not position.
    rows:    [{row: <1-based excel row>, data: {key: str}}]
    """
    width = max((len(r) for r in sheet.rows), default=0)
    if width == 0:
        return [], []

    if hidx < 0 and sheet.rows and _sniff_header_row(
        sheet.rows[0], len(sheet.rows) > 1
    ):
        # unrecognized family but the first row is clearly labels — a CSV
        # export or a sheet whose signature isn't in the family table
        hidx = 0

    if hidx >= 0:
        headers = [nz.clean(c) for c in sheet.rows[hidx]]
        data_start = hidx + 1
    else:
        headers = [""] * width
        data_start = 0
    headers += [""] * (width - len(headers))

    seen: dict[str, int] = {}
    labels: list[str] = []
    for ci, h in enumerate(headers):
        label = h or f"Column {ci + 1}"
        if label in seen:
            seen[label] += 1
            label = f"{label} ({seen[label]})"
        else:
            seen[label] = 1
        labels.append(label)

    # sample up to 60 data rows for type inference
    sample_rows = sheet.rows[data_start : data_start + 60]
    columns: list[dict] = []
    for ci in range(width):
        raws = [r[ci] for r in sample_rows if ci < len(r)]
        texts = [_cell_text(v) for v in raws]
        ctype, extra = _infer_type(labels[ci], raws, texts)
        columns.append({"key": f"c{ci}", "label": labels[ci], "type": ctype, **extra})

    rows: list[dict] = []
    for ri, raw in enumerate(sheet.rows[data_start:], start=data_start + 1):
        data = {}
        for ci in range(width):
            if ci < len(raw) and raw[ci] is not None:
                v = _cell_text(raw[ci])
                if v != "":
                    data[f"c{ci}"] = v
        if data:
            rows.append({"row": ri, "data": data})
    return columns, rows


def pick_key_column(columns: list[dict], rows: list[dict]) -> str | None:
    """Default merge column: first non-date/ip column filled in most rows
    (the leftmost name-ish column), else the first column."""
    if not columns:
        return None
    n = max(len(rows), 1)
    for c in columns:
        if c["type"] in ("date", "ip", "url"):
            continue
        filled = sum(1 for r in rows if (r["data"].get(c["key"]) or "").strip())
        if filled / n > 0.5:
            return c["key"]
    return columns[0]["key"]


def key_for(data: dict, key_column: str | None) -> str:
    """Normalized merge key — same Hebrew folding the site matcher uses."""
    if not key_column:
        return ""
    v = str(data.get(key_column) or "")
    return nz.fold_hebrew(v).lower().strip()
