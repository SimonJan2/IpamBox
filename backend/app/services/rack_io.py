"""Rack/group bundle export + multi-sheet smart import (V5C).

A rack isn't a row — it's a tree: group -> racks -> devices (-> carriers ->
children, -> interfaces -> cables). The flat CSV covers the rack list; the
.xlsx bundle carries the whole tree so a group can move between installs,
clone a site build-out, or be bulk-edited in a spreadsheet. FK columns
export as NAMES (site/group/rack/device/interface) because ids are
meaningless across installs; `id` still pins same-install re-imports.

Import is V5B-shaped: raw file + ?filename=, dry-run preview, one
transaction at commit. Sheets are detected by header signature (canonical
export headers + EN/HE aliases); unknown sheets warn and are ignored — a
flat racks CSV works as a racks-only import. Sites named anywhere in the
bundle are created when missing: the round-trip contract says a group
export rebuilds the same tree into an empty install, and the site is part
of the tree's anchor.

Matching: groups by name; racks by name+site (name alone when
unambiguous); devices by the V5B precedence with `name` scoped to the
target rack first; interfaces by device+name; cables by resolved endpoint
pair. `on_existing` is decided per matched rack — skip freezes the whole
subtree, update patches rack + devices, merge keeps occupants and only
adds. `replace_devices` unracks a rack's current occupants before the
device pass (they survive as unracked inventory — import never deletes).
"""
import io
from dataclasses import dataclass, field
from typing import Any

import openpyxl
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cabling import (
    Cable,
    CableKind,
    DeviceInterface,
    InterfaceKind,
)
from app.models.device import Device
from app.models.ip_address import IPAddress
from app.models.rack import Rack, RackGroup
from app.models.site import Site
from app.schemas.common import ip_display
from app.services.device_io import (
    DEVICE_EXPORT_COLUMNS,
    DEVICE_IMPORT_FIELDS,
    Planned,
    _float_field,
    _fold,
    _int_field,
    _name_map,
    _parse_id,
    _resolve_named,
    apply_device_import,
    apply_mapping_overrides,
    auto_map_fields,
    auto_map_headers,
    device_export_rows,
    plan_device_import,
    sheet_rows,
)
from app.services.ipam import slugify
from app.services.racks import (
    apply_device_patch,
    rack_devices,
    stamp_rack_stats,
)
from app.services.workbook.normalize import norm_header, norm_mac
from app.services.workbook.reader import load_upload

# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------

# Column orders are a contract — the importer recognizes all of them.
RACK_EXPORT_COLUMNS = [
    "id", "name", "site", "group", "group_position", "room", "height_u",
    "width", "device_count", "used_u", "free_u", "power_w", "weight_kg",
    "description", "notes", "created_at",
]
GROUP_EXPORT_COLUMNS = ["id", "name", "site", "description", "created_at"]
IFACE_EXPORT_COLUMNS = [
    "device", "name", "kind", "speed_mbps", "mac_address", "connected_ip",
]
CABLE_EXPORT_COLUMNS = [
    "a_device", "a_interface", "b_device", "b_interface", "kind", "color",
    "label", "length_m",
]


async def rack_export_rows(
    session: AsyncSession, racks: list[Rack]
) -> list[list]:
    """Flat rack rows in RACK_EXPORT_COLUMNS order. Callers stamp
    stamp_rack_stats() first — used_u/power_w/weight_kg are transient."""
    site_ids = {r.site_id for r in racks if r.site_id is not None}
    group_ids = {r.group_id for r in racks if r.group_id is not None}
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
    rows = []
    for r in racks:
        site = sites.get(r.site_id)
        group = groups.get(r.group_id)
        rows.append([
            r.id,
            r.name,
            site.name if site else None,
            group.name if group else None,
            r.group_position,
            r.room,
            r.height_u,
            r.width,
            r.device_count,
            r.used_u,
            r.height_u - r.used_u,
            r.power_w,
            r.weight_kg,
            r.description,
            r.notes,
            r.created_at.isoformat() if r.created_at else None,
        ])
    return rows


async def _group_export_rows(
    session: AsyncSession, groups: list[RackGroup]
) -> list[list]:
    site_ids = {g.site_id for g in groups if g.site_id is not None}
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
    return [
        [
            g.id,
            g.name,
            (sites[g.site_id].name if g.site_id in sites else None),
            g.description,
            g.created_at.isoformat() if g.created_at else None,
        ]
        for g in groups
    ]


async def bundle_sheets(
    session: AsyncSession, racks: list[Rack]
) -> list[tuple[str, list[str], list[list]]]:
    """Ordered (sheet, header, rows): groups, racks, devices, plus
    interfaces/cables when the exported devices have any. `racks` order is
    the caller's (group_position for group files, list order for views)."""
    await stamp_rack_stats(session, racks)
    rack_ids = [r.id for r in racks]
    group_ids = sorted({r.group_id for r in racks if r.group_id is not None})
    groups = (
        list(
            (
                await session.execute(
                    select(RackGroup)
                    .where(RackGroup.id.in_(group_ids))
                    .order_by(RackGroup.name, RackGroup.id)
                )
            ).scalars()
        )
        if group_ids
        else []
    )
    devices = (
        list(
            (
                await session.execute(
                    select(Device)
                    .where(Device.rack_id.in_(rack_ids))
                    .order_by(Device.rack_id, Device.u_position, Device.id)
                )
            ).scalars()
        )
        if rack_ids
        else []
    )
    sheets: list[tuple[str, list[str], list[list]]] = [
        ("groups", GROUP_EXPORT_COLUMNS, await _group_export_rows(session, groups)),
        ("racks", RACK_EXPORT_COLUMNS, await rack_export_rows(session, racks)),
        ("devices", DEVICE_EXPORT_COLUMNS, await device_export_rows(session, devices)),
    ]
    if not devices:
        return sheets
    dev_ids = [d.id for d in devices]
    dev_names = {d.id: d.name for d in devices}
    ifaces = list(
        (
            await session.execute(
                select(DeviceInterface)
                .where(DeviceInterface.device_id.in_(dev_ids))
                .order_by(
                    DeviceInterface.device_id,
                    DeviceInterface.position,
                    DeviceInterface.id,
                )
            )
        ).scalars()
    )
    if not ifaces:
        return sheets
    ip_ids = {i.connected_ip_id for i in ifaces if i.connected_ip_id is not None}
    ips = (
        {
            r.id: ip_display(r.address)
            for r in (
                await session.execute(
                    select(IPAddress).where(IPAddress.id.in_(ip_ids))
                )
            ).scalars()
        }
        if ip_ids
        else {}
    )
    iface_by_id = {i.id: i for i in ifaces}
    sheets.append((
        "interfaces",
        IFACE_EXPORT_COLUMNS,
        [
            [
                dev_names.get(i.device_id),
                i.name,
                i.kind.value if i.kind else None,
                i.speed_mbps,
                i.mac_address,
                ips.get(i.connected_ip_id),
            ]
            for i in ifaces
        ],
    ))
    iface_ids = [i.id for i in ifaces]
    cables = list(
        (
            await session.execute(
                select(Cable).where(
                    or_(
                        Cable.a_interface_id.in_(iface_ids),
                        Cable.b_interface_id.in_(iface_ids),
                    )
                )
            )
        ).scalars()
    )
    # Only cables whose BOTH ends are on exported devices can round-trip —
    # name-addressed endpoints can't resolve a device the bundle omits.
    cables = [
        c
        for c in cables
        if c.a_interface_id in iface_by_id and c.b_interface_id in iface_by_id
    ]
    if cables:
        sheets.append((
            "cables",
            CABLE_EXPORT_COLUMNS,
            [
                [
                    dev_names.get(iface_by_id[c.a_interface_id].device_id),
                    iface_by_id[c.a_interface_id].name,
                    dev_names.get(iface_by_id[c.b_interface_id].device_id),
                    iface_by_id[c.b_interface_id].name,
                    c.kind.value if c.kind else None,
                    c.color,
                    c.label,
                    float(c.length_m) if c.length_m is not None else None,
                ]
                for c in cables
            ],
        ))
    return sheets


