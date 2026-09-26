"""Topology map (V10): GET /topology/graph + GET/PUT /topology/layout.

One honest site-scale payload — a single aggregate beats a paginated
graph API at this size. Nodes are devices (racked or not) plus,
optionally, IP-only hosts with no device (the map stays honest about
what isn't documented). Edges are *documented cables* collapsed
device↔device: a parallel-cable pair becomes one edge with count +
union of kinds, and `mismatched` rolls up v8.2 cable_mismatch flags.

Deliberate choice: patch-panel chains do NOT resolve through panels —
an edge means "a cable directly joins these two devices". The L1 trace
(/cables/trace) already owns hop-through semantics; duplicating it here
would redraw a derived view as if it were fact.

Read-only lens: the only writes are layout positions, which are UI
state — see models/diagram_layout.py for why that table skips the
changelog but joins BACKUP_TABLES.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.core.db import get_session
from app.core.deps import DATA_READ, DATA_WRITE, require_perm
from app.models.cabling import Cable, DeviceInterface
from app.models.device import Device
from app.models.diagram_layout import DiagramLayout
from app.models.ip_address import IPAddress
from app.models.prefix import Prefix
from app.models.rack import Rack, RackGroup
from app.models.site import Site
from app.schemas.common import ip_display
from app.schemas.topology import (
    DiagramLayoutOut,
    DiagramLayoutPut,
    TopologyEdge,
    TopologyEdgeCable,
    TopologyGraph,
    TopologyGroups,
    TopologyNode,
    TopologyRackGroupRef,
    TopologyRackRef,
    TopologySiteRef,
)
from app.services.cabling import interface_stats
from app.services.devices import device_health, ips_by_device

router = APIRouter(
    prefix="/topology",
    tags=["topology"],
    dependencies=[Depends(require_perm(DATA_READ))],
)

UNMONITORED = "unmonitored"


@router.get("/graph", response_model=TopologyGraph)
async def topology_graph(
    site_id: int | None = None,
    include_unlinked: bool = False,
    session: AsyncSession = Depends(get_session),
):
    dev_stmt = (
        select(
            Device,
            Rack.site_id.label("rack_site_id"),
            Rack.group_id.label("rack_group_id"),
        )
        .outerjoin(Rack, Device.rack_id == Rack.id)
        .order_by(Device.name, Device.id)
    )
    # Same effective-site rule as /cables: a device with no site_id but
    # racked at a site belongs to that site's canvas.
    if site_id is not None:
        dev_stmt = dev_stmt.where(
            func.coalesce(Device.site_id, Rack.site_id) == site_id
        )
    dev_rows = (await session.execute(dev_stmt)).all()

    dev_ids = [d.id for d, _, _ in dev_rows]
    ips_map = await ips_by_device(session, dev_ids)
    stats = await interface_stats(session, dev_ids)

    nodes: list[TopologyNode] = []
    for d, rack_site_id, rack_group_id in dev_rows:
        health = device_health(ips_map.get(d.id, []))
        iface_total, cabled = stats.get(d.id, (0, 0))
        nodes.append(
            TopologyNode(
                id=f"dev-{d.id}",
                kind="device",
                label=d.name,
                health=health.value if health is not None else UNMONITORED,
                site_id=d.site_id if d.site_id is not None else rack_site_id,
                rack_id=d.rack_id,
                rack_group_id=rack_group_id,
                device_type=d.device_type,
                interface_count=iface_total,
                cabled_count=cabled,
                href=f"/devices/{d.id}",
            )
        )

    if include_unlinked:
        ip_stmt = (
            select(IPAddress, Prefix.site_id)
            .join(Prefix, IPAddress.prefix_id == Prefix.id)
            .where(IPAddress.device_id.is_(None))
            .order_by(IPAddress.id)
        )
        if site_id is not None:
            ip_stmt = ip_stmt.where(Prefix.site_id == site_id)
        for ip, ip_site_id in (await session.execute(ip_stmt)).all():
            addr = ip_display(ip.address) or str(ip.address)
            nodes.append(
                TopologyNode(
                    id=f"unlinked-{ip.id}",
                    kind="ip",
                    label=addr + (f" ({ip.hostname})" if ip.hostname else ""),
                    health=ip.status.value,
                    site_id=ip_site_id,
                    hostname=ip.hostname,
                    prefix_id=ip.prefix_id,
                    href=f"/prefixes/{ip.prefix_id}?q={addr}",
                )
            )

    # Edges: every documented cable joined to both ends' devices, then
    # collapsed device↔device. Ends outside the node set (filtered out
    # by site_id) can't be drawn, so their cables drop out entirely.
    a_iface = aliased(DeviceInterface)
    b_iface = aliased(DeviceInterface)
    cable_rows = (
        (
            await session.execute(
                select(Cable, a_iface, b_iface)
                .join(a_iface, Cable.a_interface_id == a_iface.id)
                .join(b_iface, Cable.b_interface_id == b_iface.id)
            )
        )
        .all()
    )
    dev_names = {d.id: d.name for d, _, _ in dev_rows}
    edge_map: dict[tuple[int, int], dict] = {}
    for cable, ia, ib in cable_rows:
        if ia.device_id not in dev_names or ib.device_id not in dev_names:
            continue
        key = (min(ia.device_id, ib.device_id), max(ia.device_id, ib.device_id))
        e = edge_map.setdefault(
            key,
            {"count": 0, "kinds": set(), "mismatched": False, "cables": []},
        )
        e["count"] += 1
        e["kinds"].add(cable.kind.value)
        e["mismatched"] = e["mismatched"] or any(
            (iface.validation or {}).get("cable_mismatch")
            for iface in (ia, ib)
        )
        e["cables"].append(
            TopologyEdgeCable(
                id=cable.id,
                kind=cable.kind.value,
                label=cable.label,
                a_label=f"{dev_names[ia.device_id]} · {ia.name}",
                b_label=f"{dev_names[ib.device_id]} · {ib.name}",
                a_device_id=ia.device_id,
                b_device_id=ib.device_id,
                a_interface_id=ia.id,
                b_interface_id=ib.id,
            )
        )
    edges = [
        TopologyEdge(
            a=f"dev-{da}",
            b=f"dev-{db}",
            count=e["count"],
            kinds=sorted(e["kinds"]),
            mismatched=e["mismatched"],
            cables=sorted(e["cables"], key=lambda c: c.id),
        )
        for (da, db), e in sorted(edge_map.items())
    ]

    # Groups ship unfiltered — the site picker and group lanes need the
    # full vocabulary even when the node set is site-scoped.
    sites = (
        (await session.execute(select(Site).order_by(Site.name)))
        .scalars()
        .all()
    )
    rack_groups = (
        (await session.execute(select(RackGroup).order_by(RackGroup.name)))
        .scalars()
        .all()
    )
    racks = (
        (await session.execute(select(Rack).order_by(Rack.name)))
        .scalars()
        .all()
    )

    return TopologyGraph(
        nodes=nodes,
        edges=edges,
        groups=TopologyGroups(
            sites=[TopologySiteRef(id=s.id, name=s.name) for s in sites],
            rack_groups=[
                TopologyRackGroupRef(id=g.id, name=g.name, site_id=g.site_id)
                for g in rack_groups
            ],
            racks=[
                TopologyRackRef(
                    id=r.id, name=r.name, site_id=r.site_id, group_id=r.group_id
                )
                for r in racks
            ],
        ),
    )


@router.get("/layout", response_model=DiagramLayoutOut)
async def get_layout(
    key: str = Query(default="main", max_length=64),
    session: AsyncSession = Depends(get_session),
):
    row = await session.scalar(
        select(DiagramLayout).where(DiagramLayout.key == key)
    )
    if row is None:
        # No saved layout is not an error — the canvas falls back to elk.
        return DiagramLayoutOut(key=key, positions={}, updated_at=None)
    return DiagramLayoutOut(
        key=row.key, positions=row.positions, updated_at=row.updated_at
    )


@router.put(
    "/layout",
    response_model=DiagramLayoutOut,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def put_layout(
    body: DiagramLayoutPut, session: AsyncSession = Depends(get_session)
):
    positions = {k: v.model_dump() for k, v in body.positions.items()}
    row = await session.scalar(
        select(DiagramLayout).where(DiagramLayout.key == body.key)
    )
    if row is None:
        row = DiagramLayout(key=body.key, positions=positions)
        session.add(row)
    else:
        row.positions = positions
    try:
        await session.commit()
    except IntegrityError:
        # Concurrent first-save raced us on the unique key — fold into
        # the winner's row instead of failing the save.
        await session.rollback()
        row = await session.scalar(
            select(DiagramLayout).where(DiagramLayout.key == body.key)
        )
        row.positions = positions
        await session.commit()
    await session.refresh(row)
    return DiagramLayoutOut(
        key=row.key, positions=row.positions, updated_at=row.updated_at
    )
