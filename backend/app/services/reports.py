"""Reports workspace (V11) — the whole estate assembled into one payload.

Every number reuses the aggregates the pages themselves show: the
dashboard's usable-IP expression for fill math, ``stamp_rack_stats`` for
rack capacity, ``device_health``/``ips_by_device`` for the device
section, the review queue's flag predicates, ``due_where`` for monitor
debt, and ``runtime_settings.get_effective`` for the cert window. A
report that disagrees with the page it summarizes is a bug, not a
viewpoint.

Sections share one shape — ``{key, title, href, metrics, columns, rows,
total_rows, truncated, note}`` — so a single payload drives the /reports
cards, the per-section CSVs and the XLSX workbook (one sheet per
section). Rows are bounded at ``SECTION_ROWS`` with an honest
``truncated`` marker; nothing is persisted.
"""
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import func, or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.cabling import DeviceInterface
from app.models.certificate import Certificate
from app.models.device import Device
from app.models.ip_address import IPAddress, IPStatus
from app.models.monitoring import MonitorState, MonitorTarget
from app.models.prefix import Prefix, PrefixStatus
from app.models.rack import Rack, RackGroup
from app.models.scan_job import ScanJob, ScanStatus
from app.models.site import Site
from app.models.vrf import VRF
from app.services import notify, runtime_settings
from app.services.device_io import HEALTH_CLASSES
from app.services.devices import device_health, ips_by_device
from app.services.ipam import v4_usable_expr
from app.services.monitors import due_where
from app.services.racks import stamp_rack_stats

# Big sections cap at ~500 rows — honesty over completeness.
SECTION_ROWS = 500
# "last-N" tails (scans) keep the report page scannable.
RECENT_SCANS = 20
FULLEST_N = 10
EMPTIEST_N = 5


def _section(
    key: str,
    title: str,
    href: str | None,
    columns: list[str],
    rows: list[list],
    *,
    metrics: list[tuple[str, object]] = (),
    note: str | None = None,
) -> dict:
    return {
        "key": key,
        "title": title,
        "href": href,
        "note": note,
        "metrics": [{"label": label, "value": value} for label, value in metrics],
        "columns": columns,
        "rows": [list(r) for r in rows[:SECTION_ROWS]],
        "total_rows": len(rows),
        "truncated": len(rows) > SECTION_ROWS,
    }


async def _has_table(session: AsyncSession, name: str) -> bool:
    return bool(await session.scalar(select(func.to_regclass(name))))


# ------------------------------------------------------------------ helpers


async def _ipam_totals(session: AsyncSession, site: Site | None) -> dict:
    """The dashboard's used/usable accounting, optionally narrowed by site.

    Usable = SUM over IPv4 non-container prefixes (masklen>=31 counts every
    slot); used = addresses under IPv4 prefixes. Same rules as
    ``ipam.dashboard_stats`` so the headline strip matches the dashboard.
    """
    p_stmt = select(func.coalesce(func.sum(v4_usable_expr()), 0)).where(
        func.family(Prefix.prefix) == 4, Prefix.status != PrefixStatus.CONTAINER
    )
    u_stmt = (
        select(func.count(IPAddress.id))
        .join(Prefix, IPAddress.prefix_id == Prefix.id)
        .where(func.family(Prefix.prefix) == 4)
    )
    if site is not None:
        p_stmt = p_stmt.where(Prefix.site_id == site.id)
        u_stmt = u_stmt.where(Prefix.site_id == site.id)
    usable = int(await session.scalar(p_stmt) or 0)
    used = int(await session.scalar(u_stmt) or 0)
    return {
        "ips_total": usable,
        "ips_used": used,
        "utilization_pct": round(used / usable * 100, 1) if usable else 0.0,
    }


# ------------------------------------------------------------------ sections


