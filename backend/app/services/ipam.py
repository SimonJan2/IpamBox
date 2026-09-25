import ipaddress
from collections.abc import Iterable
from datetime import datetime, timedelta, timezone

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.ip_address import IPAddress, IPStatus
from app.models.ip_range import IPRange
from app.models.prefix import Prefix, PrefixStatus
from app.models.site import Site
from app.models.vrf import VRF
from app.services import prefix_math


class IPAMError(Exception):
    status_code = 400


class NotFoundError(IPAMError):
    status_code = 404


class ConflictError(IPAMError):
    status_code = 409


# Provenance vocabulary for ip_addresses.source (enum-by-convention, same
# as devices.source), ranked least → most authoritative. A writer may only
# overwrite a row whose stored source ranks lower than or equal to its own:
# scan observations (0) never overwrite imported or manually curated data;
# manual (4) is never rewritten by automation.
SOURCE_RANK = {
    "scan": 0,
    "snmp": 1,
    "integration": 2,
    "import": 3,
    "manual": 4,
}


def may_write(stored: str | None, incoming: str) -> bool:
    """Field-ownership check for source-stamped rows (ip_addresses et al.).

    True when a writer tagged `incoming` may overwrite data on a row whose
    stored source is `stored` — i.e. the incoming source ranks at least as
    high in SOURCE_RANK. Fails closed both ways: an unknown stored value is
    treated as 'manual' (protected), and an unknown incoming tag ranks -1
    so it never wins. Writers call this before overwriting fields they did
    not create (v8 SNMP, v12 controller sync).
    """
    stored_rank = SOURCE_RANK.get(stored or "", SOURCE_RANK["manual"])
    return SOURCE_RANK.get(incoming, -1) >= stored_rank


async def get_or_404(session: AsyncSession, model, obj_id: int):
    obj = await session.get(model, obj_id)
    if obj is None:
        raise NotFoundError(f"{model.__name__} {obj_id} not found")
    return obj


async def check_overlap(
    session: AsyncSession, net, vrf_id: int, exclude_prefix_id: int | None = None
) -> Prefix | None:
    """Return an existing prefix in the same VRF that overlaps `net`, else None."""
    q = select(Prefix).where(
        Prefix.vrf_id == vrf_id, Prefix.status != PrefixStatus.CONTAINER
    )
    if exclude_prefix_id is not None:
        q = q.where(Prefix.id != exclude_prefix_id)
    rows = (await session.execute(q)).scalars().all()
    for row in rows:
        existing = prefix_math.to_network(row.prefix)
        if existing.version == net.version and net.overlaps(existing):
            return row
    return None


def prefix_stats_dict(prefix: Prefix, used: int) -> dict:
    """Stats payload for one prefix given its address count (no DB access).

    IPv6 capacity fields are None: usable_count() returns the full 2^n for
    v6, which is meaningless as a host count and exceeds JS's
    Number.MAX_SAFE_INTEGER — one /64 would poison any summed total. The
    documented-address count (used_ips) stays real; the UI shows '—' for
    capacity."""
    net = prefix_math.to_network(prefix.prefix)
    if net.version == 6:
        return {
            "total_ips": None,
            "usable_ips": None,
            "used_ips": used,
            "free_ips": None,
            "utilization_pct": None,
            "unusable_first": False,
            "unusable_last": False,
        }
    usable = prefix_math.usable_count(net)
    return {
        "total_ips": net.num_addresses,
        "usable_ips": usable,
        "used_ips": used,
        "free_ips": max(0, usable - used),
        "utilization_pct": round(100.0 * used / usable, 1) if usable else 0.0,
        "unusable_first": prefix_math.reserves_boundaries(net),
        "unusable_last": prefix_math.reserves_boundaries(net),
    }


async def prefix_stats(session: AsyncSession, prefix: Prefix) -> dict:
    used = int(
        (await session.execute(
            select(func.count(IPAddress.id)).where(IPAddress.prefix_id == prefix.id)
        )).scalar_one()
    )
    return prefix_stats_dict(prefix, used)


