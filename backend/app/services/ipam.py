import ipaddress
from collections.abc import Iterable

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ip_address import IPAddress, IPStatus
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


async def prefix_stats(session: AsyncSession, prefix: Prefix) -> dict:
    net = prefix_math.to_network(prefix.prefix)
    used = int(
        (await session.execute(
            select(func.count(IPAddress.id)).where(IPAddress.prefix_id == prefix.id)
        )).scalar_one()
    )
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

    free_int = prefix_math.lowest_free(net, taken)
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
    )
    session.add(row)
    await session.flush()
    return row


async def build_tree(session: AsyncSession) -> list[dict]:
    """Site -> VRF -> nested prefix containment tree."""
    sites = (await session.execute(select(Site).order_by(Site.name))).scalars().all()
    vrfs = (await session.execute(select(VRF).order_by(VRF.name))).scalars().all()
    prefixes = (await session.execute(select(Prefix))).scalars().all()

    def prefix_node(p: Prefix, siblings: list[Prefix], nets: dict[int, object]) -> dict:
        net = nets[p.id]
        children = []
        for c in siblings:
            cnet = nets[c.id]
            if cnet.version != net.version or cnet.prefixlen <= net.prefixlen:
                continue
            if cnet.subnet_of(net):
                # direct child if no intermediate sibling contains it
                if not any(
                    cnet.subnet_of(nets[o.id])
                    for o in siblings
                    if o.id != c.id
                    and nets[o.id].prefixlen > net.prefixlen
                    and nets[o.id].prefixlen < cnet.prefixlen
                    and cnet.subnet_of(nets[o.id])
                ):
                    children.append(prefix_node(c, siblings, nets))
        children.sort(key=lambda n: int(prefix_math.to_network(n["prefix"]).network_address))
        return {
            "id": p.id,
            "prefix": str(net),
            "status": p.status.value,
            "vlan_id": p.vlan_id,
            "vlan_name": p.vlan_name,
            "description": p.description,
            "children": children,
        }

    def vrf_node(v: VRF) -> dict:
        vps = [p for p in prefixes if p.vrf_id == v.id]
        nets = {p.id: prefix_math.to_network(p.prefix) for p in vps}
        roots = [
            p
            for p in vps
            if prefix_math.parent_chain(nets[p.id], [nets[o.id] for o in vps]) is None
        ]
        tree = sorted(
            (prefix_node(p, vps, nets) for p in roots),
            key=lambda n: (":" in n["prefix"], int(prefix_math.to_network(n["prefix"]).network_address)),
        )
        return {"id": v.id, "name": v.name, "rd": v.rd, "prefixes": tree}

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
    prefixes = (await session.execute(select(Prefix))).scalars().all()

    ips_total = 0
    for p in prefixes:
        if p.status != PrefixStatus.CONTAINER:
            ips_total += prefix_math.usable_count(prefix_math.to_network(p.prefix))

    ips_used = int((await session.execute(select(func.count(IPAddress.id)))).scalar_one())
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

    return {
        "sites_total": sites_total,
        "vrfs_total": vrfs_total,
        "prefixes_total": len(prefixes),
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
    }


def slugify(name: str) -> str:
    import re

    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug or "site"