async def _sites(session: AsyncSession, site: Site | None) -> dict:
    v4 = v4_usable_expr()
    p_counts = {
        k: int(c)
        for k, c in (
            await session.execute(
                select(Prefix.site_id, func.count(Prefix.id)).group_by(
                    Prefix.site_id
                )
            )
        ).all()
    }
    usable = {
        k: int(c)
        for k, c in (
            await session.execute(
                select(
                    Prefix.site_id,
                    func.coalesce(func.sum(v4), 0),
                )
                .where(
                    func.family(Prefix.prefix) == 4,
                    Prefix.status != PrefixStatus.CONTAINER,
                )
                .group_by(Prefix.site_id)
            )
        ).all()
    }
    # used follows the dashboard rule: addresses under IPv4 prefixes,
    # containers included (only capacity excludes containers).
    used = {
        k: int(c)
        for k, c in (
            await session.execute(
                select(Prefix.site_id, func.count(IPAddress.id))
                .join(Prefix, IPAddress.prefix_id == Prefix.id)
                .where(func.family(Prefix.prefix) == 4)
                .group_by(Prefix.site_id)
            )
        ).all()
    }
    devs = {
        k: int(c)
        for k, c in (
            await session.execute(
                select(Device.site_id, func.count(Device.id)).group_by(
                    Device.site_id
                )
            )
        ).all()
    }

    rows: list[list] = []
    if site is not None:
        sites = [site]
    else:
        sites = (
            (await session.execute(select(Site).order_by(Site.name, Site.id)))
            .scalars()
            .all()
        )
    for s in sites:
        u = usable.get(s.id, 0)
        d = used.get(s.id, 0)
        rows.append(
            [
                s.name,
                p_counts.get(s.id, 0),
                d,
                u if u else None,
                round(d / u * 100, 1) if u else None,
                devs.get(s.id, 0),
            ]
        )
    # addresses/prefixes/devices with no site land in one unassigned row
    if site is None and any(
        None in m for m in (p_counts, usable, used, devs)
    ):
        u = usable.get(None, 0)
        d = used.get(None, 0)
        rows.append(
            [
                "(unassigned)",
                p_counts.get(None, 0),
                d,
                u if u else None,
                round(d / u * 100, 1) if u else None,
                devs.get(None, 0),
            ]
        )

    return _section(
        "sites",
        "Sites",
        "/sites",
        ["site", "prefixes", "addresses_used", "addresses_usable", "fill_pct", "devices"],
        rows,
        metrics=[
            ("Sites", len(sites)),
            ("Prefixes", sum(r[1] for r in rows)),
            ("Devices", sum(r[5] for r in rows)),
        ],
    )


async def _status(session: AsyncSession, site: Site | None) -> dict:
    stmt = select(IPAddress.status, func.count()).group_by(IPAddress.status)
    if site is not None:
        stmt = stmt.join(Prefix, IPAddress.prefix_id == Prefix.id).where(
            Prefix.site_id == site.id
        )
    by_status = {
        (k.value if hasattr(k, "value") else str(k)): int(c)
        for k, c in (await session.execute(stmt)).all()
    }
    total = sum(by_status.values())
    rows = [
        [st.value, by_status.get(st.value, 0),
         round(by_status.get(st.value, 0) / total * 100, 1) if total else 0.0]
        for st in IPStatus
    ]
    totals = await _ipam_totals(session, site)
    return _section(
        "status",
        "Address status",
        "/addresses",
        ["status", "addresses", "share_pct"],
        rows,
        metrics=[
            ("Addresses", total),
            ("IPs used", totals["ips_used"]),
            ("Usable", totals["ips_total"]),
            ("Utilization", f"{totals['utilization_pct']}%"),
        ],
    )