async def reserve_next_available(
    session: AsyncSession,
    prefix_id: int,
    *,
    status: IPStatus = IPStatus.RESERVED,
    hostname: str | None = None,
    mac_address: str | None = None,
    notes: str | None = None,
) -> IPAddress:
    """Atomically allocate the lowest free usable IP in a prefix.

    SERIALIZES on the prefix row (SELECT ... FOR UPDATE); the
    UNIQUE(vrf_id, address) constraint is the hard backstop.
    """
    prefix = (
        await session.execute(
            select(Prefix).where(Prefix.id == prefix_id).with_for_update()
        )
    ).scalar_one_or_none()
    if prefix is None:
        raise NotFoundError(f"prefix {prefix_id} not found")

    net = prefix_math.to_network(prefix.prefix)
    rows = await session.execute(
        select(IPAddress.address_int).where(IPAddress.prefix_id == prefix_id)
    )
    taken = {int(v) for v in rows.scalars()}

    # Defined IP ranges (DHCP pools, reserved blocks) are hands-off for the
    # allocator — they are managed outside IpamBox.
    range_rows = await session.execute(
        select(IPRange.start_int, IPRange.end_int).where(
            IPRange.prefix_id == prefix_id
        )
    )
    excluded = tuple((int(s), int(e)) for s, e in range_rows.all())

    free_int = prefix_math.lowest_free(net, taken, excluded)
    if free_int is None:
        raise ConflictError(f"prefix {net} exhausted")

    addr = ipaddress.ip_address(free_int)
    row = IPAddress(
        address=str(addr),
        address_int=int(addr),
        prefix_id=prefix.id,
        vrf_id=prefix.vrf_id,
        mac_address=mac_address,
        hostname=hostname,
        status=status,
        notes=notes,
        source="manual",
    )
    session.add(row)
    await session.flush()
    return row


async def build_tree(session: AsyncSession) -> list[dict]:
    """Site -> VRF -> nested prefix containment tree."""
    sites = (await session.execute(select(Site).order_by(Site.name))).scalars().all()
    vrfs = (await session.execute(select(VRF).order_by(VRF.name))).scalars().all()
    prefixes = (
        await session.execute(select(Prefix).options(selectinload(Prefix.vlan)))
    ).scalars().all()
    used_counts = dict(
        (
            await session.execute(
                select(IPAddress.prefix_id, func.count(IPAddress.id)).group_by(
                    IPAddress.prefix_id
                )
            )
        ).all()
    )

    def vrf_prefix_tree(vps: list[Prefix]) -> list[dict]:
        """Parent = deepest network that strictly contains the prefix.

        Sorted by (version, network address, prefixlen), a stack of containing
        ancestors yields each parent in O(n log n) overall.
        """
        nets = {p.id: prefix_math.to_network(p.prefix) for p in vps}
        ordered = sorted(
            vps,
            key=lambda p: (
                nets[p.id].version,
                int(nets[p.id].network_address),
                nets[p.id].prefixlen,
            ),
        )
        children_of: dict[int, list[Prefix]] = {p.id: [] for p in vps}
        roots: list[Prefix] = []
        stack: list[Prefix] = []
        for p in ordered:
            net = nets[p.id]
            end = int(net.broadcast_address)
            while stack:
                top = nets[stack[-1].id]
                if int(top.broadcast_address) < end or top.prefixlen >= net.prefixlen:
                    stack.pop()
                else:
                    break
            if stack and nets[stack[-1].id].version == net.version:
                children_of[stack[-1].id].append(p)
            else:
                roots.append(p)
            stack.append(p)

        def prefix_node(p: Prefix) -> dict:
            net = nets[p.id]
            kids = [prefix_node(c) for c in children_of[p.id]]
            # IPv6 reports no usable capacity (2^64 would poison sums and
            # JS can't represent it); used_ips stays the documented count.
            usable = (
                prefix_math.usable_count(net) if net.version == 4 else None
            )
            used = int(used_counts.get(p.id, 0))
            return {
                "id": p.id,
                "prefix": str(net),
                "status": p.status.value,
                "vlan_id": p.vlan_id,
                "vlan_vid": p.vlan.vid if p.vlan else None,
                "vlan_name": p.vlan.name if p.vlan else None,
                "description": p.description,
                "used_ips": used,
                "usable_ips": usable,
                "utilization_pct": (
                    round(100.0 * used / usable, 1) if usable else 0.0
                )
                if net.version == 4
                else None,
                "descendant_count": sum(1 + k["descendant_count"] for k in kids),
                "agg_used_ips": used + sum(k["agg_used_ips"] for k in kids),
                "allocated_pct": round(
                    min(
                        100.0,
                        100.0
                        * sum(nets[c.id].num_addresses for c in children_of[p.id])
                        / net.num_addresses,
                    ),
                    1,
                )
                if kids
                else 0.0,
                "children": kids,
            }

        return [prefix_node(p) for p in roots]

    def vrf_node(v: VRF) -> dict:
        vps = [p for p in prefixes if p.vrf_id == v.id]
        return {"id": v.id, "name": v.name, "rd": v.rd, "prefixes": vrf_prefix_tree(vps)}

    def site_node(s: Site | None) -> dict:
        sid = s.id if s else None
        vlist = [v for v in vrfs if v.site_id == sid]
        return {
            "id": sid,
            "name": s.name if s else "No site",
            "slug": s.slug if s else None,
            "vrfs": [vrf_node(v) for v in vlist],
        }

    nodes = [site_node(s) for s in sites]
    unassigned = [v for v in vrfs if v.site_id is None]
    if unassigned:
        nodes.append(site_node(None))
    return nodes


