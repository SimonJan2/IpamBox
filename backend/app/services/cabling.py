"""Cabling helpers: grouped lookups, peer resolution, the L1 trace,
per-device coverage stats, and the legacy free-text matcher.

Trace model: an interface terminates at most one cable. At a `patch`-kind
interface the path continues through its `pair_interface_id` partner on the
same device (the panel's front↔back link — not a cable, so the hop's cable
fields stay null). The walk runs both ways from the start interface so a
trace launched mid-chain still returns the whole path; a visited set keeps
cycles (and ping-pong pairs) terminating at MAX_TRACE_HOPS.
"""
from collections import defaultdict

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cabling import Cable, DeviceInterface, InterfaceKind
from app.models.device import Device
from app.models.ip_address import IPAddress
from app.schemas.cabling import (
    CableEndOut,
    CableTraceHop,
    ConnectedIpRef,
    InterfacePeerOut,
)
from app.schemas.common import ip_display
from app.schemas.ip_address import ConnectedInterfaceRef

MAX_TRACE_HOPS = 10


async def cable_for(session: AsyncSession, interface_id: int) -> Cable | None:
    """The (at most one) cable terminating at an interface, on either end."""
    return (
        (
            await session.execute(
                select(Cable).where(
                    or_(
                        Cable.a_interface_id == interface_id,
                        Cable.b_interface_id == interface_id,
                    )
                )
            )
        )
        .scalars()
        .first()
    )


async def pair_of(
    session: AsyncSession, iface: DeviceInterface
) -> DeviceInterface | None:
    """A patch position's front↔back partner on the SAME device.

    Follows the self-FK whichever direction it was recorded (the generate
    endpoint sets both; manual edits may set one). Returns None when the
    link is missing or ambiguous — a silent wrong hop is worse than none.
    """
    if iface.pair_interface_id is not None:
        pair = await session.get(DeviceInterface, iface.pair_interface_id)
        if pair is not None and pair.device_id == iface.device_id:
            return pair
        return None
    claimants = (
        (
            await session.execute(
                select(DeviceInterface).where(
                    DeviceInterface.pair_interface_id == iface.id
                )
            )
        )
        .scalars()
        .all()
    )
    claimants = [c for c in claimants if c.device_id == iface.device_id]
    return claimants[0] if len(claimants) == 1 else None


async def interface_stats(
    session: AsyncSession, device_ids: list[int]
) -> dict[int, tuple[int, int]]:
    """device_id -> (interface_count, cabled_count). Two grouped queries —
    the anti-N+1 path for device detail, the device list and elevations."""
    if not device_ids:
        return {}
    totals = dict(
        (
            await session.execute(
                select(DeviceInterface.device_id, func.count())
                .where(DeviceInterface.device_id.in_(device_ids))
                .group_by(DeviceInterface.device_id)
            )
        ).all()
    )
    # distinct on the interface id — a row present on both end columns
    # (possible only via direct SQL) still counts as one cabled port.
    cabled = dict(
        (
            await session.execute(
                select(
                    DeviceInterface.device_id,
                    func.count(func.distinct(DeviceInterface.id)),
                )
                .select_from(DeviceInterface)
                .join(
                    Cable,
                    or_(
                        Cable.a_interface_id == DeviceInterface.id,
                        Cable.b_interface_id == DeviceInterface.id,
                    ),
                )
                .where(DeviceInterface.device_id.in_(device_ids))
                .group_by(DeviceInterface.device_id)
            )
        ).all()
    )
    return {d: (totals.get(d, 0), cabled.get(d, 0)) for d in device_ids}