async def _utilization(session: AsyncSession, site: Site | None) -> dict:
    from app.services.ipam import prefix_stats_dict

    stmt = (
        select(Prefix)
        .options(selectinload(Prefix.vrf), selectinload(Prefix.site))
        .order_by(Prefix.id)
    )
    if site is not None:
        stmt = stmt.where(Prefix.site_id == site.id)
    prefixes = (await session.execute(stmt)).scalars().all()

    counts = dict(
        (await session.execute(
            select(IPAddress.prefix_id, func.count()).group_by(
                IPAddress.prefix_id
            )
        )).all()
    )
    scored = []
    for p in prefixes:
        if p.status == PrefixStatus.CONTAINER:
            continue
        st = prefix_stats_dict(p, int(counts.get(p.id, 0)))
        if st["utilization_pct"] is None:
            continue
        scored.append((p, st))
    scored.sort(key=lambda t: (-t[1]["utilization_pct"], str(t[0].prefix)))

    def row(bucket: str, p: Prefix, st: dict) -> list:
        return [
            bucket,
            str(p.prefix),
            p.vrf.name if p.vrf else "",
            p.site.name if p.site else "",
            p.status.value,
            st["used_ips"],
            st["usable_ips"],
            st["utilization_pct"],
        ]

    rows = [row("fullest", p, st) for p, st in scored[:FULLEST_N]]
    rows += [row("emptiest", p, st) for p, st in scored[::-1][:EMPTIEST_N]]
    metrics: list[tuple[str, object]] = [("Prefixes scored", len(scored))]
    if scored:
        metrics += [
            ("Fullest", f"{scored[0][0].prefix} {scored[0][1]['utilization_pct']}%"),
            ("Emptiest", f"{scored[-1][0].prefix} {scored[-1][1]['utilization_pct']}%"),
        ]
    return _section(
        "utilization",
        "Utilization",
        "/prefixes",
        ["bucket", "prefix", "vrf", "site", "status", "used_ips", "usable_ips", "utilization_pct"],
        rows,
        metrics=metrics,
        note=f"fullest {FULLEST_N} and emptiest {EMPTIEST_N} IPv4 prefixes "
        "(containers excluded — same accounting as the dashboard chart).",
    )


async def _capacity(session: AsyncSession, site: Site | None) -> dict:
    stmt = select(Rack).order_by(Rack.name, Rack.id)
    if site is not None:
        stmt = stmt.where(Rack.site_id == site.id)
    racks = (await session.execute(stmt)).scalars().all()
    await stamp_rack_stats(session, racks)

    group_ids = {r.group_id for r in racks if r.group_id}
    groups = {
        g.id: g
        for g in (
            await session.execute(
                select(RackGroup)
                .options(selectinload(RackGroup.site))
                .where(RackGroup.id.in_(group_ids or {0}))
            )
        ).scalars()
    }

    by_group: dict[int | None, list] = {}
    for r in racks:
        by_group.setdefault(r.group_id, []).append(r)

    def group_key(item):
        gid, _ = item
        g = groups.get(gid) if gid else None
        return (gid is None, (g.name if g else "").lower())

    rows = []
    tot_racks = tot_cap = tot_used = 0
    for gid, rs in sorted(by_group.items(), key=group_key):
        g = groups.get(gid) if gid else None
        cap = sum(int(r.height_u) for r in rs)
        used_u = sum(int(r.used_u) for r in rs)
        watts = sum(int(r.power_w) for r in rs if r.power_w is not None)
        kg = sum(float(r.weight_kg) for r in rs if r.weight_kg is not None)
        watts = watts if any(r.power_w is not None for r in rs) else None
        kg = round(kg, 1) if any(r.weight_kg is not None for r in rs) else None
        rows.append(
            [
                g.name if g else "(ungrouped)",
                g.site.name if g and g.site else "",
                len(rs),
                used_u,
                cap - used_u,
                cap,
                round(used_u / cap * 100, 1) if cap else None,
                watts,
                kg,
            ]
        )
        tot_racks += len(rs)
        tot_cap += cap
        tot_used += used_u

    return _section(
        "capacity",
        "Rack capacity",
        "/racks",
        ["rack_group", "site", "racks", "used_u", "free_u", "capacity_u", "fill_pct", "power_w", "weight_kg"],
        rows,
        metrics=[
            ("Racks", tot_racks),
            ("Used U", tot_used),
            ("Capacity U", tot_cap),
            ("Fill", f"{round(tot_used / tot_cap * 100, 1)}%" if tot_cap else "0%"),
        ],
    )