async def dashboard_stats(session: AsyncSession) -> dict:
    from app.models.scan_job import ScanJob

    sites_total = int((await session.execute(select(func.count(Site.id)))).scalar_one())
    vrfs_total = int((await session.execute(select(func.count(VRF.id)))).scalar_one())
    prefixes_total = int(
        (await session.execute(select(func.count(Prefix.id)))).scalar_one()
    )

    # Aggregated in SQL — the old per-prefix Python loop loaded every row.
    # IPv4 only: usable_count() on v6 returns 2^prefixlen (a /64 ≈ 1.8e19,
    # beyond Number.MAX_SAFE_INTEGER), so a single documented v6 prefix
    # would corrupt ips_total/utilization for the whole install. masklen>=31
    # mirrors usable_bounds: /31 p2p links and /32 hosts use every address.
    v4_usable = case(
        (func.masklen(Prefix.prefix) >= 31, func.pow(2, 32 - func.masklen(Prefix.prefix))),
        else_=func.pow(2, 32 - func.masklen(Prefix.prefix)) - 2,
    )
    ips_total = int(
        (
            await session.execute(
                select(func.coalesce(func.sum(v4_usable), 0)).where(
                    func.family(Prefix.prefix) == 4,
                    Prefix.status != PrefixStatus.CONTAINER,
                )
            )
        ).scalar_one()
    )
    # Same lens for used: only addresses under IPv4 prefixes consume capacity.
    ips_used = int(
        (
            await session.execute(
                select(func.count(IPAddress.id))
                .join(Prefix, IPAddress.prefix_id == Prefix.id)
                .where(func.family(Prefix.prefix) == 4)
            )
        ).scalar_one()
    )
    by_status = {
        s: int(c)
        for s, c in (
            await session.execute(
                select(IPAddress.status, func.count(IPAddress.id)).group_by(IPAddress.status)
            )
        ).all()
    }
    scans_total = int((await session.execute(select(func.count(ScanJob.id)))).scalar_one())
    last_scan = (
        await session.execute(select(ScanJob).order_by(ScanJob.id.desc()).limit(1))
    ).scalar_one_or_none()

    # workbook-imported entities
    from app.models.asset import Asset
    from app.models.certificate import Certificate
    from app.models.circuit import Circuit
    from app.models.device import Device
    from app.models.rack import Rack
    from app.models.service import Service

    circuits_total = int(
        (await session.execute(select(func.count(Circuit.id)))).scalar_one()
    )
    assets_total = int(
        (await session.execute(select(func.count(Asset.id)))).scalar_one()
    )
    services_total = int(
        (await session.execute(select(func.count(Service.id)))).scalar_one()
    )
    # Rack capacity: occupied slots follow used_u semantics — a front+rear
    # pair shares one U, carrier children ride their carrier's span. The
    # per-rack slot sets are merged in Python (same rule as
    # services.racks.used_u) since racks are few and devices are skinny rows.
    racks_total = int(
        (await session.execute(select(func.count(Rack.id)))).scalar_one()
    )
    rack_u_total = int(
        (
            await session.execute(
                select(func.coalesce(func.sum(Rack.height_u), 0))
            )
        ).scalar_one()
    )
    rack_u_used = 0
    rack_slots: dict[int, set[int]] = {}
    for r_id, pos, h in (
        await session.execute(
            select(Device.rack_id, Device.u_position, Device.u_height).where(
                Device.u_position.is_not(None)
            )
        )
    ).all():
        rack_slots.setdefault(r_id, set()).update(range(pos, pos + (h or 1)))
    rack_u_used = sum(len(s) for s in rack_slots.values())
    certificates_total = int(
        (await session.execute(select(func.count(Certificate.id)))).scalar_one()
    )
    soon = datetime.now(timezone.utc).date() + timedelta(days=30)
    certs_expiring_30d = int(
        (
            await session.execute(
                select(func.count(Certificate.id)).where(
                    Certificate.expires_on.is_not(None),
                    Certificate.expires_on <= soon,
                )
            )
        ).scalar_one()
    )
    # Oldest expiry first — already-expired certs (past dates) lead the list.
    certs_expiring = (
        await session.execute(
            select(Certificate)
            .where(
                Certificate.expires_on.is_not(None),
                Certificate.expires_on <= soon,
            )
            .order_by(Certificate.expires_on.asc(), Certificate.id)
            .limit(8)
        )
    ).scalars().all()
    mac_mismatches = int(
        (
            await session.execute(
                select(func.count(IPAddress.id)).where(
                    IPAddress.custom_fields.has_key("mac_mismatch")  # noqa: W601
                )
            )
        ).scalar_one()
    )
    mismatch_rows = (
        await session.execute(
            select(IPAddress)
            .where(IPAddress.custom_fields.has_key("mac_mismatch"))  # noqa: W601
            .order_by(IPAddress.updated_at.desc())
            .limit(8)
        )
    ).scalars().all()
    mac_mismatch_items = [
        {
            "id": r.id,
            "address": str(r.address),
            "prefix_id": r.prefix_id,
            "mac_was": (r.custom_fields or {}).get("mac_mismatch", {}).get("was"),
            # reconcile already updated mac_address to the scanned ("seen") MAC
            "mac_seen": r.mac_address,
            "flagged_at": (r.custom_fields or {}).get("mac_mismatch", {}).get("at"),
        }
        for r in mismatch_rows
    ]

    return {
        "sites_total": sites_total,
        "vrfs_total": vrfs_total,
        "prefixes_total": prefixes_total,
        "ips_total": ips_total,
        "ips_used": ips_used,
        "ips_free": max(0, ips_total - ips_used),
        "utilization_pct": round(100.0 * ips_used / ips_total, 1) if ips_total else 0.0,
        "devices_active": by_status.get(IPStatus.ACTIVE, 0),
        "devices_discovered": by_status.get(IPStatus.DISCOVERED, 0),
        "devices_offline": by_status.get(IPStatus.OFFLINE, 0),
        "devices_reserved": by_status.get(IPStatus.RESERVED, 0),
        "scans_total": scans_total,
        "last_scan": last_scan,
        "circuits_total": circuits_total,
        "certificates_total": certificates_total,
        "certs_expiring_30d": certs_expiring_30d,
        "assets_total": assets_total,
        "services_total": services_total,
        "racks_total": racks_total,
        "rack_u_used": rack_u_used,
        "rack_u_total": rack_u_total,
        "mac_mismatches": mac_mismatches,
        "certs_expiring": certs_expiring,
        "mac_mismatch_items": mac_mismatch_items,
    }


def vrf_name_for(site_name: str, code: str | None, number: int | None) -> str:
    """VRF naming convention: the site code, then site-N, then a name slug."""
    if code:
        return code
    if number is not None:
        return f"site-{number}"
    return slugify(site_name)[:60]


def slugify(name: str) -> str:
    import re
    import unicodedata

    # \w keeps non-ASCII letters (Hebrew site names) instead of collapsing
    # them all to the same "site" fallback; NFKC folds compatibility chars.
    norm = unicodedata.normalize("NFKC", name).lower()
    slug = re.sub(r"[^\w]+", "-", norm).strip("-")
    return slug or "site"


async def slugify_unique(session: AsyncSession, name: str) -> str:
    """slugify + dedup against existing site slugs (site, site-2, site-3…)."""
    base = slugify(name)
    existing = set((await session.execute(select(Site.slug))).scalars())
    slug = base
    n = 2
    while slug in existing:
        slug = f"{base}-{n}"
        n += 1
    return slug