async def peers_for(
    session: AsyncSession, interfaces: list[DeviceInterface]
) -> dict[int, InterfacePeerOut]:
    """interface_id -> the far end of its cable (device/interface names
    resolved). Two grouped queries regardless of list size."""
    ids = [i.id for i in interfaces]
    if not ids:
        return {}
    cables = (
        (
            await session.execute(
                select(Cable).where(
                    or_(
                        Cable.a_interface_id.in_(ids),
                        Cable.b_interface_id.in_(ids),
                    )
                )
            )
        )
        .scalars()
        .all()
    )
    # interface_id (our side) -> (cable, peer interface id)
    ends: dict[int, tuple[Cable, int]] = {}
    peer_ids: set[int] = set()
    for c in cables:
        if c.a_interface_id in ids:
            ends[c.a_interface_id] = (c, c.b_interface_id)
            peer_ids.add(c.b_interface_id)
        if c.b_interface_id in ids:
            ends[c.b_interface_id] = (c, c.a_interface_id)
            peer_ids.add(c.a_interface_id)
    if not peer_ids:
        return {}
    peers = (
        (
            await session.execute(
                select(DeviceInterface, Device)
                .join(Device, DeviceInterface.device_id == Device.id)
                .where(DeviceInterface.id.in_(peer_ids))
            )
        )
        .all()
    )
    peer_info = {i.id: (i, d) for i, d in peers}
    out: dict[int, InterfacePeerOut] = {}
    for iface_id, (cable, peer_id) in ends.items():
        info = peer_info.get(peer_id)
        if info is None:
            continue
        iface, device = info
        out[iface_id] = InterfacePeerOut(
            cable_id=cable.id,
            cable_kind=cable.kind,
            cable_label=cable.label,
            interface_id=peer_id,
            interface_name=iface.name,
            device_id=device.id,
            device_name=device.name,
        )
    return out


async def cable_ends_for(
    session: AsyncSession, cables: list[Cable]
) -> dict[int, tuple[CableEndOut | None, CableEndOut | None]]:
    """cable_id -> (a-end, b-end) resolved for CableOut.a / .b."""
    ids = {c.a_interface_id for c in cables} | {
        c.b_interface_id for c in cables
    }
    if not ids:
        return {}
    rows = (
        (
            await session.execute(
                select(DeviceInterface, Device)
                .join(Device, DeviceInterface.device_id == Device.id)
                .where(DeviceInterface.id.in_(ids))
            )
        )
        .all()
    )
    info = {i.id: CableEndOut(
        interface_id=i.id,
        interface_name=i.name,
        device_id=d.id,
        device_name=d.name,
    ) for i, d in rows}
    return {
        c.id: (info.get(c.a_interface_id), info.get(c.b_interface_id))
        for c in cables
    }


async def stamp_connected_ips(session: AsyncSession, rows) -> None:
    """Populate ``connected_ip`` refs on DeviceInterfaceOut rows in one
    grouped query. Targets Out rows, not ORM objects — on the ORM the name
    is the relationship and assigning a ref would corrupt it."""
    ids = {r.connected_ip_id for r in rows if r.connected_ip_id}
    if not ids:
        return
    ips = {
        r.id: r
        for r in (
            (
                await session.execute(
                    select(IPAddress).where(IPAddress.id.in_(ids))
                )
            )
            .scalars()
            .all()
        )
    }
    for iface in rows:
        ip = ips.get(iface.connected_ip_id or 0)
        if ip is not None:
            iface.connected_ip = ConnectedIpRef(
                id=ip.id,
                label=(ip_display(ip.address) or "")
                + (f" ({ip.hostname})" if ip.hostname else ""),
                prefix_id=ip.prefix_id,
            )


async def stamp_connected_interfaces(session: AsyncSession, rows) -> None:
    """Populate ``connected_interface`` on IPAddressOut rows — the resolved
    far-end port label (device name + interface name), one grouped query."""
    ids = {r.connected_interface_id for r in rows if r.connected_interface_id}
    if not ids:
        return
    hits = (
        (
            await session.execute(
                select(DeviceInterface, Device)
                .join(Device, DeviceInterface.device_id == Device.id)
                .where(DeviceInterface.id.in_(ids))
            )
        )
        .all()
    )
    info = {i.id: (i, d) for i, d in hits}
    for r in rows:
        hit = info.get(r.connected_interface_id or 0)
        if hit is not None:
            iface, device = hit
            r.connected_interface = ConnectedInterfaceRef(
                id=iface.id,
                name=iface.name,
                device_id=device.id,
                device_name=device.name,
            )