async def _certs(session: AsyncSession, site: Site | None) -> dict:
    eff = await runtime_settings.get_effective(session)
    warn = int(eff.values.get("cert_warn_days") or 30)
    total = int(await session.scalar(select(func.count(Certificate.id))) or 0)
    today = date.today()
    certs = (
        (
            await session.execute(
                select(Certificate)
                .where(
                    Certificate.expires_on.is_not(None),
                    Certificate.expires_on <= today + timedelta(days=warn),
                )
                .order_by(Certificate.expires_on.asc(), Certificate.id)
            )
        )
        .scalars()
        .all()
    )
    rows = []
    expired = 0
    for c in certs:
        days = (c.expires_on - today).days
        if days < 0:
            expired += 1
        rows.append(
            [
                c.cert_name or c.server_name or f"cert #{c.id}",
                c.server_name,
                c.platform,
                c.target,
                c.expires_on.isoformat(),
                days,
                "expired" if days < 0 else "expiring",
            ]
        )
    return _section(
        "certs",
        "Certificates",
        "/certificates",
        ["certificate", "server_name", "platform", "target", "expires_on", "days_left", "state"],
        rows,
        metrics=[
            ("Certificates", total),
            ("Expiring", len(rows)),
            ("Expired", expired),
        ],
        note=f"within the effective cert_warn_days window ({warn}d) — "
        "the same predicate the certificates page and review queue use.",
    )


async def _scans(session: AsyncSession, site: Site | None) -> dict:
    # Site scope rides the job's resolved prefix; prefix-less scans stay
    # unattributed rather than guessed.
    def scoped(stmt):
        if site is None:
            return stmt
        return stmt.join(Prefix, ScanJob.prefix_id == Prefix.id).where(
            Prefix.site_id == site.id
        )

    by_status = {
        (k.value if hasattr(k, "value") else str(k)): int(c)
        for k, c in (
            await session.execute(
                scoped(select(ScanJob.status, func.count())).group_by(
                    ScanJob.status
                )
            )
        ).all()
    }
    hosts_seen = int(
        await session.scalar(
            scoped(select(func.coalesce(func.sum(ScanJob.hosts_discovered), 0)))
        )
        or 0
    )
    recent = (
        (
            await session.execute(
                scoped(select(ScanJob)).order_by(ScanJob.id.desc()).limit(
                    RECENT_SCANS
                )
            )
        )
        .scalars()
        .all()
    )
    rows = [
        [
            j.id,
            j.cidr,
            j.status.value if hasattr(j.status, "value") else str(j.status),
            j.hosts_discovered,
            j.hosts_new,
            j.duration_seconds,
            j.started_at.isoformat() if j.started_at else None,
            j.finished_at.isoformat() if j.finished_at else None,
        ]
        for j in recent
    ]
    return _section(
        "scans",
        "Scans",
        "/scans",
        ["id", "cidr", "status", "hosts_discovered", "hosts_new", "duration_s", "started_at", "finished_at"],
        rows,
        metrics=[
            ("Jobs", sum(by_status.values())),
            ("Completed", by_status.get(ScanStatus.COMPLETED.value, 0)),
            ("Failed", by_status.get(ScanStatus.FAILED.value, 0)),
            ("Hosts seen", hosts_seen),
        ],
        note=f"last {RECENT_SCANS} jobs by recency; status counts cover all jobs.",
    )


