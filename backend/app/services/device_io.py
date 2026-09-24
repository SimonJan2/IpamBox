"""Device CSV/XLSX export + smart stateless import.

Export: every filter param GET /devices accepts — the exported set equals
the filtered set, computed facets (health/wiring) included. FK columns
export as NAMES (site/rack/rack_group/carrier) so the file reads like the
page; `id` pins exact rows for update re-import; `ips` is a
space-separated address list. Column order is the round-trip contract —
the import auto-map recognizes every one of these headers.

Import: stateless file-posted-twice flow (dry_run preview, then commit —
no staging table). Headers auto-map through norm_header aliases
(canonical + English + Hebrew + the NetBox device CSV shape). Matching
precedence: id -> serial_number -> mac_address -> name+site (name alone
only when unambiguous). All writes go through the normal service layer
(apply_device_patch / the create path's check_placement) so the changelog
covers imported rows for free. The ips column only ever LINKS existing
ip_addresses rows — import never creates addresses.
"""
import io
import ipaddress
import json
from collections.abc import Iterable
from dataclasses import dataclass, field

import openpyxl
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.device import Device
from app.models.ip_address import IPAddress
from app.models.rack import Rack, RackFace, RackGroup
from app.models.site import Site
from app.schemas.common import ip_display
from app.services.cabling import interface_stats
from app.services.devices import ips_by_device
from app.services.ipam import IPAMError
from app.services.racks import (
    SLOT_LAYOUTS,
    apply_device_patch,
    check_placement,
    device_fields,
    rack_devices,
)
from app.services.workbook.normalize import (
    clean,
    fold_hebrew,
    norm_header,
    norm_mac,
)
from app.services.workbook.reader import load_upload

# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------

# Column order is a contract — the import auto-map recognizes all of these.
DEVICE_EXPORT_COLUMNS = [
    "id", "name", "device_type", "manufacturer", "model", "category",
    "serial_number", "mac_address", "site", "rack", "rack_group",
    "u_position", "u_height", "face", "carrier", "slot", "slot_layout",
    "watts", "weight_kg", "ips", "ip_count", "interface_count",
    "cabled_count", "source", "notes", "created_at",
]

# Health facet values: the five IP statuses + the no-linked-IPs bucket —
# same vocabulary as the page's Health facet.
HEALTH_CLASSES = (
    "active", "reserved", "dhcp", "discovered", "offline", "unmonitored",
)


async def device_export_rows(
    session: AsyncSession, devices: list[Device]
) -> list[list]:
    """Devices -> matrix rows in DEVICE_EXPORT_COLUMNS order.

    FK columns are names (site/rack/rack_group/carrier); ips is
    space-separated; counts mirror the list endpoint's transients.
    """
    ids = [d.id for d in devices]
    rack_ids = {d.rack_id for d in devices if d.rack_id is not None}
    site_ids = {d.site_id for d in devices if d.site_id is not None}
    carrier_ids = {d.carrier_id for d in devices if d.carrier_id is not None}

    racks = (
        {
            r.id: r
            for r in (
                await session.execute(select(Rack).where(Rack.id.in_(rack_ids)))
            ).scalars()
        }
        if rack_ids
        else {}
    )
    group_ids = {r.group_id for r in racks.values() if r.group_id is not None}
    groups = (
        {
            g.id: g
            for g in (
                await session.execute(
                    select(RackGroup).where(RackGroup.id.in_(group_ids))
                )
            ).scalars()
        }
        if group_ids
        else {}
    )
    sites = (
        {
            s.id: s
            for s in (
                await session.execute(select(Site).where(Site.id.in_(site_ids)))
            ).scalars()
        }
        if site_ids
        else {}
    )
    # Carrier names: carriers in the exported set resolve locally; ones
    # outside it (filtered export of just the children) need a lookup.
    carrier_names = {d.id: d.name for d in devices if d.id in carrier_ids}
    outside = carrier_ids - set(carrier_names)
    if outside:
        carrier_names.update(
            dict(
                (
                    await session.execute(
                        select(Device.id, Device.name).where(
                            Device.id.in_(outside)
                        )
                    )
                ).all()
            )
        )
    ips = await ips_by_device(session, ids)
    istats = await interface_stats(session, ids)

    rows = []
    for d in devices:
        rack = racks.get(d.rack_id)
        group = groups.get(rack.group_id) if rack else None
        site = sites.get(d.site_id)
        iface, cabled = istats.get(d.id, (0, 0))
        rows.append(
            [
                d.id,
                d.name,
                d.device_type,
                d.manufacturer,
                d.model,
                d.category,
                d.serial_number,
                d.mac_address,
                site.name if site else None,
                rack.name if rack else None,
                group.name if group else None,
                d.u_position,
                d.u_height,
                d.face.value if d.face else None,
                carrier_names.get(d.carrier_id),
                d.slot,
                d.slot_layout,
                d.watts,
                float(d.weight_kg) if d.weight_kg is not None else None,
                " ".join(
                    ip_display(i.address) or "" for i in ips.get(d.id, [])
                ),
                len(ips.get(d.id, [])),
                iface,
                cabled,
                d.source,
                d.notes,
                d.created_at.isoformat() if d.created_at else None,
            ]
        )
    return rows