async def trace_path(
    session: AsyncSession,
    start: DeviceInterface,
    max_hops: int = MAX_TRACE_HOPS,
) -> list[CableTraceHop]:
    """The L1 path through an interface, ordered end to end.

    From `start` the walk follows cable → peer interface; at a `patch` peer
    it additionally hops to the pair on the same device and keeps going.
    Starting mid-chain explores the pair direction first so the returned
    list still holds the whole path. Visited-set + max_hops bound cycles.
    """
    visited: set[int] = {start.id}
    remaining = max_hops - 1  # the start hop counts toward the total

    async def hop(iface: DeviceInterface, cable: Cable | None) -> CableTraceHop:
        device = await session.get(Device, iface.device_id)
        return CableTraceHop(
            device_id=iface.device_id,
            device_name=device.name if device else f"device {iface.device_id}",
            interface_id=iface.id,
            interface_name=iface.name,
            cable_id=cable.id if cable else None,
            cable_kind=cable.kind if cable else None,
            cable_label=cable.label if cable else None,
        )

    async def walk(cur: DeviceInterface, hops: list[CableTraceHop]) -> None:
        """Append hops moving away from `cur` (already emitted/visited)."""
        nonlocal remaining
        while remaining > 0:
            cable = await cable_for(session, cur.id)
            if cable is None:
                return
            peer_id = (
                cable.b_interface_id
                if cable.a_interface_id == cur.id
                else cable.a_interface_id
            )
            if peer_id in visited:
                return
            peer = await session.get(DeviceInterface, peer_id)
            if peer is None:
                return
            visited.add(peer.id)
            hops.append(await hop(peer, cable))
            remaining -= 1
            cur = peer
            # Patch-panel pass-through: front port's pair is the back port
            # on the same panel device.
            if cur.kind == InterfaceKind.PATCH and remaining > 0:
                pair = await pair_of(session, cur)
                if pair is None or pair.id in visited:
                    return
                visited.add(pair.id)
                hops.append(await hop(pair, None))
                remaining -= 1
                cur = pair

    start_hop = await hop(start, None)
    # Reverse direction: out through the start's own pair first (patch
    # ports launched mid-panel still surface the full chain).
    back: list[CableTraceHop] = []
    if start.kind == InterfaceKind.PATCH:
        pair = await pair_of(session, start)
        if pair is not None and pair.id not in visited:
            visited.add(pair.id)
            back.append(await hop(pair, None))
            remaining -= 1
            await walk(pair, back)
    fwd: list[CableTraceHop] = []
    await walk(start, fwd)
    return [*reversed(back), start_hop, *fwd]


async def match_free_text(session: AsyncSession) -> dict:
    """Link legacy switch_name/switch_port pairs to real interfaces.

    For every ip_address lacking connected_interface_id: devices whose name
    exactly matches switch_name are candidates; among them, the ones owning
    an interface named exactly switch_port. Exactly one candidate → link;
    none → unmatched; more than one → ambiguous (reported, never guessed).
    Callers commit — ORM attribute writes produce changelog entries, which
    is what makes the run reviewable.
    """
    rows = (
        (
            await session.execute(
                select(IPAddress).where(
                    IPAddress.connected_interface_id.is_(None),
                    IPAddress.switch_name.is_not(None),
                    IPAddress.switch_port.is_not(None),
                )
            )
        )
        .scalars()
        .all()
    )
    by_name: dict[str, list[int]] = defaultdict(list)
    for did, name in (
        await session.execute(select(Device.id, Device.name))
    ).all():
        by_name[name.strip()].append(did)
    by_dev_port: dict[tuple[int, str], int] = {}
    for iface in (
        (
            await session.execute(
                select(DeviceInterface.id, DeviceInterface.device_id,
                       DeviceInterface.name)
            )
        )
        .all()
    ):
        by_dev_port[(iface.device_id, iface.name.strip())] = iface.id

    report = {"matched": [], "ambiguous": [], "unmatched": []}
    for ip in rows:
        dev_ids = by_name.get((ip.switch_name or "").strip(), [])
        candidates = [
            by_dev_port[(d, ip.switch_port.strip())]
            for d in dev_ids
            if (d, (ip.switch_port or "").strip()) in by_dev_port
        ]
        if len(candidates) == 1:
            ip.connected_interface_id = candidates[0]
            report["matched"].append(ip.id)
        elif len(candidates) > 1:
            report["ambiguous"].append(ip.id)
        else:
            report["unmatched"].append(ip.id)
    return report