async def _flags(session: AsyncSession, site: Site | None) -> dict:
    """The review queue's flag predicates as counts (detection state, so
    dismissed-but-present findings still count — triage lives on /review)."""
    mac_stmt = select(func.count(IPAddress.id)).where(
        IPAddress.custom_fields.has_key("mac_mismatch")  # noqa: W601
    )
    disc_stmt = select(func.count(IPAddress.id)).where(
        IPAddress.status == IPStatus.DISCOVERED
    )
    if site is not None:
        mac_stmt = mac_stmt.join(
            Prefix, IPAddress.prefix_id == Prefix.id
        ).where(Prefix.site_id == site.id)
        disc_stmt = disc_stmt.join(
            Prefix, IPAddress.prefix_id == Prefix.id
        ).where(Prefix.site_id == site.id)
    cable_stmt = select(func.count(DeviceInterface.id)).where(
        DeviceInterface.validation.has_key("cable_mismatch")  # noqa: W601
    )
    dup_stmt = (
        select(func.lower(IPAddress.mac_address), func.count())
        .where(IPAddress.mac_address.is_not(None), IPAddress.mac_address != "")
        .group_by(func.lower(IPAddress.mac_address))
        .having(func.count() > 1)
    )
    if site is not None:
        cable_stmt = cable_stmt.join(
            Device, DeviceInterface.device_id == Device.id
        ).where(Device.site_id == site.id)
        dup_stmt = dup_stmt.join(
            Prefix, IPAddress.prefix_id == Prefix.id
        ).where(Prefix.site_id == site.id)
    mac_n = int(await session.scalar(mac_stmt) or 0)
    cable_n = int(await session.scalar(cable_stmt) or 0)
    dup_n = len((await session.execute(dup_stmt)).all())
    disc_n = int(await session.scalar(disc_stmt) or 0)
    rows = [
        ["mac_mismatch", "MAC mismatches", mac_n,
         "scanner saw a different MAC than documented"],
        ["cable_mismatch", "Cable mismatches", cable_n,
         "SNMP observations contradict documented cabling"],
        ["dup_mac", "Duplicate MACs", dup_n,
         "one MAC claimed by multiple addresses"],
        ["discovered_unconfirmed", "Discovered, unconfirmed", disc_n,
         "scan-found hosts not yet confirmed"],
    ]
    return _section(
        "flags",
        "Flags",
        "/review",
        ["flag", "label", "count", "description"],
        rows,
        metrics=[("Open flags", sum(r[2] for r in rows))],
        note="detection state — review-queue dismissals don't lower these "
        "counts; triage on /review.",
    )


async def _devices(session: AsyncSession, site: Site | None) -> dict:
    stmt = select(Device.id, Device.category, Device.rack_id).order_by(Device.id)
    if site is not None:
        stmt = stmt.where(Device.site_id == site.id)
    devs = (await session.execute(stmt)).all()
    ips = await ips_by_device(session, [d.id for d in devs])

    by_cat: dict[str, int] = {}
    by_health: dict[str, int] = {h: 0 for h in HEALTH_CLASSES}
    unracked = 0
    for d in devs:
        by_cat[d.category or ""] = by_cat.get(d.category or "", 0) + 1
        h = device_health(ips.get(d.id, []))
        by_health[h.value if h else "unmonitored"] += 1
        if d.rack_id is None:
            unracked += 1

    rows = [
        ["category", cat or "(none)", n]
        for cat, n in sorted(by_cat.items(), key=lambda kv: (-kv[1], kv[0]))
    ]
    rows += [["health", h, by_health[h]] for h in HEALTH_CLASSES]
    rows += [
        ["placement", "racked", len(devs) - unracked],
        ["placement", "unracked", unracked],
    ]
    return _section(
        "devices",
        "Devices",
        "/devices",
        ["dimension", "value", "devices"],
        rows,
        metrics=[("Devices", len(devs)), ("Unracked", unracked)],
    )