def workbook_response(
    filename: str, sheets: list[tuple[str, list[str], list[list]]]
) -> StreamingResponse:
    """Multi-sheet xlsx — the bundle counterpart of device_io's
    single-sheet xlsx_response."""
    wb = openpyxl.Workbook()
    for i, (name, header, rows) in enumerate(sheets):
        ws = wb.active if i == 0 else wb.create_sheet()
        ws.title = name
        ws.append(header)
        for row in rows:
            ws.append(list(row))
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ---------------------------------------------------------------------------
# Import — sheet detection
# ---------------------------------------------------------------------------

GROUP_IMPORT_FIELDS = ["id", "name", "site", "description"]
RACK_IMPORT_FIELDS = [
    "id", "name", "site", "group", "group_position", "room", "height_u",
    "width", "description", "notes",
]
IFACE_IMPORT_FIELDS = [
    "device", "name", "kind", "speed_mbps", "mac_address", "connected_ip",
]
CABLE_IMPORT_FIELDS = [
    "a_device", "a_interface", "b_device", "b_interface", "kind", "color",
    "label", "length_m",
]

_GROUP_ALIASES = {
    "id": {"id", "#id", "pk", "group id", "rack group id"},
    "name": {
        "name", "group", "group name", "rack group", "rack_group",
        "rack group name", "row", "row name",
        "שם", "קבוצה", "שורה", "קבוצת ארונות", "שורת ארונות", "שם קבוצה",
    },
    "site": {"site", "site_name", "site name", "אתר", "מיקום", "שם אתר"},
    "description": {"description", "desc", "details", "תיאור"},
}
_RACK_ALIASES = {
    "id": {"id", "#id", "pk", "rack id"},
    "name": {
        "name", "rack", "rack_name", "rack name", "cabinet",
        "שם", "ארון", "רק", "ארון תקשורת", "שם ארון",
    },
    "site": {"site", "site_name", "site name", "אתר", "מיקום", "שם אתר"},
    "group": {
        "group", "rack_group", "rack group", "group name", "row",
        "קבוצה", "שורה", "קבוצת ארונות", "שורת ארונות",
    },
    "group_position": {
        "group_position", "group position", "position", "pos",
        "position in group", "מיקום בשורה",
    },
    "room": {"room", "חדר"},
    "height_u": {
        "height_u", "height", "u", "height u", "rack height", "height (u)",
        "גובה", "גובה u", "גובה ארון",
    },
    "width": {"width", "rail width", "רוחב"},
    "description": {"description", "desc", "details", "תיאור"},
    "notes": {"notes", "note", "comment", "comments", "הערות", "הערה"},
}
_IFACE_ALIASES = {
    "device": {"device", "device_name", "device name", "מכשיר", "שם מכשיר"},
    "name": {
        "name", "interface", "interface_name", "interface name", "port",
        "port name", "שם", "שם ממשק", "פורט",
    },
    "kind": {"kind", "type", "interface_kind", "interface kind", "סוג"},
    "speed_mbps": {
        "speed_mbps", "speed", "speed mbps", "mbps", "speed (mbps)", "מהירות",
    },
    "mac_address": {
        "mac_address", "mac", "mac address", "מאק", "כתובת mac", "כתובת מאק",
    },
    "connected_ip": {
        "connected_ip", "connected ip", "ip", "ip_address", "ip address",
        "כתובת ip", "אייפי",
    },
}
_CABLE_ALIASES = {
    "a_device": {"a_device", "a device", "device a", "a side", "a_side", "מכשיר א"},
    "a_interface": {
        "a_interface", "a interface", "interface a", "a port", "a_port",
        "ממשק א", "פורט א",
    },
    "b_device": {"b_device", "b device", "device b", "b side", "b_side", "מכשיר ב"},
    "b_interface": {
        "b_interface", "b interface", "interface b", "b port", "b_port",
        "ממשק ב", "פורט ב",
    },
    "kind": {"kind", "cable_kind", "cable kind", "סוג"},
    "color": {"color", "colour", "cable color", "צבע"},
    "label": {"label", "cable label", "תווית"},
    "length_m": {
        "length_m", "length", "length m", "length (m)", "meters", "אורך",
    },
}

_FAMILY_ALIASES = {
    "groups": _GROUP_ALIASES,
    "racks": _RACK_ALIASES,
    "interfaces": _IFACE_ALIASES,
    "cables": _CABLE_ALIASES,
}
_FAMILY_FIELDS = {
    "groups": GROUP_IMPORT_FIELDS,
    "racks": RACK_IMPORT_FIELDS,
    "devices": DEVICE_IMPORT_FIELDS,
    "interfaces": IFACE_IMPORT_FIELDS,
    "cables": CABLE_IMPORT_FIELDS,
}
# Export-only columns map to None quietly rather than flagging unmapped.
_FAMILY_IGNORED = {
    "groups": {"created_at"},
    "racks": {
        "device_count", "used_u", "free_u", "power_w", "weight_kg",
        "created_at", "updated_at",
    },
    "devices": {
        "ip_count", "interface_count", "cabled_count", "source",
        "created_at", "updated_at",
    },
    "interfaces": {"position"},
    "cables": set(),
}
# Fields that tell a family apart from the others (name/site/id are shared).
_IFACE_DISTINCT = {"kind", "speed_mbps", "connected_ip"}
_DEVICE_DISTINCT = {
    "device_type", "manufacturer", "model", "category", "serial_number",
    "mac_address", "rack", "rack_group", "u_position", "u_height", "face",
    "carrier", "slot", "slot_layout", "watts", "weight_kg", "ips",
}
_RACK_DISTINCT = {"group", "group_position", "room", "height_u", "width"}
_CABLE_SIGNATURE = {"a_device", "a_interface", "b_device", "b_interface"}