def xlsx_response(filename: str, header: list[str], rows: list[list]) -> StreamingResponse:
    """Single-sheet plain-value workbook — the xlsx twin of csv_response."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "devices"
    ws.append(header)
    for row in rows:
        ws.append(["" if v is None else v for v in row])
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ---------------------------------------------------------------------------
# Header auto-map
# ---------------------------------------------------------------------------

# Fields the importer can write/match on, in the order the dialog offers
# them. `source`/`created_at`/counts are export-only — never written.
DEVICE_IMPORT_FIELDS = [
    "id", "name", "device_type", "manufacturer", "model", "category",
    "serial_number", "mac_address", "site", "rack", "rack_group",
    "u_position", "u_height", "face", "carrier", "slot", "slot_layout",
    "watts", "weight_kg", "ips", "notes",
]

# Scalar text fields a row may set directly (blank cell = clear on update).
_SCALAR_FIELDS = (
    "device_type", "manufacturer", "model", "category",
    "serial_number", "mac_address", "slot_layout", "notes",
)

# Headers recognized but intentionally not imported: provenance is always
# "import" on create (source) and the rest are computed/export-only.
_IGNORED_HEADERS = {
    "source", "created_at", "updated_at", "health",
    "ip_count", "interface_count", "cabled_count",
}

# canonical field -> normalized alias set (norm_header applied to both
# sides at lookup — case/quotes/whitespace already folded).
_ALIASES: dict[str, set[str]] = {
    "id": {"id", "#id", "pk", "device id"},
    "name": {
        "name", "host", "hostname", "device", "device name", "server",
        "שם", "שם מכשיר", "מכשיר", "מארח", "שם שרת",
    },
    "device_type": {
        "device_type", "device type", "type", "kind", "role",
        "device_role", "device role", "סוג", "סוג מכשיר", "תפקיד",
    },
    "manufacturer": {"manufacturer", "vendor", "make", "oem", "יצרן", "ספק"},
    "model": {"model", "דגם", "מודל"},
    "category": {"category", "קטגוריה"},
    "serial_number": {
        "serial_number", "serial", "serial number", "serial no", "sn",
        "s/n", 'מק"ט', "מספר סידורי", "סידורי", "סיריאל",
    },
    "mac_address": {
        "mac_address", "mac", "mac address", "כתובת מאק", "מאק",
        "כתובת mac",
    },
    "site": {"site", "site_name", "site name", "אתר", "מיקום"},
    "rack": {"rack", "rack_name", "rack name", "ארון", "רק", "ארון תקשורת"},
    "rack_group": {
        "rack_group", "rack group", "קבוצת ארונות", "שורת ארונות", "שורה",
    },
    "u_position": {
        "u_position", "u", "position", "rack u", "rack_u", "u position",
        "start u", "מיקום u", "גובה התחלה", "יחידת u",
    },
    "u_height": {
        "u_height", "height", "u height", "size", "u size", "גובה", "גובה u",
    },
    "face": {"face", "rack face", "side", "פנים", "צד"},
    "carrier": {"carrier", "tray", "carrier name", "מגש", "carrier_slot"},
    "slot": {"slot", "carrier slot", "חריץ", "סלוט"},
    "slot_layout": {
        "slot_layout", "slot layout", "layout", "carrier layout", "פריסה",
    },
    "watts": {
        "watts", "power", "power w", "power (w)", "power_w", "wattage",
        "הספק",
    },
    "weight_kg": {
        "weight_kg", "weight", "weight kg", "weight (kg)", "kg", "משקל",
    },
    "ips": {
        "ips", "ip", "ip_addresses", "ip addresses", "addresses", "address",
        "כתובות ip", "כתובת ip", "אייפי",
    },
    "notes": {
        "notes", "note", "comment", "comments", "description", "הערות",
        "הערה", "תיאור",
    },
}

# NetBox role headers — their presence with no explicit `model` column is
# the signal that `device_type` carries NetBox's model slug, not our type.
_NETBOX_ROLE_HEADERS = {"role", "device_role", "device role"}


def _alias_to_field() -> dict[str, str]:
    out = {}
    for field, aliases in _ALIASES.items():
        out.setdefault(field, field)
        for a in aliases:
            out[a] = field
    return out


def auto_map_fields(
    headers: list[str],
    alias_to_field: dict[str, str],
    ignored: set[str] | frozenset[str] = frozenset(),
    remap=None,
) -> tuple[dict[str, str | None], list[str]]:
    """header -> canonical field (None = skip). Unmapped columns are
    reported, never guessed into a field. First column wins on duplicate
    field claims — later duplicates surface as unmapped.

    Shared by every sheet family (devices, racks, groups, interfaces,
    cables): `alias_to_field` maps normalized headers to the family's
    canonical fields, `ignored` holds export-only headers that map to
    None without an unmapped flag, and `remap(field, norm, normed)` may
    redirect a mapped field (the NetBox shape rule)."""
    normed = [norm_header(h) for h in headers]
    mapping: dict[str, str | None] = {}
    unmapped: list[str] = []
    claimed: set[str] = set()
    for h, n in zip(headers, normed):
        if not n:
            continue
        if n in ignored:
            mapping[h] = None
            continue
        f = alias_to_field.get(n)
        if remap is not None:
            f = remap(f, n, normed)
        if f is None:
            mapping[h] = None
            unmapped.append(h)
        elif f in claimed:
            mapping[h] = None
            unmapped.append(h)
        else:
            mapping[h] = f
            claimed.add(f)
    return mapping, unmapped


def auto_map_headers(
    headers: list[str],
) -> tuple[dict[str, str | None], list[str]]:
    """Device-sheet auto-map — auto_map_fields with the device alias table
    and the NetBox shape rule (a role column with no explicit `model`
    column means `device_type` carries NetBox's model slug, not our type)."""
    def remap(field, n, normed):
        netbox_shape = (
            any(x in _NETBOX_ROLE_HEADERS for x in normed)
            and "model" not in normed
        )
        if netbox_shape and field == "device_type" and n in (
            "device_type", "device type"
        ):
            return "model"
        return field

    return auto_map_fields(
        headers, _alias_to_field(), _IGNORED_HEADERS, remap
    )


def apply_mapping_overrides(
    mapping: dict[str, str | None],
    headers: list[str],
    raw: str | None,
    fields: list[str] | None = None,
    union_headers: list[str] | None = None,
) -> dict[str, str | None]:
    """User {source_header: field} overrides on top of the auto-map.
    field "" / null explicitly unmaps a column; a field outside `fields`
    (default DEVICE_IMPORT_FIELDS) leaves the header untouched — per-sheet
    families only take overrides they understand. `union_headers` (bundle
    imports) validates each source against every sheet's headers combined —
    a source living in a different sheet is skipped here rather than 422."""
    if not raw:
        return mapping
    try:
        overrides = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        raise HTTPException(422, "bad mapping JSON — expected {header: field}")
    if not isinstance(overrides, dict):
        raise HTTPException(422, "bad mapping JSON — expected {header: field}")
    valid = fields if fields is not None else DEVICE_IMPORT_FIELDS
    known = union_headers if union_headers is not None else headers
    known_exact = set(known)
    known_norm = {norm_header(h) for h in known}
    by_norm = {norm_header(h): h for h in headers}
    by_exact = {h: h for h in headers}
    for src, field in overrides.items():
        if src not in known_exact and norm_header(src) not in known_norm:
            raise HTTPException(
                422, f"mapping source {src!r} is not a column in the file"
            )
        h = by_exact.get(src) or by_norm.get(norm_header(src))
        if h is None:
            continue
        if field in (None, ""):
            mapping[h] = None
            continue
        if field not in valid:
            continue
        mapping[h] = field
    return mapping


def sheet_rows(
    sheet,
) -> tuple[list[str], list[tuple[int, dict[str, str]]]]:
    """One SheetMatrix -> (headers, [(row_no, {header: str})]).

    Row numbers are the file's (header = row 1). Unnamed interior columns
    still surface — their data is reportable rather than silently dropped.
    Shared by the single-sheet device importer and the multi-sheet rack
    bundle importer."""
    if not sheet.rows:
        raise HTTPException(422, "empty file or missing header row")
    raw_headers = sheet.rows[0]
    headers = [clean(h) for h in raw_headers]
    if not any(headers):
        raise HTTPException(422, "empty file or missing header row")
    headers = [h or f"column {i + 1}" for i, h in enumerate(headers)]
    rows: list[tuple[int, dict[str, str]]] = []
    for i, raw in enumerate(sheet.rows[1:], start=2):
        row: dict[str, str] = {}
        for h, v in zip(headers, raw):
            if h not in row:  # first column wins on duplicate header names
                row[h] = clean(v)
        if any(row.values()):
            rows.append((i, row))
    return headers, rows


def parse_device_sheet(
    payload: bytes, filename: str
) -> tuple[list[str], list[tuple[int, dict[str, str]]]]:
    """First sheet of an xlsx/CSV -> (headers, [(row_no, {header: str})]).

    xlsx is detected by zipfile magic inside load_upload; everything else
    is parsed as CSV (utf-8-sig, cp1255 fallback for Hebrew ANSI saves).
    """
    try:
        sheets = load_upload(payload, filename)
    except Exception as e:
        raise HTTPException(422, f"cannot parse file: {e}")
    if not sheets:
        raise HTTPException(422, "empty file or missing header row")
    return sheet_rows(sheets[0])


# ---------------------------------------------------------------------------
# Import planning
# ---------------------------------------------------------------------------

# Patch keys that place a device — their presence triggers the placement
# simulation on updates (attribute-only patches skip it).
_PLACEMENT_KEYS = {"rack_id", "u_position", "u_height", "face", "carrier_id", "slot"}


@dataclass
class _Refs:
    """All reference data loaded once up front — no per-row queries."""
    sites_by_id: dict[int, Site]
    sites_by_name: dict[str, list[Site]]
    racks_by_id: dict[int, Rack]
    racks_by_name: dict[str, list[Rack]]
    groups_by_id: dict[int, RackGroup]
    groups_by_name: dict[str, list[RackGroup]]
    devices_by_id: dict[int, Device]
    devices_by_serial: dict[str, list[Device]]
    devices_by_mac: dict[str, list[Device]]
    devices_by_name: dict[str, list[Device]]
    ip_by_addr: dict[str, IPAddress]
    device_ips: dict[int, list[IPAddress]]


@dataclass
class Planned:
    """One file row's verdict + everything needed to apply it."""
    row: int
    ok: bool
    action: str                      # create|update|skip|error
    detail: str
    diff: dict | None = None
    device: Device | None = None     # matched existing row (update/skip)
    create_data: dict | None = None  # Device(**create_data) on commit
    patch: dict | None = None        # apply_device_patch payload (update)
    ip_rows: list = field(default_factory=list)
    # commit-time helpers — batch carriers hold a negative temp id until
    # the pass-A flush assigns a real one.
    carrier_parent: "Planned | None" = None

    def out(self) -> dict:
        d = {"row": self.row, "ok": self.ok, "action": self.action,
             "detail": self.detail}
        if self.diff:
            d["diff"] = self.diff
        return d


class _Occupancy:
    """Simulated rack occupancy: DB occupants plus earlier batch rows,
    kept current through update/unrack simulations so conflicts against
    the batch itself surface in the preview."""

    def __init__(self, devices: list[Device]):
        self.by_rack: dict[int, list[Device]] = {}
        self.current: dict[int, Device] = {}  # device id -> current occupant
        for d in devices:
            if d.rack_id is not None:
                self.by_rack.setdefault(d.rack_id, []).append(d)
                self.current[d.id] = d

    def devices(self, rack_id: int) -> list[Device]:
        return self.by_rack.get(rack_id, [])

    def add(self, d: Device) -> None:
        self.by_rack.setdefault(d.rack_id, []).append(d)
        if d.id is not None:
            self.current[d.id] = d

    def _drop(self, d: Device) -> None:
        lst = self.by_rack.get(d.rack_id or -1)
        if lst and d in lst:
            lst.remove(d)

    def replace(self, device_id: int, cand: Device) -> None:
        old = self.current.get(device_id)
        if old is not None:
            self._drop(old)
        self.add(cand)

    def remove(self, device_id: int) -> None:
        old = self.current.pop(device_id, None)
        if old is not None:
            self._drop(old)


def _fold(v: str) -> str:
    return fold_hebrew(v.strip().lower())


def _name_map(rows) -> dict[str, list]:
    out: dict[str, list] = {}
    for r in rows:
        out.setdefault(_fold(r.name or ""), []).append(r)
    return out


async def _load_refs(
    session: AsyncSession,
    frows: list[tuple[int, dict[str, str]]],
    *,
    extra_sites: Iterable[Site] = (),
    extra_groups: Iterable[RackGroup] = (),
    extra_racks: Iterable[Rack] = (),
) -> _Refs:
    """One-shot reference load keyed by what the file actually mentions —
    the addresses importer's O(table)-per-row bug must not come back.

    The extra_* iterables carry transient rows planned by an enclosing
    bundle import (negative temp ids) so the file can name sites/groups/
    racks it creates itself."""
    ids: set[int] = set()
    serials: set[str] = set()
    macs: set[str] = set()
    names: set[str] = set()
    ip_tokens: set[str] = set()
    rack_vals: set[str] = set()
    carrier_ids: set[int] = set()
    for _, fields in frows:
        if v := _parse_id(fields.get("id")):
            ids.add(v)
        if v := (fields.get("serial_number") or "").strip():
            serials.add(v)
        if v := norm_mac(fields.get("mac_address") or ""):
            macs.add(v)
        if v := (fields.get("name") or "").strip():
            names.add(_fold(v))
        for t in _ip_tokens(fields.get("ips") or "")[0]:
            ip_tokens.add(t)
        if v := (fields.get("rack") or "").strip():
            rack_vals.add(v)
        if v := (fields.get("carrier") or "").strip():
            if cid := _parse_id(v):
                carrier_ids.add(cid)
            else:
                names.add(_fold(v))  # carriers resolve by name too

    sites = list((await session.execute(select(Site))).scalars()) + list(
        extra_sites
    )
    groups = list((await session.execute(select(RackGroup))).scalars()) + list(
        extra_groups
    )
    racks = list((await session.execute(select(Rack))).scalars()) + list(
        extra_racks
    )

    # Rack-name candidates decide which racks' occupants to pull.
    racks_by_name = _name_map(racks)
    ref_rack_ids: set[int] = set()
    for v in rack_vals:
        if rid := _parse_id(v):
            ref_rack_ids.add(rid)
        else:
            ref_rack_ids.update(r.id for r in racks_by_name.get(_fold(v), []))

    device_filter = [
        Device.id.in_(ids | carrier_ids),
        Device.rack_id.in_(ref_rack_ids),
    ]
    if serials:
        device_filter.append(Device.serial_number.in_(serials))
    if macs:
        device_filter.append(Device.mac_address.in_(macs))
    if names:
        device_filter.append(
            func.lower(func.translate(Device.name, "םןץףך", "מנצפכ")).in_(names)
        )
    devices = list(
        (await session.execute(select(Device).where(or_(*device_filter))))
        .scalars()
    )
    # Carriers named in the file but living in racks the `rack` column
    # never mentions still need their racks' occupants for slot checks —
    # pull any missing rack now.
    carrier_name_vals = {
        _fold(f["carrier"])
        for _, f in frows
        if (f.get("carrier") or "").strip() and _parse_id(f["carrier"]) is None
    }
    extra_racks = {
        d.rack_id
        for d in devices
        if (d.id in carrier_ids or _fold(d.name or "") in carrier_name_vals)
        and d.rack_id is not None
    } - ref_rack_ids
    if extra_racks:
        devices += list(
            (
                await session.execute(
                    select(Device).where(Device.rack_id.in_(extra_racks))
                )
            ).scalars()
        )
    devices_by_id = {d.id: d for d in devices}
    devices_by_serial: dict[str, list[Device]] = {}
    devices_by_mac: dict[str, list[Device]] = {}
    for d in devices:
        if d.serial_number:
            devices_by_serial.setdefault(d.serial_number, []).append(d)
        if d.mac_address:
            devices_by_mac.setdefault(d.mac_address, []).append(d)
    devices_by_name = _name_map(devices)

    ip_rows = (
        list(
            (
                await session.execute(
                    select(IPAddress).where(
                        func.host(IPAddress.address).in_(ip_tokens)
                    )
                )
            ).scalars()
        )
        if ip_tokens
        else []
    )
    ip_by_addr = {ip_display(r.address): r for r in ip_rows}
    device_ips = await ips_by_device(session, list(devices_by_id))

    return _Refs(
        sites_by_id={s.id: s for s in sites},
        sites_by_name=_name_map(sites),
        racks_by_id={r.id: r for r in racks},
        racks_by_name=racks_by_name,
        groups_by_id={g.id: g for g in groups},
        groups_by_name=_name_map(groups),
        devices_by_id=devices_by_id,
        devices_by_serial=devices_by_serial,
        devices_by_mac=devices_by_mac,
        devices_by_name=devices_by_name,
        ip_by_addr=ip_by_addr,
        device_ips=device_ips,
    )


def _parse_id(v: str | None) -> int | None:
    """'#5' or '5' -> 5; None when the cell isn't an id reference."""
    s = (v or "").strip().lstrip("#")
    return int(s) if s.isdigit() else None


def _ip_tokens(raw: str) -> tuple[list[str], list[str]]:
    """'10.0.0.1 10.0.0.2' (comma/semicolon ok) -> (normalized, bad)."""
    good, bad = [], []
    for tok in raw.replace(",", " ").replace(";", " ").split():
        try:
            good.append(str(ipaddress.ip_interface(tok).ip))
        except ValueError:
            bad.append(tok)
    return good, bad


def _resolve_named(
    value: str,
    by_id: dict[int, object],
    by_name: dict[str, list],
    kind: str,
) -> tuple[object | None, str | None]:
    """'#id' or folded-name lookup -> (row, error). Ambiguity is an error —
    a coin flip into the wrong rack is worse than a red row."""
    v = value.strip()
    if rid := _parse_id(v):
        row = by_id.get(rid)
        return (row, None) if row is not None else (None, f"{kind} {v} not found")
    cands = by_name.get(_fold(v)) or []
    if len(cands) == 1:
        return cands[0], None
    if not cands:
        return None, f"{kind} '{v}' not found"
    return None, f"{kind} '{v}' is ambiguous ({len(cands)} matches — use #id)"


def _resolve_rack(
    value: str,
    site_id: int | None,
    group_id: int | None,
    refs: _Refs,
) -> tuple[Rack | None, str | None]:
    """Rack by '#id' or name, scoped by site/group when the row gives them."""
    v = value.strip()
    if rid := _parse_id(v):
        rack = refs.racks_by_id.get(rid)
        if rack is None:
            return None, f"rack {v} not found"
        if site_id is not None and rack.site_id != site_id:
            return None, f"rack '{rack.name}' is not in the given site"
        if group_id is not None and rack.group_id != group_id:
            return None, f"rack '{rack.name}' is not in the given rack_group"
        return rack, None
    cands = refs.racks_by_name.get(_fold(v)) or []
    if site_id is not None:
        cands = [r for r in cands if r.site_id == site_id]
    if group_id is not None:
        cands = [r for r in cands if r.group_id == group_id]
    if len(cands) == 1:
        return cands[0], None
    if not cands:
        return None, f"rack '{v}' not found"
    return None, (
        f"rack '{v}' is ambiguous ({len(cands)} matches — "
        "qualify with site/rack_group or #id)"
    )


def _int_field(v: str | None, name: str) -> tuple[int | None, str | None]:
    s = (v or "").strip()
    if not s:
        return None, None
    try:
        return int(s), None
    except ValueError:
        try:
            f = float(s)
            return (int(f), None) if f.is_integer() else (None, f"bad {name} value {v!r}")
        except ValueError:
            return None, f"bad {name} value {v!r}"


def _float_field(v: str | None, name: str) -> tuple[float | None, str | None]:
    s = (v or "").strip()
    if not s:
        return None, None
    try:
        return float(s), None
    except ValueError:
        return None, f"bad {name} value {v!r}"


def _match(
    fields: dict[str, str],
    site_id: int | None,
    refs: _Refs,
    rack_id: int | None = None,
) -> tuple[Device | None, str | None, str | None]:
    """Precedence id -> serial -> mac -> name+site. Returns (device, how,
    error); ambiguity is an error row, never a coin flip. `rack_id` scopes
    the name match to the rack the row is being placed into first (a
    same-named device elsewhere is then picked up by the global rules —
    the file moves it, same as serial/mac/id)."""
    if rid := _parse_id(fields.get("id")):
        if d := refs.devices_by_id.get(rid):
            return d, "id", None
    if s := (fields.get("serial_number") or "").strip():
        c = refs.devices_by_serial.get(s) or []
        if len(c) > 1:
            return None, None, f"serial_number '{s}' is ambiguous ({len(c)} devices)"
        if c:
            return c[0], "serial_number", None
    if m := norm_mac(fields.get("mac_address") or ""):
        c = refs.devices_by_mac.get(m) or []
        if len(c) > 1:
            return None, None, f"mac_address '{m}' is ambiguous ({len(c)} devices)"
        if c:
            return c[0], "mac_address", None
    if n := (fields.get("name") or "").strip():
        cands = refs.devices_by_name.get(_fold(n)) or []
        if rack_id is not None:
            scoped = [d for d in cands if d.rack_id == rack_id]
            if len(scoped) > 1:
                return None, None, (
                    f"name '{n}' is ambiguous within rack "
                    f"({len(scoped)} devices — use #id)"
                )
            if scoped:
                return scoped[0], "name+rack", None
        if site_id is not None:
            scoped = [d for d in cands if d.site_id == site_id]
            if len(scoped) > 1:
                return None, None, (
                    f"name '{n}' + site is ambiguous ({len(scoped)} devices)"
                )
            if scoped:
                return scoped[0], "name+site", None
        else:
            if len(cands) > 1:
                return None, None, (
                    f"name '{n}' is ambiguous ({len(cands)} devices — "
                    "add a site column or use #id)"
                )
            if cands:
                return cands[0], "name", None
    return None, None, None


def _err(row: int, detail: str) -> Planned:
    return Planned(row=row, ok=False, action="error", detail=detail)


async def plan_device_import(
    session: AsyncSession,
    frows: list[tuple[int, dict[str, str]]],
    mapping: dict[str, str | None],
    *,
    on_match: str,
    unracked_on_missing: bool,
    extra_sites: Iterable[Site] = (),
    extra_groups: Iterable[RackGroup] = (),
    extra_racks: Iterable[Rack] = (),
    skipped_rack_ids: frozenset[int] = frozenset(),
    replace_rack_ids: frozenset[int] = frozenset(),
    scope_names_to_rack: bool = False,
) -> list[Planned]:
    """Validate every row against the DB + earlier batch rows. Pure —
    writes nothing (dry_run and commit share this plan).

    Bundle-import knobs (all no-ops for the standalone device importer):
    - extra_*: transient rows the bundle plans create (negative temp ids)
      so the devices sheet can name sites/groups/racks built by the file.
    - skipped_rack_ids: racks an enclosing on_existing=skip froze — rows
      landing there report skip, nothing is placed or unmounted.
    - replace_rack_ids: racks whose rack-level occupants the commit
      unracks first (replace_devices) — the simulation drops them so
      incoming rows see the emptied rack; carrier children keep their
      mount (unracking a carrier never unmounts its tray).
    - scope_names_to_rack: name matching prefers the target rack's own
      occupants before the site/global rules."""
    # canonical field -> raw cell text per row
    field_rows = [
        (
            num,
            {
                f: row[h]
                for h, f in mapping.items()
                if f is not None and row.get(h) is not None
            },
        )
        for num, row in frows
    ]
    refs = await _load_refs(
        session, field_rows,
        extra_sites=extra_sites, extra_groups=extra_groups,
        extra_racks=extra_racks,
    )
    occ = _Occupancy(
        [
            d
            for d in refs.devices_by_id.values()
            if d.rack_id is not None
            and not (
                d.rack_id in replace_rack_ids and d.carrier_id is None
            )
        ]
    )
    # (rack_id, folded name) -> pending carrier plan for pass-B resolution
    pending_carriers: dict[tuple[int, str], Planned] = {}
    results: list[Planned] = []
    deferred: list[tuple[int, dict[str, str]]] = []
    for num, fields in field_rows:
        if (fields.get("carrier") or "").strip():
            deferred.append((num, fields))
            continue
        p = _plan_rack_level(
            num, fields, refs, occ, on_match, unracked_on_missing,
            skipped_rack_ids=skipped_rack_ids,
            replace_rack_ids=replace_rack_ids,
            scope_names_to_rack=scope_names_to_rack,
        )
        results.append(p)
        if not p.ok:
            continue
        if (
            p.create_data
            and p.create_data.get("slot_layout")
            and p.create_data.get("rack_id") is not None
        ):
            pending_carriers[
                (p.create_data["rack_id"], _fold(p.create_data["name"]))
            ] = p
        elif p.patch is not None and p.device is not None:
            # A matched carrier that stays/lands racked is also resolvable
            # by pass-B children — key it by its post-patch rack + name.
            layout = p.patch.get("slot_layout", p.device.slot_layout)
            rid = p.patch.get("rack_id", p.device.rack_id)
            if layout and rid is not None:
                pending_carriers[
                    (rid, _fold(p.patch.get("name") or p.device.name or ""))
                ] = p
    for num, fields in deferred:
        results.append(
            _plan_child(
                num, fields, refs, occ, on_match,
                unracked_on_missing, pending_carriers,
                skipped_rack_ids=skipped_rack_ids,
                replace_rack_ids=replace_rack_ids,
                scope_names_to_rack=scope_names_to_rack,
            )
        )
    results.sort(key=lambda p: p.row)
    return results


def _scalars(fields: dict[str, str]) -> tuple[dict, str | None]:
    """Mapped text/number columns -> device values; blank cells mean None
    (explicit clear on update / unset on create)."""
    out: dict = {}
    for f in _SCALAR_FIELDS:
        if f not in fields:
            continue
        v = fields[f].strip()
        if f == "mac_address":
            if v:
                mac = norm_mac(v)
                if mac is None:
                    return {}, f"bad mac_address value {v!r}"
                out[f] = mac
            else:
                out[f] = None
        elif f == "slot_layout":
            if v and v not in SLOT_LAYOUTS:
                return {}, (
                    f"bad slot_layout {v!r} "
                    f"(expected {'/'.join(SLOT_LAYOUTS)})"
                )
            out[f] = v or None
        else:
            out[f] = v or None
    for f in ("u_position", "u_height", "slot", "watts"):
        if f in fields:
            n, err = _int_field(fields[f], f)
            if err:
                return {}, err
            if f == "u_position" and n is not None and n < 1:
                return {}, "u_position must be >= 1"
            if f == "u_height" and n is not None and n < 1:
                return {}, "u_height must be >= 1"
            if f == "slot" and n is not None and n < 0:
                return {}, "slot must be >= 0"
            if f == "watts" and n is not None and n < 0:
                return {}, "watts must be >= 0"
            out[f] = n
    if "weight_kg" in fields:
        w, err = _float_field(fields["weight_kg"], "weight_kg")
        if err:
            return {}, err
        out["weight_kg"] = w
    if "face" in fields:
        v = fields["face"].strip().lower()
        if v:
            try:
                out["face"] = RackFace(v)
            except ValueError:
                return {}, f"bad face {v!r} (expected front/rear/both)"
        else:
            out["face"] = None
    return out, None


def _resolve_ips(
    fields: dict[str, str],
    device_id: int | None,
    current: list[IPAddress],
    refs: _Refs,
) -> tuple[list[IPAddress], list[str], list | None]:
    """ips column -> existing address rows. Unknown tokens are warnings,
    not errors; linking is additive (import never unlinks or creates)."""
    if "ips" not in fields:
        return [], [], None
    tokens, bad = _ip_tokens(fields["ips"] or "")
    warns = [f"unknown ip '{t}'" for t in bad]
    rows: list[IPAddress] = []
    for t in tokens:
        ip = refs.ip_by_addr.get(t)
        if ip is None:
            warns.append(f"unknown ip '{t}'")
        else:
            rows.append(ip)
            if ip.device_id is not None and ip.device_id != device_id:
                other = refs.devices_by_id.get(ip.device_id)
                warns.append(
                    f"ip {t} moves from "
                    f"'{(other.name if other else ip.device_id)}'"
                )
    if device_id is None:
        return rows, warns, None
    old = sorted(ip_display(i.address) or "" for i in current)
    new = sorted({*old, *[ip_display(i.address) or "" for i in rows]})
    return rows, warns, ([" ".join(old), " ".join(new)] if old != new else None)


def _placement_candidate(
    device_fields_dict: dict, patch: dict, rack_id: int
) -> Device:
    """Merged post-patch Device for the occupancy simulation — the same
    blend apply_device_patch builds before check_placement."""
    merged = {**device_fields_dict, **patch}
    merged.pop("rack_id", None)
    merged["u_height"] = merged.get("u_height") or 1
    merged["face"] = merged.get("face") or RackFace.FRONT
    return Device(rack_id=rack_id, **merged)


def _sim_placement(
    p: Planned,
    occ: _Occupancy,
    rack: Rack,
    cand: Device,
    exclude_id: int | None,
) -> bool:
    """check_placement -> error row on the plan. Shared by creates and
    update simulations."""
    try:
        check_placement(rack, occ.devices(rack.id), cand, exclude_id=exclude_id)
    except IPAMError as e:
        p.ok, p.action, p.detail = False, "error", str(e)
        return False
    return True


def _site_diff_name(refs: _Refs, site_id: int | None) -> str | None:
    s = refs.sites_by_id.get(site_id) if site_id is not None else None
    return s.name if s else None


def _rack_diff_name(refs: _Refs, rack_id: int | None) -> str | None:
    r = refs.racks_by_id.get(rack_id) if rack_id is not None else None
    return r.name if r else None


def _carrier_diff_name(refs: _Refs, carrier_id: int | None) -> str | None:
    d = refs.devices_by_id.get(carrier_id) if carrier_id is not None else None
    return d.name if d else None


def _plan_rack_level(
    num: int,
    fields: dict[str, str],
    refs: _Refs,
    occ: _Occupancy,
    on_match: str,
    unracked_on_missing: bool,
    *,
    skipped_rack_ids: frozenset[int] = frozenset(),
    replace_rack_ids: frozenset[int] = frozenset(),
    scope_names_to_rack: bool = False,
) -> Planned:
    """Pass A: rows without a `carrier` value — rack-level devices,
    unracked inventory, and carrier trays."""
    # Reference resolution first — site scopes both matching and racks.
    if "site" in fields and (fields["site"] or "").strip():
        site, err = _resolve_named(
            fields["site"], refs.sites_by_id, refs.sites_by_name, "site"
        )
        if err:
            return _err(num, err)
        site_id = site.id
    else:
        site_id = None
    group_broken = ""
    if "rack_group" in fields and (fields["rack_group"] or "").strip():
        group, err = _resolve_named(
            fields["rack_group"], refs.groups_by_id, refs.groups_by_name,
            "rack_group",
        )
        if err:
            if not (unracked_on_missing and "ambiguous" not in err):
                return _err(num, err)
            # The qualifier is broken — the whole placement claim is void,
            # so the rack cell isn't trusted either: unracked inventory.
            group_broken = err
            group_id = None
        else:
            group_id = group.id
    else:
        group_id = None

    rack: Rack | None = None
    rack_note = f"{group_broken} — unracked" if group_broken else ""
    if "rack" in fields and not group_broken:  # group_broken: chain void → unracked
        v = (fields["rack"] or "").strip()
        if v:
            rack, err = _resolve_rack(v, site_id, group_id, refs)
            if err:
                if unracked_on_missing and "ambiguous" not in err:
                    rack_note = f"{err} — unracked"
                else:
                    return _err(num, err)
        # blank cell = explicit unrack (update) / unracked inventory (create)

    # A rack frozen by the enclosing bundle's on_existing=skip swallows
    # every row aimed at it — the whole subtree stays untouched.
    if rack is not None and rack.id in skipped_rack_ids:
        return Planned(
            row=num, ok=True, action="skip",
            detail=f"rack '{rack.name}' untouched (on_existing=skip)",
        )

    scalars, err = _scalars(fields)
    if err:
        return _err(num, err)
    if rack_note:
        # Forced unracked — a bare u_position/slot can't place anything.
        scalars.pop("u_position", None)
        scalars.pop("slot", None)

    device, how, merr = _match(
        fields, site_id, refs,
        rack.id if scope_names_to_rack and rack is not None else None,
    )
    if merr:
        return _err(num, merr)

    name = (fields.get("name") or "").strip()

    # ---- matched row: skip or update --------------------------------
    if device is not None:
        # replace_devices unracks this rack's occupants at commit — a
        # matched occupant row must re-place it or it would land as
        # unracked inventory even under on_match=skip.
        replaced = (
            device.carrier_id is None
            and device.rack_id in replace_rack_ids
        )
        if on_match == "skip" and not replaced:
            return Planned(
                row=num, ok=True, action="skip",
                detail=f"exists (matched by {how})", device=device,
            )
        if on_match == "skip":
            # placement-only patch: attributes stay untouched (skip), the
            # file's placement cells re-rack the device.
            patch = {}
            if "rack" in fields:
                patch["rack_id"] = rack.id if rack else None
                for k in ("u_position", "u_height", "face"):
                    if k in scalars:
                        patch[k] = scalars[k]
                if "carrier" in fields:
                    patch["carrier_id"] = None
                    patch["slot"] = None
        else:
            patch = dict(scalars)
            if name:
                patch["name"] = name
            if "site" in fields:
                patch["site_id"] = site_id
            if "rack" in fields:
                patch["rack_id"] = rack.id if rack else None
            # carrier column present-but-blank unmounts; carrier-with-value
            # rows never reach pass A.
            if "carrier" in fields and not (fields["carrier"] or "").strip():
                patch["carrier_id"] = None
                patch["slot"] = None
        diff = _update_diff(device, patch, refs)
        ip_rows, ip_warns, ip_diff = _resolve_ips(
            fields, device.id, refs.device_ips.get(device.id, []), refs
        )
        if ip_diff:
            diff["ips"] = ip_diff
        detail = f"update (matched by {how})" if diff else f"identical (matched by {how})"
        if replaced and not diff:
            detail = (
                "re-placed after replace_devices unrack"
                if patch.get("rack_id") is not None
                else "unracked by replace_devices"
            )
        if rack_note:
            detail += f" — {rack_note}"
        if ip_warns:
            detail += "; " + "; ".join(ip_warns)
        p = Planned(
            row=num, ok=True,
            action="update"
            if (diff or (replaced and patch.get("rack_id") is not None))
            else "skip",
            detail=detail, diff=diff or None,
            device=device, patch=patch or None, ip_rows=ip_rows,
        )
        # Simulate the placement consequence for later rows + validation.
        if p.patch and (
            p.patch.keys() & _PLACEMENT_KEYS or "slot_layout" in p.patch
        ):
            if not _sim_update_placement(p, p.patch, device, occ, refs):
                return p
        return p

    # ---- new row -----------------------------------------------------
    if not name:
        return _err(num, "name required")
    create: dict = dict(scalars)
    create["name"] = name
    create["site_id"] = site_id
    if rack is not None:
        create["rack_id"] = rack.id
        if scalars.get("u_position") is None:
            return _err(
                num, f"rack '{rack.name}' given but u_position is missing"
            )
        create["u_position"] = scalars.get("u_position")
        create["u_height"] = scalars.get("u_height") or 1
        create["face"] = scalars.get("face") or RackFace.FRONT
    else:
        create["rack_id"] = None
        if scalars.get("u_position") is not None or scalars.get("slot") is not None:
            return _err(num, "set rack to place the device")
        create["u_height"] = scalars.get("u_height") or 1
        create["face"] = scalars.get("face") or RackFace.FRONT
    ip_rows, ip_warns, _ = _resolve_ips(fields, None, [], refs)
    detail = f"create '{name}'"
    if rack_note:
        detail += f" — {rack_note}"
    if ip_warns:
        detail += "; " + "; ".join(ip_warns)
    p = Planned(
        row=num, ok=True, action="create", detail=detail,
        create_data=create, ip_rows=ip_rows,
    )
    if rack is not None:
        # negative temp id lets pass-B children name this row as carrier
        cand = Device(
            rack_id=rack.id, id=-num, name=name,
            u_position=create["u_position"], u_height=create["u_height"],
            face=create["face"], carrier_id=None,
            slot=scalars.get("slot"),
            slot_layout=create.get("slot_layout"),
        )
        if not _sim_placement(p, occ, rack, cand, None):
            return p
        occ.add(cand)
    return p


def _update_diff(device: Device, patch: dict, refs: _Refs) -> dict:
    """{field: [old, new]} over patch keys that actually change — the
    honest preview. FKs display as names, enums as values."""
    diff: dict = {}
    _NAMED = {
        "site_id": lambda i: _site_diff_name(refs, i),
        "rack_id": lambda i: _rack_diff_name(refs, i),
        "carrier_id": lambda i: _carrier_diff_name(refs, i),
    }
    for k, v in patch.items():
        old = getattr(device, k, None)
        new = v
        if k == "weight_kg" and old is not None:
            old = float(old)
        if old == new:
            continue
        if k in _NAMED:
            diff[k[:-3]] = [_NAMED[k](old), _NAMED[k](v)]
        elif isinstance(old, RackFace) or isinstance(new, RackFace):
            diff[k] = [
                old.value if isinstance(old, RackFace) else old,
                new.value if isinstance(new, RackFace) else new,
            ]
        else:
            diff[k] = [old, new]
    return diff


def _sim_update_placement(
    p: Planned, patch: dict, device: Device, occ: _Occupancy, refs: _Refs
) -> bool:
    """Apply an update's placement to the simulated occupancy: merge onto
    the device, check_placement, then keep the candidate as the current
    occupant so later batch rows see the post-move state."""
    target_rack_id = patch.get("rack_id", device.rack_id)
    if target_rack_id is None:
        # unrack — device and its mounted children leave occupancy.
        occ.remove(device.id)
        for c in list(occ.current.values()):
            if c.carrier_id == device.id:
                occ.remove(c.id)
        return True
    rack = refs.racks_by_id.get(target_rack_id)
    if rack is None:
        p.ok, p.action, p.detail = False, "error", f"Rack {target_rack_id} not found"
        return False
    cand = _placement_candidate(device_fields(device), patch, rack.id)
    # _DEVICE_FIELD_NAMES has no id — keep it so carrier children resolve
    # the moved carrier (and occ bookkeeping keys on the real id).
    cand.id = device.id
    if cand.u_position is None and cand.carrier_id is None:
        p.ok, p.action, p.detail = (
            False, "error",
            "u_position is required unless the device mounts into a carrier",
        )
        return False
    if not _sim_placement(p, occ, rack, cand, exclude_id=device.id):
        return False
    # Carrier children mirror the carrier's rack/span/face in the sim —
    # same behaviour apply_device_patch has at commit time.
    for c in list(occ.current.values()):
        if c.carrier_id == device.id:
            child = Device(
                rack_id=cand.rack_id,
                id=c.id,
                name=c.name,
                u_position=cand.u_position,
                u_height=c.u_height,
                face=cand.face,
                carrier_id=c.carrier_id,
                slot=c.slot,
            )
            occ.replace(c.id, child)
    occ.replace(device.id, cand)
    return True


def _find_carrier(
    val: str,
    rack: Rack | None,
    occ: _Occupancy,
    pending_carriers: dict[tuple[int, str], Planned],
    refs: _Refs,
) -> tuple[Device | Planned | None, str | None]:
    """carrier cell -> the carrier row. '#id' resolves a stored device;
    names resolve inside the same rack across occupants + batch carriers."""
    v = val.strip()
    if rid := _parse_id(v):
        d = refs.devices_by_id.get(rid)
        if d is None:
            return None, f"carrier {v} not found"
        if d.slot_layout is None:
            return None, f"'{d.name}' is not a carrier"
        if rack is not None and d.rack_id != rack.id:
            return None, (
                f"carrier '{d.name}' is in another rack — "
                f"leave rack blank or fix it"
            )
        return d, None
    # pending batch carriers first — they shadow same-named DB rows in
    # this file (the file's own carrier is what the author meant).
    if rack is not None:
        if p := pending_carriers.get((rack.id, _fold(v))):
            return p, None
    else:
        pending = [
            p for (rid, n), p in pending_carriers.items() if n == _fold(v)
        ]
        if len(pending) == 1:
            return pending[0], None
        if len(pending) > 1:
            return None, f"carrier '{v}' is ambiguous — add the rack column or use #id"
    cands = (
        [d for d in occ.devices(rack.id) if _fold(d.name or "") == _fold(v)]
        if rack is not None
        else [
            d for d in refs.devices_by_id.values()
            if _fold(d.name or "") == _fold(v)
        ]
    )
    carriers = [d for d in cands if d.slot_layout is not None]
    if len(carriers) == 1:
        return carriers[0], None
    if len(carriers) > 1:
        return None, f"carrier '{v}' is ambiguous — use #id"
    if cands:
        return None, f"'{v}' is not a carrier"
    if rack is not None:
        # Occupancy missed the name — the carrier may still be stored in
        # this rack but dropped from the simulation because the enclosing
        # bundle's replace_devices unracks it. Resolve it so _plan_child
        # can report that honestly instead of a bare "not found".
        stored = [
            d
            for d in refs.devices_by_id.values()
            if _fold(d.name or "") == _fold(v)
            and d.rack_id == rack.id
            and d.slot_layout is not None
        ]
        if len(stored) == 1:
            return stored[0], None
        if len(stored) > 1:
            return None, f"carrier '{v}' is ambiguous — use #id"
        # Not in this rack — maybe it exists unracked (a skipped/frozen
        # row, or an earlier unracked salvage). Returning it lets the
        # caller report the honest "is not racked" instead of "not found".
        unracked = [
            d
            for d in refs.devices_by_id.values()
            if _fold(d.name or "") == _fold(v)
            and d.rack_id is None
            and d.slot_layout is not None
        ]
        if len(unracked) == 1:
            return unracked[0], None
        if len(unracked) > 1:
            return None, f"carrier '{v}' is ambiguous — use #id"
    return None, f"carrier '{v}' not found" + (
        " in this rack" if rack is not None else ""
    )


def _plan_unracked_child(
    num: int,
    fields: dict[str, str],
    site_id: int | None,
    refs: _Refs,
    on_match: str,
    note: str,
) -> Planned:
    """unracked_on_missing salvage for a carrier row whose mount is void
    (carrier missing / unracked): the device lands as unracked inventory —
    same shape as pass A's unracked path."""
    scalars, serr = _scalars(fields)
    if serr:
        return _err(num, serr)
    scalars.pop("u_position", None)
    scalars.pop("slot", None)
    device, how, merr = _match(fields, site_id, refs, None)
    if merr:
        return _err(num, merr)
    name = (fields.get("name") or "").strip()
    if device is not None:
        if on_match == "skip":
            return Planned(
                row=num, ok=True, action="skip",
                detail=f"exists (matched by {how})", device=device,
            )
        patch = dict(scalars)
        if name:
            patch["name"] = name
        if "site" in fields:
            patch["site_id"] = site_id
        patch["rack_id"] = None
        patch["carrier_id"] = None
        patch["slot"] = None
        diff = _update_diff(device, patch, refs)
        ip_rows, ip_warns, ip_diff = _resolve_ips(
            fields, device.id, refs.device_ips.get(device.id, []), refs
        )
        if ip_diff:
            diff["ips"] = ip_diff
        detail = (
            f"update (matched by {how})" if diff
            else f"identical (matched by {how})"
        ) + f" — {note}"
        if ip_warns:
            detail += "; " + "; ".join(ip_warns)
        return Planned(
            row=num, ok=True,
            action="update" if diff else "skip",
            detail=detail, diff=diff or None,
            device=device, patch=patch or None, ip_rows=ip_rows,
        )
    if not name:
        return _err(num, "name required")
    create = dict(scalars)
    create["name"] = name
    create["site_id"] = site_id
    create["rack_id"] = None
    create["carrier_id"] = None
    create["slot"] = None
    create["u_height"] = scalars.get("u_height") or 1
    create["face"] = scalars.get("face") or RackFace.FRONT
    ip_rows, ip_warns, _ = _resolve_ips(fields, None, [], refs)
    detail = f"create '{name}' — {note}"
    if ip_warns:
        detail += "; " + "; ".join(ip_warns)
    return Planned(
        row=num, ok=True, action="create", detail=detail,
        create_data=create, ip_rows=ip_rows,
    )


def _plan_child(
    num: int,
    fields: dict[str, str],
    refs: _Refs,
    occ: _Occupancy,
    on_match: str,
    unracked_on_missing: bool,
    pending_carriers: dict[tuple[int, str], Planned],
    *,
    skipped_rack_ids: frozenset[int] = frozenset(),
    replace_rack_ids: frozenset[int] = frozenset(),
    scope_names_to_rack: bool = False,
) -> Planned:
    """Pass B: rows with a `carrier` value — mount into a carrier slot.
    Children inherit rack/u/face from the carrier; rack on the row must
    agree when given."""
    if "site" in fields and (fields["site"] or "").strip():
        site, err = _resolve_named(
            fields["site"], refs.sites_by_id, refs.sites_by_name, "site"
        )
        if err:
            return _err(num, err)
        site_id = site.id
    else:
        site_id = None
    group_broken = False
    if "rack_group" in fields and (fields["rack_group"] or "").strip():
        group, err = _resolve_named(
            fields["rack_group"], refs.groups_by_id, refs.groups_by_name,
            "rack_group",
        )
        if err:
            if not (unracked_on_missing and "ambiguous" not in err):
                return _err(num, err)
            # Broken qualifier — void the rack cell too; the carrier's own
            # placement decides where the child lands.
            group_broken = True
            group_id = None
        else:
            group_id = group.id
    else:
        group_id = None

    rack: Rack | None = None
    if (
        "rack" in fields
        and not group_broken
        and (fields["rack"] or "").strip()
    ):
        rack, err = _resolve_rack(fields["rack"], site_id, group_id, refs)
        if err:
            if unracked_on_missing and "ambiguous" not in err:
                rack = None
            else:
                return _err(num, err)

    # Frozen racks swallow mount attempts too — the subtree stays put.
    if rack is not None and rack.id in skipped_rack_ids:
        return Planned(
            row=num, ok=True, action="skip",
            detail=f"rack '{rack.name}' untouched (on_existing=skip)",
        )

    carrier, err = _find_carrier(
        fields["carrier"], rack, occ, pending_carriers, refs
    )
    if err:
        if unracked_on_missing and "ambiguous" not in err:
            # mount is void — the child lands as unracked inventory
            return _plan_unracked_child(
                num, fields, site_id, refs, on_match, f"{err} — unracked",
            )
        return _err(num, err)
    # Resolved carrier (DB row or a pending pass-A create/update).
    if isinstance(carrier, Planned):
        carrier_row = carrier.device  # set post-commit; None in plan
        if carrier.create_data is not None:
            c_rack_id = carrier.create_data["rack_id"]
            c_u = carrier.create_data.get("u_position")
            c_face = carrier.create_data.get("face") or RackFace.FRONT
            c_layout = carrier.create_data.get("slot_layout")
            c_u_height = carrier.create_data.get("u_height") or 1
            c_temp_id = -carrier.row
        else:  # matched carrier whose own row re-places it (update)
            base = carrier.device
            patch = carrier.patch or {}
            c_rack_id = patch.get("rack_id", base.rack_id)
            c_u = patch.get("u_position", base.u_position)
            c_face = patch.get("face", base.face) or RackFace.FRONT
            c_layout = patch.get("slot_layout", base.slot_layout)
            c_u_height = patch.get("u_height", base.u_height) or 1
            c_temp_id = base.id
    else:
        carrier_row = carrier
        c_rack_id = carrier.rack_id
        c_u = carrier.u_position
        c_face = carrier.face or RackFace.FRONT
        c_layout = carrier.slot_layout
        c_u_height = carrier.u_height or 1
        c_temp_id = carrier.id
        if (
            c_rack_id in replace_rack_ids
            and carrier.id not in occ.current
        ):
            return _err(
                num,
                f"carrier '{fields['carrier'].strip()}' is unracked by "
                "replace_devices — its row must re-place it first",
            )
    if c_rack_id in skipped_rack_ids:
        return Planned(
            row=num, ok=True, action="skip",
            detail=f"rack '{_rack_diff_name(refs, c_rack_id)}' untouched "
            "(on_existing=skip)",
        )
    if c_rack_id is None:
        if unracked_on_missing:
            return _plan_unracked_child(
                num, fields, site_id, refs, on_match,
                f"carrier '{fields['carrier'].strip()}' is not racked — "
                "unracked",
            )
        if on_match == "skip":
            # The carrier stays unracked (skipped/frozen) — but if the
            # child itself already exists, the row is a skip like any
            # other matched row under on_match=skip.
            device, how, merr = _match(fields, site_id, refs)
            if merr is None and device is not None:
                return Planned(
                    row=num, ok=True, action="skip",
                    detail=f"exists (matched by {how}) — carrier not "
                    "racked, untouched",
                    device=device,
                )
        return _err(num, f"carrier '{fields['carrier'].strip()}' is not racked")
    if rack is not None and rack.id != c_rack_id:
        return _err(
            num,
            f"rack '{rack.name}' disagrees with carrier's rack "
            f"'{_rack_diff_name(refs, c_rack_id)}'",
        )
    rack = refs.racks_by_id[c_rack_id]
    if "slot" not in fields or (fields["slot"] or "").strip() == "":
        return _err(num, "slot required for a carrier mount")
    slot, serr = _int_field(fields["slot"], "slot")
    if serr:
        return _err(num, serr)
    count = SLOT_LAYOUTS.get(c_layout or "")
    if count is None:
        return _err(num, "carrier has no slot layout")
    if slot is None or not 0 <= slot < count:
        return _err(num, f"slot must be 0–{count - 1} for a {c_layout} carrier")

    scalars, err = _scalars(fields)
    if err:
        return _err(num, err)
    if scalars.get("slot_layout"):
        return _err(num, "a carrier can't mount inside another carrier")
    if scalars.get("u_height") and scalars["u_height"] > c_u_height:
        return _err(num, "child is taller than its carrier")

    device, how, merr = _match(
        fields, site_id, refs,
        rack.id if scope_names_to_rack else None,
    )
    if merr:
        return _err(num, merr)
    name = (fields.get("name") or "").strip()

    if device is not None:
        if on_match == "skip":
            return Planned(
                row=num, ok=True, action="skip",
                detail=f"exists (matched by {how})", device=device,
            )
        patch = {f: v for f, v in scalars.items() if f != "u_position"}
        if name:
            patch["name"] = name
        if "site" in fields:
            patch["site_id"] = site_id
        patch["rack_id"] = c_rack_id
        patch["carrier_id"] = c_temp_id
        patch["slot"] = slot
        # face/u inherit — keep patch honest like apply_device_patch does.
        patch["face"] = c_face
        patch["u_position"] = c_u
        diff = _update_diff(device, patch, refs)
        ip_rows, ip_warns, ip_diff = _resolve_ips(
            fields, device.id, refs.device_ips.get(device.id, []), refs
        )
        if ip_diff:
            diff["ips"] = ip_diff
        detail = f"update (matched by {how})" if diff else f"identical (matched by {how})"
        if ip_warns:
            detail += "; " + "; ".join(ip_warns)
        p = Planned(
            row=num, ok=True,
            action="update" if diff else "skip",
            detail=detail, diff=diff or None,
            device=device, patch=patch, ip_rows=ip_rows,
            carrier_parent=carrier if isinstance(carrier, Planned) else None,
        )
        cand = Device(
            rack_id=rack.id, id=device.id, name=device.name,
            u_position=c_u, u_height=scalars.get("u_height") or device.u_height or 1,
            face=c_face, carrier_id=c_temp_id, slot=slot,
        )
        if not _sim_placement(p, occ, rack, cand, exclude_id=device.id):
            return p
        occ.replace(device.id, cand)
        return p

    if not name:
        return _err(num, "name required")
    create = {f: v for f, v in scalars.items() if f != "u_position"}
    create["name"] = name
    create["site_id"] = site_id
    create["rack_id"] = rack.id
    create["carrier_id"] = c_temp_id
    create["slot"] = slot
    create["u_position"] = c_u
    create["face"] = c_face
    create["u_height"] = scalars.get("u_height") or 1
    ip_rows, ip_warns, _ = _resolve_ips(fields, None, [], refs)
    detail = f"create '{name}' on carrier"
    if ip_warns:
        detail += "; " + "; ".join(ip_warns)
    p = Planned(
        row=num, ok=True, action="create", detail=detail,
        create_data=create, ip_rows=ip_rows,
        carrier_parent=carrier if isinstance(carrier, Planned) else None,
    )
    cand = Device(
        rack_id=rack.id, id=-num, name=name,
        u_position=c_u, u_height=create["u_height"],
        face=c_face, carrier_id=c_temp_id, slot=slot,
        slot_layout=None,
    )
    if not _sim_placement(p, occ, rack, cand, None):
        return p
    occ.add(cand)
    return p


# ---------------------------------------------------------------------------
# Commit
# ---------------------------------------------------------------------------


async def apply_device_import(
    session: AsyncSession,
    planned: list[Planned],
    *,
    rack_ids: dict[int, int] | None = None,
    site_ids: dict[int, int] | None = None,
) -> None:
    """Write the ok rows in one transaction. Creates go through the create
    path's check_placement; updates through apply_device_patch — the
    changelog then covers imports for free. Raises IPAMError on a
    commit-time conflict (the caller turns it into an error row count or
    rolls everything back).

    rack_ids/site_ids translate negative temp ids a bundle import staged
    for rows it created earlier in the same transaction."""
    temp_ids: dict[int, Device] = {}  # plan row -> flushed carrier/device
    rack_ids = rack_ids or {}
    site_ids = site_ids or {}

    def _carrier_id(p: Planned, raw: int | None) -> int | None:
        if raw is None or raw >= 0:
            return raw
        parent = temp_ids.get(-raw)
        return parent.id if parent is not None else raw

    def _translate(d: dict) -> dict:
        d = dict(d)
        if d.get("rack_id") in rack_ids:
            d["rack_id"] = rack_ids[d["rack_id"]]
        if d.get("site_id") in site_ids:
            d["site_id"] = site_ids[d["site_id"]]
        return d

    # Pass A first — carriers get real ids before children mount.
    order = sorted(planned, key=lambda p: p.row)
    for p in order:
        if not p.ok or p.action == "skip":
            continue
        if p.carrier_parent is not None:
            continue  # pass B
        if p.create_data is not None:
            data = _translate(p.create_data)
            data["carrier_id"] = _carrier_id(p, data.get("carrier_id"))
            d = Device(**data, source="import")
            if d.rack_id is not None:
                rack = await session.get(Rack, d.rack_id)
                check_placement(rack, await rack_devices(session, rack.id), d)
            session.add(d)
            p.device = d
        elif p.patch is not None and p.device is not None:
            patch = _translate(p.patch)
            patch["carrier_id"] = _carrier_id(p, patch.get("carrier_id"))
            await apply_device_patch(session, p.device, patch)
        await session.flush()
        temp_ids[p.row] = p.device
    for p in order:
        if not p.ok or p.action == "skip" or p.carrier_parent is None:
            continue
        if p.create_data is not None:
            data = _translate(p.create_data)
            data["carrier_id"] = _carrier_id(p, data.get("carrier_id"))
            d = Device(**data, source="import")
            rack = await session.get(Rack, d.rack_id)
            check_placement(rack, await rack_devices(session, rack.id), d)
            session.add(d)
            p.device = d
        elif p.patch is not None and p.device is not None:
            patch = _translate(p.patch)
            patch["carrier_id"] = _carrier_id(p, patch.get("carrier_id"))
            await apply_device_patch(session, p.device, patch)
        await session.flush()
    for p in order:
        if not p.ok or p.action == "skip" or p.device is None:
            continue
        for ip in p.ip_rows:
            ip.device_id = p.device.id