async def _monitors(session: AsyncSession, site: Site | None) -> dict | None:
    if not await _has_table(session, "monitor_targets"):
        return None
    now = datetime.now(timezone.utc)

    def scoped(stmt):
        if site is None:
            return stmt
        return (
            stmt.outerjoin(Device, MonitorTarget.device_id == Device.id)
            .outerjoin(IPAddress, MonitorTarget.address_id == IPAddress.id)
            .outerjoin(Prefix, IPAddress.prefix_id == Prefix.id)
            .where(or_(Device.site_id == site.id, Prefix.site_id == site.id))
        )

    states = {
        (k.value if hasattr(k, "value") else str(k)): int(c)
        for k, c in (
            await session.execute(
                scoped(select(MonitorTarget.state, func.count())).group_by(
                    MonitorTarget.state
                )
            )
        ).all()
    }
    kinds = {
        (k.value if hasattr(k, "value") else str(k)): int(c)
        for k, c in (
            await session.execute(
                scoped(select(MonitorTarget.kind, func.count())).group_by(
                    MonitorTarget.kind
                )
            )
        ).all()
    }
    enabled = int(
        await session.scalar(
            scoped(select(func.count(MonitorTarget.id))).where(
                MonitorTarget.enabled
            )
        )
        or 0
    )
    due = int(
        await session.scalar(
            scoped(select(func.count(MonitorTarget.id))).where(
                MonitorTarget.enabled, due_where(now)
            )
        )
        or 0
    )
    rows = [
        ["state", st.value, states.get(st.value, 0)] for st in MonitorState
    ]
    rows += [["kind", k, n] for k, n in sorted(kinds.items())]
    total = sum(states.values())
    rows += [
        ["enabled", "yes", enabled],
        ["enabled", "no", total - enabled],
    ]
    return _section(
        "monitors",
        "Monitors",
        "/monitors",
        ["dimension", "value", "targets"],
        rows,
        metrics=[
            ("Up", states.get(MonitorState.UP.value, 0)),
            ("Down", states.get(MonitorState.DOWN.value, 0)),
            ("Unknown", states.get(MonitorState.UNKNOWN.value, 0)),
            ("Due now", due),
        ],
        note="only present when the monitor_targets table exists (v7).",
    )


async def _audits(session: AsyncSession, site: Site | None) -> dict | None:
    """Rack-audit section — gated on the v9 table; emits a stub with the
    audit count so the contract is forward-compatible."""
    if not await _has_table(session, "rack_audits"):
        return None
    total = int(await session.scalar(text("SELECT count(*) FROM rack_audits")) or 0)
    return _section(
        "audits",
        "Rack audits",
        "/review",
        ["metric", "value"],
        [["audits_total", total]],
        metrics=[("Audits", total)],
        note="v9 rack audits — unresolved findings are triaged on /review.",
    )


# ------------------------------------------------------------------ assembly