def _family_alias_to_field(family: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for f, aliases in _FAMILY_ALIASES[family].items():
        out.setdefault(f, f)
        for a in aliases:
            out[a] = f
    return out


_FAMILIES = ("groups", "racks", "devices", "interfaces", "cables")


def _min_sig(family: str, mapped: set[str]) -> bool:
    if family == "cables":
        return _CABLE_SIGNATURE <= mapped
    if family == "interfaces":
        return {"device", "name"} <= mapped
    return "name" in mapped


def classify_sheet(name: str, headers: list[str]) -> str | None:
    """Header signature -> sheet family. Our own exports name their sheets
    after the family — an exact name match wins when its minimal signature
    holds; otherwise the distinctive-column test decides (cables >
    interfaces > devices > racks > groups so shared name/site/id columns
    can't mislead)."""
    normed = [norm_header(h) for h in headers]

    def mapped(family: str) -> set[str]:
        if family == "devices":
            cmap, _ = auto_map_headers(headers)
            return {f for f in cmap.values() if f is not None}
        a2f = _family_alias_to_field(family)
        return {a2f[n] for n in normed if n in a2f}

    sigs = {fam: mapped(fam) for fam in _FAMILIES}
    hint = norm_header(name or "")
    if hint in _FAMILIES and _min_sig(hint, sigs[hint]):
        return hint
    if _CABLE_SIGNATURE <= sigs["cables"]:
        return "cables"
    if {"device", "name"} <= sigs["interfaces"] and (
        sigs["interfaces"] & _IFACE_DISTINCT
    ):
        return "interfaces"
    if "name" in sigs["devices"] and sigs["devices"] & _DEVICE_DISTINCT:
        return "devices"
    if "name" in sigs["racks"] and sigs["racks"] & _RACK_DISTINCT:
        return "racks"
    if "name" in sigs["groups"]:
        return "groups"
    return None


@dataclass
class BundleSheet:
    """One parsed workbook sheet: family, auto-map, header-keyed rows."""
    name: str
    family: str | None
    headers: list[str]
    rows: list[tuple[int, dict[str, str]]]
    col_map: dict[str, str | None] = field(default_factory=dict)
    unmapped: list[str] = field(default_factory=list)
    warning: str | None = None

    def frows(self) -> list[tuple[int, dict[str, str]]]:
        """(row_no, {field: cell}) — same projection plan_device_import
        does for the standalone importer."""
        return [
            (
                num,
                {
                    f: row[h]
                    for h, f in self.col_map.items()
                    if f is not None and row.get(h) is not None
                },
            )
            for num, row in self.rows
        ]


def parse_bundle(payload: bytes, filename: str) -> list[BundleSheet]:
    """xlsx/CSV -> sheets classified by header signature. Unknown or
    empty sheets are kept with a warning (preview reports them) — the
    caller 422s when nothing at all is importable."""
    try:
        matrices = load_upload(payload, filename)
    except Exception as e:
        raise HTTPException(422, f"cannot parse file: {e}")
    if not matrices:
        raise HTTPException(422, "empty file or missing header row")
    sheets: list[BundleSheet] = []
    for m in matrices:
        try:
            headers, rows = sheet_rows(m)
        except HTTPException:
            sheets.append(
                BundleSheet(
                    name=m.name, family=None, headers=[], rows=[],
                    warning=f"sheet '{m.name}' ignored (empty)",
                )
            )
            continue
        family = classify_sheet(m.name, headers)
        sheet = BundleSheet(name=m.name, family=family, headers=headers, rows=rows)
        if family is None:
            sheet.warning = (
                f"sheet '{m.name}' ignored (unrecognized headers — "
                "expected groups/racks/devices/interfaces/cables)"
            )
        elif family == "devices":
            sheet.col_map, sheet.unmapped = auto_map_headers(headers)
        else:
            sheet.col_map, sheet.unmapped = auto_map_fields(
                headers,
                _family_alias_to_field(family),
                _FAMILY_IGNORED.get(family, set()),
            )
        sheets.append(sheet)
    if not any(s.family for s in sheets):
        raise HTTPException(
            422,
            "no importable sheets — expected groups/racks/devices/"
            "interfaces/cables headers",
        )
    return sheets


# ---------------------------------------------------------------------------
# Import — planning
# ---------------------------------------------------------------------------


def _out(row: int, sheet: str, ok: bool, action: str, detail: str,
         diff: dict | None = None) -> dict:
    d = {"row": row, "sheet": sheet, "ok": ok, "action": action,
         "detail": detail}
    if diff:
        d["diff"] = diff
    return d


@dataclass
class _SitePlan:
    name: str
    temp_id: int
    site: Site | None = None


@dataclass
class _GroupPlan:
    row: int
    ok: bool
    action: str
    detail: str
    sheet: str = "groups"
    diff: dict | None = None
    group: RackGroup | None = None
    create: dict | None = None
    patch: dict | None = None
    temp_id: int = 0


@dataclass
class _RackPlan:
    row: int
    ok: bool
    action: str
    detail: str
    sheet: str = "racks"
    diff: dict | None = None
    rack: Rack | None = None
    create: dict | None = None
    patch: dict | None = None
    temp_id: int = 0
    transient: Rack | None = None  # what extra_racks hands the device pass


@dataclass
class _IfacePlan:
    row: int
    ok: bool
    action: str
    detail: str
    sheet: str = "interfaces"
    diff: dict | None = None
    iface: DeviceInterface | None = None
    device_ref: Any = None           # Device | Planned (device sheet row)
    create: dict | None = None       # sans device_id — resolved at commit
    patch: dict | None = None


@dataclass
class _CablePlan:
    row: int
    ok: bool
    action: str
    detail: str
    sheet: str = "cables"
    diff: dict | None = None
    cable: Cable | None = None
    a_ref: Any = None                # DeviceInterface | _IfacePlan
    b_ref: Any = None
    create: dict | None = None       # sans a/b ids — resolved at commit
    patch: dict | None = None


@dataclass
class BundlePlan:
    """Every sheet's verdicts + the commit payload. Pure plan — dry_run
    and commit share it exactly like V5B's Planned list."""
    sites: list[_SitePlan] = field(default_factory=list)
    groups: list[_GroupPlan] = field(default_factory=list)
    racks: list[_RackPlan] = field(default_factory=list)
    devices: list[Planned] = field(default_factory=list)
    # (sheet name, plan) pairs — device rows tag their file sheet
    device_rows: list[tuple[str, Planned]] = field(default_factory=list)
    ifaces: list[_IfacePlan] = field(default_factory=list)
    cables: list[_CablePlan] = field(default_factory=list)
    rows: list[dict] = field(default_factory=list)
    sheets_meta: list[dict] = field(default_factory=list)
    columns: list[dict] = field(default_factory=list)
    unmapped: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    replace_rack_ids: set[int] = field(default_factory=set)

    def counts(self) -> dict:
        c = {"create": 0, "update": 0, "skip": 0, "error": 0}
        for r in self.rows:
            c[r["action"]] += 1
        return c

    def out(self, committed: bool) -> dict:
        return {
            "counts": self.counts(),
            "rows": self.rows,
            "columns": self.columns,
            "unmapped": self.unmapped,
            "sheets": self.sheets_meta,
            "warnings": self.warnings,
            "committed": committed,
        }


def _resolve_site_cell(
    token: str,
    site_res: dict[str, Site | str],
) -> tuple[int | None, str | None]:
    """site cell -> (site_id, error) through the pre-resolved token map —
    planned sites carry their negative temp id."""
    r = site_res.get(token.strip())
    if isinstance(r, str):
        return None, r
    if r is None:
        return None, f"site '{token.strip()}' not found"
    return r.id, None


async def _plan_sites(
    session: AsyncSession,
    sheets: list[BundleSheet],
) -> tuple[list[_SitePlan], dict[str, Site | str]]:
    """Resolve every site token any sheet references; missing names become
    planned creates (the empty-install round-trip). Token -> Site or the
    error string that referencing rows surface."""
    tokens: list[str] = []
    for s in sheets:
        if s.family not in ("groups", "racks", "devices"):
            continue
        for _, fields in s.frows():
            if "site" in fields and (v := fields["site"].strip()):
                tokens.append(v)
    db = list((await session.execute(select(Site))).scalars())
    by_id = {s.id: s for s in db}
    by_name = _name_map(db)
    plans: list[_SitePlan] = []
    res: dict[str, Site | str] = {}
    pending: dict[str, Site] = {}
    for tok in tokens:
        if tok in res:
            continue
        if rid := _parse_id(tok):
            s = by_id.get(rid)
            res[tok] = s if s is not None else f"site '{tok}' not found"
            continue
        fold = _fold(tok)
        if fold in pending:
            res[tok] = pending[fold]
            continue
        cands = by_name.get(fold) or []
        if len(cands) > 1:
            res[tok] = f"site '{tok}' is ambiguous ({len(cands)} matches)"
            continue
        if cands:
            res[tok] = cands[0]
            continue
        # Missing -> planned create (transient row, negative temp id).
        t = Site(id=-(len(plans) + 1), name=tok, slug=slugify(tok))
        pending[fold] = t
        res[tok] = t
        plans.append(_SitePlan(name=tok, temp_id=t.id, site=t))
    return plans, res


async def _plan_groups(
    sheets: list[BundleSheet],
    site_res: dict[str, Site | str],
    groups: list[RackGroup],
    on_existing: str,
) -> tuple[list[_GroupPlan], dict[str, list[RackGroup]], dict[int, RackGroup]]:
    """groups sheet -> plans; returns folded-name + id lookups (incl.
    planned creates) the racks pass resolves `group` cells through."""
    plans: list[_GroupPlan] = []
    by_id: dict[int, RackGroup] = {g.id: g for g in groups}
    by_name: dict[str, list[RackGroup]] = _name_map(groups)
    for sheet in sheets:
        if sheet.family != "groups":
            continue
        for num, fields in sheet.frows():
            name = (fields.get("name") or "").strip()
            if not name and _parse_id(fields.get("id")) is None:
                plans.append(_GroupPlan(
                    num, False, "error", "name required", sheet.name))
                continue
            group: RackGroup | None = None
            if rid := _parse_id(fields.get("id")):
                group = by_id.get(rid)
            if group is None and name:
                cands = by_name.get(_fold(name)) or []
                if len(cands) > 1:
                    plans.append(_GroupPlan(
                        num, False, "error",
                        f"group '{name}' is ambiguous "
                        f"({len(cands)} matches — use #id)", sheet.name))
                    continue
                if cands:
                    group = cands[0]
            if group is not None:
                if on_existing == "update":
                    patch: dict = {}
                    if name:
                        patch["name"] = name
                    if "site" in fields:
                        sid, serr = _resolve_site_cell(
                            fields["site"], site_res
                        )
                        if serr:
                            plans.append(_GroupPlan(
                                num, False, "error", serr, sheet.name))
                            continue
                        patch["site_id"] = sid
                    if "description" in fields:
                        patch["description"] = (
                            fields["description"].strip() or None
                        )
                    diff = {
                        k: [getattr(group, k), v]
                        for k, v in patch.items()
                        if getattr(group, k) != v
                    }
                    plans.append(_GroupPlan(
                        num, True,
                        "update" if diff else "skip",
                        f"update (matched group '{group.name}')"
                        if diff
                        else f"identical (matched group '{group.name}')",
                        sheet.name, diff or None, group, None, patch,
                    ))
                else:
                    plans.append(_GroupPlan(
                        num, True, "skip",
                        f"exists (matched group '{group.name}')",
                        sheet.name, None, group,
                    ))
                continue
            if not name:
                plans.append(_GroupPlan(
                    num, False, "error", "name required", sheet.name))
                continue
            site_id = None
            if "site" in fields and fields["site"].strip():
                site_id, serr = _resolve_site_cell(fields["site"], site_res)
                if serr:
                    plans.append(_GroupPlan(
                        num, False, "error", serr, sheet.name))
                    continue
            t = RackGroup(
                id=-num, name=name, site_id=site_id,
                description=(fields.get("description") or "").strip() or None,
            )
            by_name.setdefault(_fold(name), []).append(t)
            by_id[-num] = t
            plans.append(_GroupPlan(
                num, True, "create", f"create group '{name}'", sheet.name,
                None, None,
                {
                    "name": name,
                    "site_id": site_id,
                    "description": t.description,
                },
                None, -num,
            ))
    return plans, by_name, by_id


def _rack_match(
    name: str,
    site_id: int | None,
    racks_by_name: dict[str, list[Rack]],
) -> tuple[Rack | None, str | None, str | None]:
    """name+site when the row gives a site, name alone when unambiguous —
    ambiguity is an error, never a coin flip."""
    cands = racks_by_name.get(_fold(name)) or []
    if site_id is not None:
        scoped = [r for r in cands if r.site_id == site_id]
        if len(scoped) > 1:
            return None, None, (
                f"rack '{name}' + site is ambiguous "
                f"({len(scoped)} matches — use #id)"
            )
        return (
            (scoped[0], "name+site", None)
            if scoped
            else (None, None, None)
        )
    if len(cands) > 1:
        return None, None, (
            f"rack '{name}' is ambiguous ({len(cands)} matches — "
            "add a site column or use #id)"
        )
    return (cands[0], "name", None) if cands else (None, None, None)


async def _plan_racks(
    session: AsyncSession,
    sheets: list[BundleSheet],
    site_res: dict[str, Site | str],
    groups_by_name: dict[str, list[RackGroup]],
    groups_by_id: dict[int, RackGroup],
    group_override: RackGroup | None,
    on_existing: str,
    warnings: list[str],
) -> tuple[list[_RackPlan], set[int], set[int], dict[str, list[Rack]], dict[int, Rack]]:
    """racks sheet -> plans + (skipped_rack_ids, replace_candidates,
    rack name/id lookups incl. planned creates for the devices pass).

    Positions inside a group are assigned honestly: the file's
    group_position wins when free; a taken slot appends at the row's right
    end with a warning, exactly like joining without a position."""
    db_racks = list((await session.execute(select(Rack))).scalars())
    racks_by_id: dict[int, Rack] = {r.id: r for r in db_racks}
    racks_by_name: dict[str, list[Rack]] = _name_map(db_racks)

    # Occupied group positions — a matched rack's own slot doesn't collide
    # with itself (it's released when we see the row).
    used_pos: dict[int, set[int]] = {}
    for r in db_racks:
        if r.group_id is not None and r.group_position is not None:
            used_pos.setdefault(r.group_id, set()).add(r.group_position)

    plans: list[_RackPlan] = []
    skipped_ids: set[int] = set()
    replace_ids: set[int] = set()
    for sheet in sheets:
        if sheet.family != "racks":
            continue
        for num, fields in sheet.frows():
            name = (fields.get("name") or "").strip()
            # --- site resolution (absent col = don't scope/touch) ---
            site_id: int | None = None
            site_given = "site" in fields
            if site_given and fields["site"].strip():
                site_id, serr = _resolve_site_cell(fields["site"], site_res)
                if serr:
                    plans.append(_RackPlan(num, False, "error", serr, sheet.name))
                    continue
            # --- group resolution (override > cell > absent) ---
            group_id: int | None = None
            group_field_present = False
            if group_override is not None:
                group_id = group_override.id
                group_field_present = True
            elif "group" in fields:
                group_field_present = True
                if fields["group"].strip():
                    g, gerr = _resolve_named(
                        fields["group"], groups_by_id, groups_by_name,
                        "group",
                    )
                    if gerr:
                        plans.append(_RackPlan(
                            num, False, "error", gerr, sheet.name))
                        continue
                    group_id = g.id

            # --- scalars ---
            h, herr = _int_field(fields.get("height_u"), "height_u")
            if herr:
                plans.append(_RackPlan(num, False, "error", herr, sheet.name))
                continue
            if h is not None and not 1 <= h <= 100:
                plans.append(_RackPlan(
                    num, False, "error",
                    f"height_u {h} out of range (1–100)", sheet.name))
                continue
            w, werr = _int_field(fields.get("width"), "width")
            if werr:
                plans.append(_RackPlan(num, False, "error", werr, sheet.name))
                continue
            if w is not None and w not in (10, 19):
                plans.append(_RackPlan(
                    num, False, "error", "width must be 10 or 19",
                    sheet.name))
                continue
            pos, perr = _int_field(
                fields.get("group_position"), "group_position")
            if perr:
                plans.append(_RackPlan(num, False, "error", perr, sheet.name))
                continue
            if pos is not None and pos < 0:
                plans.append(_RackPlan(
                    num, False, "error", "group_position must be >= 0",
                    sheet.name))
                continue

            # --- match ---
            rack: Rack | None = None
            how = ""
            if rid := _parse_id(fields.get("id")):
                rack = racks_by_id.get(rid)
                how = "id"
            if rack is None and name:
                rack, how, merr = _rack_match(name, site_id, racks_by_name)
                if merr:
                    plans.append(_RackPlan(num, False, "error", merr, sheet.name))
                    continue

            def _position_for(
                gid: int | None,
                current: Rack | None,
                patch_or_create: dict,
            ) -> str | None:
                """Assign group_position inside gid; append+warn on
                collision. Returns a warning string or None."""
                if gid is None:
                    return None
                used = used_pos.setdefault(gid, set())
                if current is not None and current.group_id == gid and (
                    current.group_position is not None
                ):
                    used.discard(current.group_position)
                want = pos
                if want is None and current is not None and (
                    current.group_id == gid
                    and current.group_position is not None
                ):
                    return None  # keeps its slot — no patch
                if want is not None and want not in used:
                    used.add(want)
                    patch_or_create["group_position"] = want
                    return None
                top = max(used | {0})
                patch_or_create["group_position"] = top + 1
                used.add(top + 1)
                if want is not None:
                    return (
                        f"group_position {want} is taken in this row — "
                        f"appended at {top + 1}"
                    )
                return None

            if rack is not None:
                if on_existing == "skip":
                    skipped_ids.add(rack.id)
                    plans.append(_RackPlan(
                        num, True, "skip",
                        f"exists (matched by {how})", sheet.name, None,
                        rack,
                    ))
                    continue
                if on_existing == "merge":
                    # keep occupants + attributes — the devices sheet adds
                    # into free Us only (replace_devices still unracks).
                    replace_ids.add(rack.id)
                    plans.append(_RackPlan(
                        num, True, "skip",
                        f"exists (matched by {how}) — occupants kept",
                        sheet.name, None, rack,
                    ))
                    continue
                patch: dict = {}
                if name:
                    patch["name"] = name
                if site_given:
                    patch["site_id"] = site_id
                if "room" in fields:
                    patch["room"] = fields["room"].strip() or None
                if "description" in fields:
                    patch["description"] = (
                        fields["description"].strip() or None
                    )
                if "notes" in fields:
                    patch["notes"] = fields["notes"].strip() or None
                if group_field_present:
                    patch["group_id"] = group_id
                if h is not None:
                    patch["height_u"] = h
                if w is not None:
                    patch["width"] = w
                pwarn = None
                if patch.get("group_id", rack.group_id) is not None:
                    gid = patch.get("group_id", rack.group_id)
                    if group_field_present or "group_position" in fields:
                        pwarn = _position_for(gid, rack, patch)
                elif "group_position" in fields:
                    # leaving/no group — position is meaningless
                    patch["group_position"] = None
                if pwarn:
                    warnings.append(f"{sheet.name} row {num}: {pwarn}")
                # height shrink can't strand occupants — same rule the
                # PATCH route enforces.
                if "height_u" in patch:
                    over = [
                        d.name or f"#{d.id}"
                        for d in await rack_devices(session, rack.id)
                        if d.u_position is not None
                        and d.u_position + (d.u_height or 1) - 1
                        > patch["height_u"]
                    ]
                    if over:
                        plans.append(_RackPlan(
                            num, False, "error",
                            f"height {patch['height_u']}U strands devices: "
                            + ", ".join(over[:5]),
                            sheet.name, None, rack,
                        ))
                        continue
                diff = {
                    k: [getattr(rack, k), v]
                    for k, v in patch.items()
                    if getattr(rack, k) != v
                }
                replace_ids.add(rack.id)
                plans.append(_RackPlan(
                    num, True,
                    "update" if diff else "skip",
                    f"update (matched by {how})" if diff
                    else f"identical (matched by {how})",
                    sheet.name, diff or None, rack, None, patch,
                ))
                continue

            # ---- create ----
            if not name:
                plans.append(_RackPlan(
                    num, False, "error", "name required", sheet.name))
                continue
            create: dict = {
                "name": name,
                "site_id": site_id,
                "room": (fields.get("room") or "").strip() or None,
                "height_u": h if h is not None else 42,
                "width": w if w is not None else 19,
                "description": (fields.get("description") or "").strip() or None,
                "notes": (fields.get("notes") or "").strip() or None,
            }
            gid = group_id if group_field_present else None
            create["group_id"] = gid
            pwarn = _position_for(gid, None, create) if gid else None
            if gid and "group_position" not in create:
                create["group_position"] = None
            if pwarn:
                warnings.append(f"{sheet.name} row {num}: {pwarn}")
            transient = Rack(
                id=-num, name=name, site_id=site_id, group_id=gid,
                height_u=create["height_u"], width=create["width"],
            )
            plans.append(_RackPlan(
                num, True, "create", f"create rack '{name}'", sheet.name,
                None, None, create, None, -num, transient,
            ))
            racks_by_name.setdefault(_fold(name), []).append(transient)
            racks_by_id[-num] = transient
    return plans, skipped_ids, replace_ids, racks_by_name, racks_by_id


async def _replace_targets(
    sheets: list[BundleSheet],
    racks_by_name: dict[str, list[Rack]],
    racks_by_id: dict[int, Rack],
    skipped_ids: set[int],
) -> set[int]:
    """DB racks the devices sheet places into — their occupants unrack
    first under replace_devices (file racks under update/merge are added
    by _plan_racks). Skipped racks are frozen — never in the set."""
    out: set[int] = set()
    for sheet in sheets:
        if sheet.family != "devices":
            continue
        for _, fields in sheet.frows():
            v = (fields.get("rack") or "").strip()
            if not v:
                continue
            if rid := _parse_id(v):
                r = racks_by_id.get(rid)
                if r is not None and r.id not in skipped_ids:
                    out.add(r.id)
                continue
            for r in racks_by_name.get(_fold(v), []):
                if r.id not in skipped_ids and r.id > 0:
                    out.add(r.id)
    return out


async def _load_rack_index(session: AsyncSession) -> tuple[dict, dict]:
    racks = list((await session.execute(select(Rack))).scalars())
    return _name_map(racks), {r.id: r for r in racks}


async def _plan_ifaces(
    session: AsyncSession,
    sheets: list[BundleSheet],
    device_plans: list[Planned],
    skipped_rack_ids: set[int],
    on_existing: str,
) -> list[_IfacePlan]:
    """interfaces sheet -> plans. Devices resolve by name against batch
    plans first, then the DB; interfaces match by device+name."""
    names_needed: set[str] = set()
    id_refs: set[int] = set()
    for sheet in sheets:
        if sheet.family != "interfaces":
            continue
        for _, f in sheet.frows():
            v = (f.get("device") or "").strip()
            if not v:
                continue
            if rid := _parse_id(v):
                id_refs.add(rid)
            else:
                names_needed.add(_fold(v))
    # batch devices (creates + matched) shadow the DB by name
    batch: dict[str, list] = {}
    for p in device_plans:
        if p.ok and p.create_data:
            batch.setdefault(_fold(p.create_data.get("name") or ""), []).append(p)
        if p.device is not None:
            batch.setdefault(_fold(p.device.name or ""), []).append(p.device)
    db: dict[str, list[Device]] = {}
    missing_names = {n for n in names_needed if n not in batch}
    conds = []
    if id_refs:
        conds.append(Device.id.in_(id_refs))
    if missing_names:
        conds.append(
            func.lower(func.translate(Device.name, "םןץףך", "מנצפכ"))
            .in_(missing_names)
        )
    devices: list[Device] = []
    if conds:
        devices = list(
            (await session.execute(select(Device).where(or_(*conds))))
            .scalars()
        )
    db_by_id = {d.id: d for d in devices}
    for d in devices:
        db.setdefault(_fold(d.name or ""), []).append(d)

    # existing interfaces for every DB device we may touch
    real_ids = {
        d.id for d in devices
    } | {
        p.device.id for p in device_plans if p.device is not None
    }
    ifaces = (
        list(
            (
                await session.execute(
                    select(DeviceInterface).where(
                        DeviceInterface.device_id.in_(real_ids)
                    )
                )
            ).scalars()
        )
        if real_ids
        else []
    )
    by_dev_name: dict[tuple[int, str], DeviceInterface] = {}
    next_pos: dict[int, int] = {}
    for i in ifaces:
        by_dev_name[(i.device_id, _fold(i.name or ""))] = i
        next_pos[i.device_id] = max(
            next_pos.get(i.device_id, 0), (i.position or 0) + 1
        )

    ip_tokens = {
        f["connected_ip"].strip()
        for sheet in sheets
        if sheet.family == "interfaces"
        for _, f in sheet.frows()
        if (f.get("connected_ip") or "").strip()
    }
    ip_by_addr = {
        ip_display(r.address): r
        for r in (
            (
                await session.execute(
                    select(IPAddress).where(
                        func.host(IPAddress.address).in_(ip_tokens)
                    )
                )
            ).scalars()
        )
    } if ip_tokens else {}

    plans: list[_IfacePlan] = []
    batch_names: dict[tuple[Any, str], _IfacePlan] = {}
    for sheet in sheets:
        if sheet.family != "interfaces":
            continue
        for num, fields in sheet.frows():
            ref_v = (fields.get("device") or "").strip()
            name = (fields.get("name") or "").strip()
            # --- resolve device ---
            dev: Device | Planned | None = None
            if not ref_v:
                plans.append(_IfacePlan(
                    num, False, "error", "device required", sheet.name))
                continue
            if rid := _parse_id(ref_v):
                dev = db_by_id.get(rid)
                if dev is None:
                    dev = next(
                        (p.device for p in device_plans
                         if p.device is not None and p.device.id == rid),
                        None,
                    )
                if dev is None:
                    plans.append(_IfacePlan(
                        num, False, "error", f"device '{ref_v}' not found",
                        sheet.name))
                    continue
            else:
                cands = batch.get(_fold(ref_v)) or db.get(_fold(ref_v)) or []
                if len(cands) > 1:
                    plans.append(_IfacePlan(
                        num, False, "error",
                        f"device '{ref_v}' is ambiguous "
                        f"({len(cands)} matches)", sheet.name))
                    continue
                if not cands:
                    plans.append(_IfacePlan(
                        num, False, "error",
                        f"device '{ref_v}' not found", sheet.name))
                    continue
                dev = cands[0]
            dev_rack = (
                dev.rack_id if isinstance(dev, Device)
                else (dev.device.rack_id if dev.device is not None
                      else (dev.create_data or {}).get("rack_id"))
            )
            if dev_rack in skipped_rack_ids:
                plans.append(_IfacePlan(
                    num, True, "skip",
                    "device's rack untouched (on_existing=skip)",
                    sheet.name, None, None, dev,
                ))
                continue
            if isinstance(dev, Planned) and not dev.ok:
                plans.append(_IfacePlan(
                    num, False, "error",
                    f"device '{ref_v}' is an error row", sheet.name))
                continue
            if not name:
                plans.append(_IfacePlan(
                    num, False, "error", "name required", sheet.name))
                continue

            # --- field validation ---
            kind = None
            if "kind" in fields and fields["kind"].strip():
                try:
                    kind = InterfaceKind(fields["kind"].strip().lower())
                except ValueError:
                    plans.append(_IfacePlan(
                        num, False, "error",
                        f"bad kind {fields['kind']!r} (expected "
                        + "/".join(k.value for k in InterfaceKind) + ")",
                        sheet.name))
                    continue
            speed, serr = _int_field(fields.get("speed_mbps"), "speed_mbps")
            if serr:
                plans.append(_IfacePlan(num, False, "error", serr, sheet.name))
                continue
            if speed is not None and not 1 <= speed <= 3_200_000:
                plans.append(_IfacePlan(
                    num, False, "error", "speed_mbps out of range",
                    sheet.name))
                continue
            mac = None
            if "mac_address" in fields and fields["mac_address"].strip():
                mac = norm_mac(fields["mac_address"])
                if mac is None:
                    plans.append(_IfacePlan(
                        num, False, "error",
                        f"bad mac_address {fields['mac_address']!r}",
                        sheet.name))
                    continue
            warn = ""
            ip_id: int | None = None
            if "connected_ip" in fields:
                tok = fields["connected_ip"].strip()
                if tok:
                    ip = ip_by_addr.get(tok)
                    if ip is None:
                        warn = f"unknown ip '{tok}' — linked ip skipped"
                    else:
                        dev_id = (
                            dev.id if isinstance(dev, Device)
                            else (dev.device.id if dev.device else None)
                        )
                        if ip.device_id is not None and (
                            dev_id is None or ip.device_id != dev_id
                        ):
                            warn = (
                                f"ip {tok} belongs to another device — "
                                "linked ip skipped"
                            )
                        else:
                            ip_id = ip.id

            dev_key = dev.id if isinstance(dev, Device) else ("row", dev.row)
            key = (dev_key, _fold(name))
            if key in batch_names:
                plans.append(_IfacePlan(
                    num, False, "error",
                    f"duplicate interface '{name}' for device '{ref_v}' "
                    "in file", sheet.name))
                continue
            existing = None
            if isinstance(dev, Device):
                existing = by_dev_name.get((dev.id, _fold(name)))
            if existing is not None:
                if on_existing != "update":
                    plans.append(_IfacePlan(
                        num, True, "skip",
                        f"exists ({existing.name} on {dev.name})",
                        sheet.name, None, existing, dev,
                    ))
                    batch_names[key] = plans[-1]
                    continue
                patch: dict = {}
                if kind is not None:
                    patch["kind"] = kind
                if "speed_mbps" in fields:
                    patch["speed_mbps"] = speed
                if "mac_address" in fields:
                    patch["mac_address"] = (
                        mac if fields["mac_address"].strip() else None
                    )
                if "connected_ip" in fields:
                    patch["connected_ip_id"] = ip_id
                diff = {
                    k: [
                        (getattr(existing, k).value
                         if isinstance(getattr(existing, k), InterfaceKind)
                         else getattr(existing, k)),
                        (v.value if isinstance(v, InterfaceKind) else v),
                    ]
                    for k, v in patch.items()
                    if getattr(existing, k) != v
                }
                plans.append(_IfacePlan(
                    num, True,
                    "update" if diff else "skip",
                    f"update ({dev.name}/{existing.name})" if diff
                    else f"identical ({dev.name}/{existing.name})",
                    sheet.name, diff or None, existing, dev, None, patch,
                ))
                batch_names[key] = plans[-1]
                continue
            create = {
                "name": name,
                "kind": kind or InterfaceKind.RJ45,
                "speed_mbps": speed,
                "mac_address": mac,
                "connected_ip_id": ip_id,
                "position": next_pos.get(
                    dev.id if isinstance(dev, Device) else -1, 0
                ),
            }
            if isinstance(dev, Device):
                next_pos[dev.id] = create["position"] + 1
            plans.append(_IfacePlan(
                num, True, "create",
                f"create {dev.name if isinstance(dev, Device) else dev.create_data['name']}"
                f"/{name}" + (f" — {warn}" if warn else ""),
                sheet.name, None, None, dev, create,
            ))
            batch_names[key] = plans[-1]
    return plans


async def _plan_cables(
    session: AsyncSession,
    sheets: list[BundleSheet],
    device_plans: list[Planned],
    iface_plans: list[_IfacePlan],
    skipped_rack_ids: set[int],
    on_existing: str,
) -> list[_CablePlan]:
    """cables sheet -> plans. Endpoints resolve by device name + interface
    name across the batch and the DB; a claimed interface errors instead
    of silently re-cabling."""
    names_needed: set[str] = set()
    for sheet in sheets:
        if sheet.family != "cables":
            continue
        for _, f in sheet.frows():
            for k in ("a_device", "b_device"):
                v = (f.get(k) or "").strip()
                if v and _parse_id(v) is None:
                    names_needed.add(_fold(v))
    batch: dict[str, list] = {}
    for p in device_plans:
        if p.ok and p.create_data:
            batch.setdefault(_fold(p.create_data.get("name") or ""), []).append(p)
        if p.device is not None:
            batch.setdefault(_fold(p.device.name or ""), []).append(p.device)
    db: dict[str, list[Device]] = {}
    missing = names_needed - set(batch)
    if missing:
        for d in (
            await session.execute(
                select(Device).where(
                    func.lower(
                        func.translate(Device.name, "םןץףך", "מנצפכ")
                    ).in_(missing)
                )
            )
        ).scalars():
            db.setdefault(_fold(d.name or ""), []).append(d)

    # resolved device -> its interfaces (DB + batch plans)
    real_ids = {d.id for ds in db.values() for d in ds} | {
        p.device.id for p in device_plans if p.device is not None
    }
    ifaces = (
        list(
            (
                await session.execute(
                    select(DeviceInterface).where(
                        DeviceInterface.device_id.in_(real_ids)
                    )
                )
            ).scalars()
        )
        if real_ids
        else []
    )
    by_dev_name: dict[tuple[int, str], DeviceInterface] = {}
    for i in ifaces:
        by_dev_name[(i.device_id, _fold(i.name or ""))] = i
    batch_iface: dict[tuple[Any, str], _IfacePlan] = {}
    for ip_ in iface_plans:
        if not ip_.ok or ip_.create is None:
            continue
        dev = ip_.device_ref
        dev_key = dev.id if isinstance(dev, Device) else ("row", dev.row)
        batch_iface[(dev_key, _fold(ip_.create["name"]))] = ip_
    cable_by_iface: dict[int, Cable] = {}
    iface_ids = [i.id for i in ifaces]
    if iface_ids:
        for c in (
            (
                await session.execute(
                    select(Cable).where(
                        or_(
                            Cable.a_interface_id.in_(iface_ids),
                            Cable.b_interface_id.in_(iface_ids),
                        )
                    )
                )
            ).scalars()
        ):
            cable_by_iface[c.a_interface_id] = c
            cable_by_iface[c.b_interface_id] = c

    def _dev(v: str) -> tuple[Device | Planned | None, str | None]:
        if not v:
            return None, "device required"
        cands = batch.get(_fold(v)) or db.get(_fold(v)) or []
        if len(cands) > 1:
            return None, f"device '{v}' is ambiguous ({len(cands)} matches)"
        if not cands:
            return None, f"device '{v}' not found"
        return cands[0], None

    def _iface(dev, name: str) -> tuple[Any, str | None]:
        dev_key = dev.id if isinstance(dev, Device) else ("row", dev.row)
        p = batch_iface.get((dev_key, _fold(name)))
        if p is not None:
            return p, None
        if isinstance(dev, Device):
            i = by_dev_name.get((dev.id, _fold(name)))
            if i is not None:
                return i, None
        return None, None

    plans: list[_CablePlan] = []
    claimed: dict[Any, int] = {}  # endpoint key -> row that took it
    for sheet in sheets:
        if sheet.family != "cables":
            continue
        for num, fields in sheet.frows():
            refs: list[Any] = []
            bad = None
            for side in ("a", "b"):
                dev, derr = _dev((fields.get(f"{side}_device") or "").strip())
                if derr:
                    bad = f"{side}-side: {derr}"
                    break
                iname = (fields.get(f"{side}_interface") or "").strip()
                if not iname:
                    bad = f"{side}-side: interface required"
                    break
                ref, _ = _iface(dev, iname)
                if ref is None:
                    bad = (
                        f"{side}-side: interface '{iname}' not found on "
                        f"device '{fields[f'{side}_device'].strip()}'"
                    )
                    break
                refs.append((dev, ref))
            if bad:
                plans.append(_CablePlan(num, False, "error", bad, sheet.name))
                continue
            (adev, aref), (bdev, bref) = refs
            if aref is bref or (
                isinstance(aref, DeviceInterface)
                and isinstance(bref, DeviceInterface)
                and aref.id == bref.id
            ):
                plans.append(_CablePlan(
                    num, False, "error",
                    "cable ends must be two distinct interfaces",
                    sheet.name))
                continue
            # skipped rack check on either device
            for d in (adev, bdev):
                rid = (
                    d.rack_id if isinstance(d, Device)
                    else (d.device.rack_id if d.device is not None
                          else (d.create_data or {}).get("rack_id"))
                )
                if rid in skipped_rack_ids:
                    plans.append(_CablePlan(
                        num, True, "skip",
                        "device's rack untouched (on_existing=skip)",
                        sheet.name, None, None, aref, bref,
                    ))
                    break
            else:
                # claim check — one cable per interface, DB or batch
                seen = False
                for dev, ref in ((adev, aref), (bdev, bref)):
                    key = ref.id if isinstance(ref, DeviceInterface) else ("plan", ref.row)
                    if key in claimed:
                        plans.append(_CablePlan(
                            num, False, "error",
                            f"interface already claimed by cable row "
                            f"{claimed[key]}", sheet.name))
                        seen = True
                        break
                    if isinstance(ref, DeviceInterface):
                        existing = cable_by_iface.get(ref.id)
                        if existing is not None:
                            other_end = (
                                existing.b_interface_id
                                if existing.a_interface_id == ref.id
                                else existing.a_interface_id
                            )
                            mate = bref if ref is aref else aref
                            mate_id = (
                                mate.id
                                if isinstance(mate, DeviceInterface)
                                else None
                            )
                            if mate_id == other_end:
                                # the file re-declares this exact link
                                plans.append(_cable_match(
                                    num, existing, aref, bref, fields,
                                    on_existing, sheet.name))
                                seen = True
                                break
                            plans.append(_CablePlan(
                                num, False, "error",
                                "interface already terminated by "
                                f"cable#{existing.id}", sheet.name))
                            seen = True
                            break
                if seen:
                    continue
                for dev, ref in ((adev, aref), (bdev, bref)):
                    claimed[
                        ref.id if isinstance(ref, DeviceInterface)
                        else ("plan", ref.row)
                    ] = num
                kind = CableKind.OTHER
                if "kind" in fields and fields["kind"].strip():
                    try:
                        kind = CableKind(fields["kind"].strip().lower())
                    except ValueError:
                        plans.append(_CablePlan(
                            num, False, "error",
                            f"bad kind {fields['kind']!r} (expected "
                            + "/".join(k.value for k in CableKind) + ")",
                            sheet.name))
                        continue
                length, lerr = _float_field(
                    fields.get("length_m"), "length_m")
                if lerr:
                    plans.append(_CablePlan(num, False, "error", lerr, sheet.name))
                    continue
                if length is not None and not 0 <= length <= 9999.9:
                    plans.append(_CablePlan(
                        num, False, "error", "length_m out of range",
                        sheet.name))
                    continue
                plans.append(_CablePlan(
                    num, True, "create",
                    "link "
                    f"{fields['a_device'].strip()}/"
                    f"{fields['a_interface'].strip()} — "
                    f"{fields['b_device'].strip()}/"
                    f"{fields['b_interface'].strip()}",
                    sheet.name, None, None, aref, bref,
                    {
                        "kind": kind,
                        "color": (fields.get("color") or "").strip() or None,
                        "label": (fields.get("label") or "").strip() or None,
                        "length_m": length,
                    },
                ))
    return plans


def _cable_match(
    num: int,
    cable: Cable,
    aref,
    bref,
    fields: dict[str, str],
    on_existing: str,
    sheet: str,
) -> _CablePlan:
    """The cable exists with this exact endpoint pair — skip or patch its
    attributes under on_existing=update."""
    if on_existing != "update":
        return _CablePlan(
            num, True, "skip", f"exists (cable#{cable.id})", sheet,
            None, cable, aref, bref,
        )
    patch: dict = {}
    if "kind" in fields and fields["kind"].strip():
        try:
            patch["kind"] = CableKind(fields["kind"].strip().lower())
        except ValueError:
            return _CablePlan(num, False, "error",
                              f"bad kind {fields['kind']!r}", sheet)
    if "color" in fields:
        patch["color"] = fields["color"].strip() or None
    if "label" in fields:
        patch["label"] = fields["label"].strip() or None
    if "length_m" in fields:
        length, lerr = _float_field(fields["length_m"], "length_m")
        if lerr:
            return _CablePlan(num, False, "error", lerr, sheet)
        patch["length_m"] = length
    diff = {}
    for k, v in patch.items():
        old = getattr(cable, k)
        if isinstance(old, CableKind):
            old = old.value
        nv = v.value if isinstance(v, CableKind) else v
        if k == "length_m" and old is not None:
            old = float(old)
        if old != nv:
            diff[k] = [old, nv]
    return _CablePlan(
        num, True,
        "update" if diff else "skip",
        f"update (cable#{cable.id})" if diff else f"identical (cable#{cable.id})",
        sheet, diff or None, cable, aref, bref, patch,
    )


async def plan_bundle(
    session: AsyncSession,
    sheets: list[BundleSheet],
    *,
    on_existing: str,
    replace_devices: bool,
    group_override: RackGroup | None,
) -> BundlePlan:
    """Every sheet -> verdict rows; pure — nothing is written. Stages run
    in tree order so later stages resolve what earlier ones staged."""
    plan = BundlePlan()
    warnings: list[str] = []

    site_plans, site_res = await _plan_sites(session, sheets)
    plan.sites = site_plans

    db_groups = list((await session.execute(select(RackGroup))).scalars())
    group_plans, groups_by_name, groups_by_id = await _plan_groups(
        sheets, site_res, db_groups, on_existing
    )
    plan.groups = group_plans

    rack_plans, skipped_ids, replace_ids, racks_by_name, racks_by_id = (
        await _plan_racks(
            session, sheets, site_res, groups_by_name, groups_by_id,
            group_override, on_existing, warnings,
        )
    )
    plan.racks = rack_plans

    # devices sheet — racks the file touches get their occupants unracked
    # first under replace_devices (skipped racks never do).
    if replace_devices:
        plan.replace_rack_ids = replace_ids | await _replace_targets(
            sheets, racks_by_name, racks_by_id, skipped_ids
        )
    device_sheets = [s for s in sheets if s.family == "devices"]
    for sheet in device_sheets:
        devs = await plan_device_import(
            session, sheet.rows, sheet.col_map,
            on_match="update" if on_existing == "update" else "skip",
            unracked_on_missing=False,
            extra_sites=[p.site for p in site_plans],
            extra_groups=[
                g
                for p in group_plans
                if p.ok and p.create is not None
                for g in [RackGroup(
                    id=p.temp_id, name=p.create["name"],
                    site_id=p.create["site_id"],
                    description=p.create["description"],
                )]
            ],
            extra_racks=[p.transient for p in rack_plans
                         if p.transient is not None],
            skipped_rack_ids=frozenset(skipped_ids),
            replace_rack_ids=frozenset(plan.replace_rack_ids),
            scope_names_to_rack=True,
        )
        plan.devices += devs
        plan.device_rows += [(sheet.name, p) for p in devs]
    plan.ifaces = await _plan_ifaces(
        session, sheets, plan.devices, skipped_ids, on_existing
    )
    plan.cables = await _plan_cables(
        session, sheets, plan.devices, plan.ifaces, skipped_ids, on_existing
    )

    # ---- response rows: canonical tree order, sheet field per row ----
    site_first: dict[int, int] = {}
    for s in sheets:
        if s.family not in ("groups", "racks", "devices"):
            continue
        for num, f in s.frows():
            if "site" in f and f["site"].strip():
                site = site_res.get(f["site"].strip())
                if isinstance(site, Site) and site.id is not None and (
                    site.id < 0
                ):
                    site_first.setdefault(site.id, num)
    for p in site_plans:
        plan.rows.append(_out(
            site_first.get(p.temp_id, 0), "sites", True, "create",
            f"create site '{p.name}' (referenced by the bundle)",
        ))
    for p in group_plans:
        plan.rows.append(
            _out(p.row, p.sheet, p.ok, p.action, p.detail, p.diff)
        )
    for p in rack_plans:
        plan.rows.append(
            _out(p.row, p.sheet, p.ok, p.action, p.detail, p.diff)
        )
    for sheet_name, p in plan.device_rows:
        d = p.out()
        d["sheet"] = sheet_name
        plan.rows.append(d)
    for p in plan.ifaces:
        plan.rows.append(
            _out(p.row, p.sheet, p.ok, p.action, p.detail, p.diff)
        )
    for p in plan.cables:
        plan.rows.append(
            _out(p.row, p.sheet, p.ok, p.action, p.detail, p.diff)
        )

    seen_cols: set[str] = set()
    for s in sheets:
        for h in s.headers:
            if h not in seen_cols:
                seen_cols.add(h)
                plan.columns.append({"header": h, "field": s.col_map.get(h)})
        plan.unmapped += [u for u in s.unmapped if u not in plan.unmapped]
        plan.sheets_meta.append({
            "name": s.name,
            "family": s.family,
            "row_count": len(s.rows),
            "columns": [
                {"header": h, "field": s.col_map.get(h)} for h in s.headers
            ],
            "unmapped": s.unmapped,
            **({"warning": s.warning} if s.warning else {}),
        })
        if s.warning:
            warnings.append(s.warning)
    plan.warnings = warnings
    return plan


async def apply_bundle(session: AsyncSession, plan: BundlePlan) -> None:
    """Commit a clean (or forced) plan in one transaction — same apply
    order as the plan: sites, groups, racks, replace-unrack, devices,
    interfaces, cables."""
    site_ids: dict[int, int] = {}
    group_ids: dict[int, int] = {}
    rack_ids: dict[int, int] = {}
    for sp in plan.sites:
        s = Site(name=sp.name, slug=sp.site.slug if sp.site else slugify(sp.name))
        session.add(s)
        await session.flush()
        site_ids[sp.temp_id] = s.id
        sp.site = s

    def _t(d: dict) -> dict:
        out = dict(d)
        for k, m in (
            ("site_id", site_ids), ("group_id", group_ids),
            ("rack_id", rack_ids),
        ):
            if out.get(k) in m:
                out[k] = m[out[k]]
        return out

    for gp in plan.groups:
        if not gp.ok:
            continue
        if gp.create is not None:
            g = RackGroup(**_t(gp.create))
            session.add(g)
            await session.flush()
            group_ids[gp.temp_id] = g.id
        elif gp.patch and gp.group is not None:
            for k, v in _t(gp.patch).items():
                setattr(gp.group, k, v)
            await session.flush()
    for rp in plan.racks:
        if not rp.ok:
            continue
        if rp.create is not None:
            r = Rack(**_t(rp.create))
            session.add(r)
            await session.flush()
            rack_ids[rp.temp_id] = r.id
            rp.rack = r
        elif rp.patch and rp.rack is not None:
            for k, v in _t(rp.patch).items():
                setattr(rp.rack, k, v)
            await session.flush()
    # replace_devices: rack-level occupants leave the rack (carrier
    # children ride along mounted — unrack never unmounts a tray).
    if plan.replace_rack_ids:
        occupants = list(
            (
                await session.execute(
                    select(Device).where(
                        Device.rack_id.in_(plan.replace_rack_ids),
                        Device.carrier_id.is_(None),
                    )
                )
            ).scalars()
        )
        for d in occupants:
            await apply_device_patch(session, d, {"rack_id": None})
        await session.flush()
    await apply_device_import(
        session, plan.devices, rack_ids=rack_ids, site_ids=site_ids
    )

    def _dev_id(ref) -> int | None:
        if isinstance(ref, Device):
            return ref.id
        if isinstance(ref, Planned):
            return ref.device.id if ref.device is not None else None
        return None

    iface_ids: dict[int, int] = {}  # plan row -> flushed interface
    for ip_ in plan.ifaces:
        if not ip_.ok:
            continue
        if ip_.create is not None:
            did = _dev_id(ip_.device_ref)
            if did is None:
                continue
            i = DeviceInterface(device_id=did, **ip_.create)
            session.add(i)
            await session.flush()
            ip_.iface = i
        elif ip_.patch and ip_.iface is not None:
            for k, v in ip_.patch.items():
                setattr(ip_.iface, k, v)
            await session.flush()

    def _iface_id(ref) -> int | None:
        if isinstance(ref, DeviceInterface):
            return ref.id
        if isinstance(ref, _IfacePlan):
            return ref.iface.id if ref.iface is not None else None
        return None

    for cp in plan.cables:
        if not cp.ok:
            continue
        if cp.create is not None:
            a = _iface_id(cp.a_ref)
            b = _iface_id(cp.b_ref)
            if a is None or b is None:
                continue
            session.add(Cable(a_interface_id=a, b_interface_id=b, **cp.create))
        elif cp.patch and cp.cable is not None:
            for k, v in cp.patch.items():
                setattr(cp.cable, k, v)
        await session.flush()