async def _headline(session: AsyncSession, site: Site | None) -> list[dict]:
    """The payload's top metric strip — the dashboard's own totals,
    narrowed to the site when scoped."""
    sites_stmt = select(func.count(Site.id))
    if site is not None:
        sites_stmt = sites_stmt.where(Site.id == site.id)
    sites_n = int(await session.scalar(sites_stmt) or 0)
    vrfs_stmt = select(func.count(VRF.id))
    prefixes_stmt = select(func.count(Prefix.id))
    devices_stmt = select(func.count(Device.id))
    racks_stmt = select(func.count(Rack.id), func.coalesce(func.sum(Rack.height_u), 0))
    if site is not None:
        vrfs_stmt = vrfs_stmt.where(VRF.site_id == site.id)
        prefixes_stmt = prefixes_stmt.where(Prefix.site_id == site.id)
        devices_stmt = devices_stmt.where(Device.site_id == site.id)
        racks_stmt = racks_stmt.where(Rack.site_id == site.id)
    vrfs_n = int(await session.scalar(vrfs_stmt) or 0)
    prefixes_n = int(await session.scalar(prefixes_stmt) or 0)
    devices_n = int(await session.scalar(devices_stmt) or 0)
    racks_n, u_total = (await session.execute(racks_stmt)).one()
    racks_n, u_total = int(racks_n), int(u_total)

    # used U: distinct occupied slots per rack (same as dashboard_stats)
    slots: dict[int, set[int]] = {}
    dev_stmt = select(Device.rack_id, Device.u_position, Device.u_height).where(
        Device.rack_id.is_not(None), Device.u_position.is_not(None)
    )
    if site is not None:
        dev_stmt = dev_stmt.join(Rack, Device.rack_id == Rack.id).where(
            Rack.site_id == site.id
        )
    for rid, pos, h in (await session.execute(dev_stmt)).all():
        span = {pos + i for i in range(int(h or 1))}
        slots.setdefault(rid, set()).update(span)
    u_used = sum(len(s) for s in slots.values())

    totals = await _ipam_totals(session, site)
    return [
        {"label": "Sites", "value": sites_n},
        {"label": "VRFs", "value": vrfs_n},
        {"label": "Prefixes", "value": prefixes_n},
        {
            "label": "Addresses",
            "value": f"{totals['ips_used']:,} used / {totals['ips_total']:,} usable",
        },
        {"label": "Utilization", "value": f"{totals['utilization_pct']}%"},
        {"label": "Devices", "value": devices_n},
        {"label": "Racks", "value": racks_n},
        {"label": "Rack U", "value": f"{u_used} / {u_total}"},
    ]


SECTION_BUILDERS = [
    _sites,
    _status,
    _utilization,
    _capacity,
    _certs,
    _scans,
    _flags,
    _devices,
    _monitors,
    _audits,
]


async def build_report(session: AsyncSession, site: Site | None) -> dict:
    """One payload, every supported section (bounded). Optional sections
    (monitors, audits) return ``None`` when their table doesn't exist."""
    sections = []
    for build in SECTION_BUILDERS:
        sec = await build(session, site)
        if sec is not None:
            sections.append(sec)
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "site": {"id": site.id, "name": site.name, "slug": site.slug} if site else None,
        "metrics": await _headline(session, site),
        "sections": sections,
    }


def report_sheets(report: dict) -> list[tuple[str, list[str], list[list]]]:
    """``(sheet_name, header, rows)`` for the workbook exporter — one sheet
    per section, stable order, values only."""
    return [
        (s["title"], s["columns"], s["rows"]) for s in report["sections"]
    ]


def digest_text(report: dict) -> str:
    """One-line-per-fact digest for notification channels."""
    scope = report["site"]["name"] if report["site"] else "all sites"
    lines = [
        f"IpamBox estate report — {scope}",
        " · ".join(f"{m['label']}: {m['value']}" for m in report["metrics"]),
    ]
    sec = {s["key"]: s for s in report["sections"]}
    callouts = []

    def metric(key: str, label: str):
        for m in sec.get(key, {}).get("metrics", []):
            if m["label"] == label:
                return m["value"]
        return None

    for key, label, name in (
        ("flags", "Open flags", "Flags"),
        ("certs", "Expiring", "Certs expiring"),
        ("monitors", "Down", "Monitors down"),
        ("scans", "Failed", "Failed scans"),
    ):
        v = metric(key, label)
        if v:
            callouts.append(f"{name}: {v}")
    if callouts:
        lines.append(" · ".join(callouts))
    return "\n".join(lines)


async def emit_report(
    session: AsyncSession, site: Site | None, *, event: str = "report.requested"
) -> int:
    """Fan the report digest through enabled notification channels — the
    same path for the /reports "Email" button and the weekly scheduler.
    Channels carry text + a link; attachments are out of scope."""
    report = await build_report(session, site)
    return await notify.emit(
        event,
        digest_text(report),
        {
            "generated_at": report["generated_at"],
            "site": report["site"],
            "url": "/reports"
            + (f"?site_id={report['site']['id']}" if report["site"] else ""),
            "sections": {s["key"]: s["total_rows"] for s in report["sections"]},
        },
    )
