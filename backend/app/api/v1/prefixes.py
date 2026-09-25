import ipaddress
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import String, cast, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import get_settings
from app.core.db import get_session
from app.core.deps import DATA_DELETE, DATA_WRITE, require_perm
from app.models.ip_address import IPAddress
from app.models.prefix import Prefix, PrefixStatus
from app.models.site import Site
from app.models.tag import TagAssignment
from app.models.vlan import VLAN
from app.models.vrf import VRF
from app.schemas.ip_address import IPAddressOut, IPAddressPage
from app.schemas.prefix import (
    AllocateIPRequest,
    AvailableIPOut,
    PrefixCreate,
    PrefixOut,
    PrefixSplitOut,
    PrefixUpdate,
)
from app.services import prefix_math
from app.services.colors import stamp_colors
from app.services.csv_export import csv_response
from app.services.ipam import (
    IPAMError,
    build_tree,
    check_overlap,
    get_or_404,
    prefix_stats,
    prefix_stats_dict,
    reserve_next_available,
)
from app.services.ranges import stamp_range_roles, sync_technical_addresses

router = APIRouter(prefix="/prefixes", tags=["prefixes"])


async def _with_stats(session: AsyncSession, p: Prefix) -> PrefixOut:
    return PrefixOut.model_validate(p).model_copy(update=await prefix_stats(session, p))


@router.get("/tree")
async def prefix_tree(session: AsyncSession = Depends(get_session)):
    """Site -> VRF -> nested prefix containment hierarchy."""
    return await build_tree(session)


async def _prefix_rows(
    session: AsyncSession,
    vrf_id: int | None,
    site_id: int | None,
    status: PrefixStatus | None,
    tag_id: int | None,
    q: str | None,
) -> list[Prefix]:
    """Shared list/export filter construction — one predicate, two callers."""
    stmt = select(Prefix).options(selectinload(Prefix.vlan), selectinload(Prefix.vrf))
    if vrf_id is not None:
        stmt = stmt.where(Prefix.vrf_id == vrf_id)
    if site_id is not None:
        stmt = stmt.where(Prefix.site_id == site_id)
    if status is not None:
        stmt = stmt.where(Prefix.status == status)
    if tag_id is not None:
        stmt = stmt.where(
            Prefix.id.in_(
                select(TagAssignment.object_id).where(
                    TagAssignment.object_type == "Prefix",
                    TagAssignment.tag_id == tag_id,
                )
            )
        )
    if q:
        # CIDR text match pushed into SQL — a post-fetch filter would make
        # callers paginate before filtering.
        stmt = stmt.where(cast(Prefix.prefix, String).ilike(f"%{q}%"))
    return (await session.execute(stmt)).scalars().all()


@router.get("/export.csv")
async def export_prefixes(
    vrf_id: int | None = None,
    site_id: int | None = None,
    status: PrefixStatus | None = None,
    tag_id: int | None = None,
    q: str | None = Query(default=None, description="substring match on CIDR"),
    session: AsyncSession = Depends(get_session),
):
    """Same filters as the list endpoint — a filtered view exports what it shows."""
    rows = await _prefix_rows(session, vrf_id, site_id, status, tag_id, q)
    filtered = any(x is not None for x in (vrf_id, site_id, status, tag_id, q))
    return csv_response(
        "prefixes-filtered.csv" if filtered else "prefixes.csv",
        ["prefix", "vrf", "site_id", "vlan", "status", "description", "created_at"],
        [
            [
                str(p.prefix),
                p.vrf.name,
                p.site_id,
                f"{p.vlan.vid} {p.vlan.name}" if p.vlan else "",
                p.status.value,
                p.description or "",
                p.created_at.isoformat() if p.created_at else "",
            ]
            for p in rows
        ],
    )


@router.get("", response_model=list[PrefixOut])
async def list_prefixes(
    vrf_id: int | None = None,
    site_id: int | None = None,
    status: PrefixStatus | None = None,
    tag_id: int | None = None,
    q: str | None = Query(default=None, description="substring match on CIDR"),
    order_by: Literal["prefix", "utilization"] = "prefix",
    limit: int | None = Query(default=None, ge=1, le=1000),
    session: AsyncSession = Depends(get_session),
):
    rows = await _prefix_rows(session, vrf_id, site_id, status, tag_id, q)

    # One grouped COUNT covers every returned prefix — not a per-prefix
    # round-trip (utilization ordering needs the counts up front anyway).
    used_counts: dict[int, int] = {}
    if rows:
        used_counts = {
            pid: int(n)
            for pid, n in (
                await session.execute(
                    select(IPAddress.prefix_id, func.count(IPAddress.id))
                    .where(IPAddress.prefix_id.in_([p.id for p in rows]))
                    .group_by(IPAddress.prefix_id)
                )
            ).all()
        }
    pairs = [
        (p, prefix_stats_dict(p, used_counts.get(p.id, 0))) for p in rows
    ]

    def _net_key(p: Prefix) -> int:
        return int(prefix_math.to_network(p.prefix).network_address)

    if order_by == "utilization":
        # IPv6 prefixes report utilization_pct=None — sort them last.
        pairs.sort(
            key=lambda t: (
                t[1]["utilization_pct"] is None,
                -(t[1]["utilization_pct"] or 0),
                _net_key(t[0]),
            )
        )
    else:
        # order by network address integer for a natural hierarchy view
        pairs.sort(key=lambda t: _net_key(t[0]))
    if limit is not None:
        pairs = pairs[:limit]
    return [
        PrefixOut.model_validate(p).model_copy(update=s) for p, s in pairs
    ]


@router.post(
    "",
    response_model=PrefixOut,
    status_code=201,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def create_prefix(body: PrefixCreate, session: AsyncSession = Depends(get_session)):
    net = prefix_math.to_network(body.prefix)
    try:
        await get_or_404(session, VRF, body.vrf_id)
        if body.site_id is not None:
            await get_or_404(session, Site, body.site_id)
        if body.vlan_id is not None:
            await get_or_404(session, VLAN, body.vlan_id)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))

    # Containers are exempt from the no-overlap rule (they exist to hold children)
    conflict = (
        None
        if body.status == PrefixStatus.CONTAINER
        else await check_overlap(session, net, body.vrf_id)
    )
    if conflict is not None:
        raise HTTPException(
            409,
            f"{net} overlaps existing prefix {conflict.prefix} (id={conflict.id}) in this VRF",
        )

    prefix = Prefix(**body.model_dump())
    session.add(prefix)
    try:
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        if "excl_prefixes_no_overlap" in str(e):
            raise HTTPException(409, f"{net} overlaps an existing prefix in this VRF")
        raise HTTPException(400, "invalid prefix data")
    return await get_prefix(prefix.id, session)


@router.get("/{prefix_id}", response_model=PrefixOut)
async def get_prefix(prefix_id: int, session: AsyncSession = Depends(get_session)):
    prefix = (
        await session.execute(
            select(Prefix)
            .options(selectinload(Prefix.vlan))
            .where(Prefix.id == prefix_id)
        )
    ).scalar_one_or_none()
    if prefix is None:
        raise HTTPException(404, f"Prefix {prefix_id} not found")
    return await _with_stats(session, prefix)


@router.patch(
    "/{prefix_id}",
    response_model=PrefixOut,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def update_prefix(prefix_id: int, body: PrefixUpdate, session: AsyncSession = Depends(get_session)):
    prefix = (
        await session.execute(
            select(Prefix)
            .options(selectinload(Prefix.vlan))
            .where(Prefix.id == prefix_id)
        )
    ).scalar_one_or_none()
    if prefix is None:
        raise HTTPException(404, f"Prefix {prefix_id} not found")
    data = body.model_dump(exclude_unset=True)
    new_vrf = data.get("vrf_id")
    moving_vrf = new_vrf is not None and new_vrf != prefix.vrf_id
    net = prefix_math.to_network(prefix.prefix)
    if data.get("gateway") is not None:
        gw = ipaddress.ip_address(data["gateway"])
        if gw.version != net.version or gw not in net:
            raise HTTPException(422, f"gateway {gw} is not inside prefix {net}")
    try:
        if data.get("vlan_id") is not None:
            await get_or_404(session, VLAN, data["vlan_id"])
        if moving_vrf:
            await get_or_404(session, VRF, new_vrf)
            if prefix.status == PrefixStatus.CONTAINER:
                # Children of a container live in its VRF — refuse to strand them.
                siblings = (
                    await session.execute(
                        select(Prefix).where(
                            Prefix.vrf_id == prefix.vrf_id, Prefix.id != prefix.id
                        )
                    )
                ).scalars().all()
                children = [
                    s for s in siblings
                    if (sn := prefix_math.to_network(s.prefix)).version == net.version
                    and sn.subnet_of(net)
                ]
                if children:
                    raise HTTPException(
                        409,
                        f"container has child prefixes in this VRF "
                        f"({', '.join(str(s.prefix) for s in children[:5])}) — "
                        "move or delete them first",
                    )
            else:
                conflict = await check_overlap(session, net, new_vrf)
                if conflict is not None:
                    raise HTTPException(
                        409,
                        f"{net} overlaps existing prefix {conflict.prefix} "
                        f"(id={conflict.id}) in the target VRF",
                    )
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))
    for field, value in data.items():
        setattr(prefix, field, value)
    if "gateway" in data or "dns_servers" in data:
        # Mirror the technical addresses into reserved, marker-tagged rows —
        # removed rows drop only when they're still exactly what we wrote.
        await sync_technical_addresses(session, prefix)
    if moving_vrf:
        # Addresses carry their own vrf_id (UNIQUE(vrf_id, address)) — cascade.
        for addr in (
            await session.execute(
                select(IPAddress).where(IPAddress.prefix_id == prefix.id)
            )
        ).scalars():
            addr.vrf_id = new_vrf
    try:
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        if "uq_ip_addresses_vrf_address" in str(e):
            raise HTTPException(409, "an address already exists in the target VRF")
        if "excl_prefixes_no_overlap" in str(e):
            raise HTTPException(409, f"{net} overlaps an existing prefix in the target VRF")
        raise HTTPException(400, "invalid prefix data")
    await session.refresh(prefix)
    return await _with_stats(session, prefix)


@router.delete(
    "/{prefix_id}",
    status_code=204,
    dependencies=[Depends(require_perm(DATA_DELETE))],
)
async def delete_prefix(prefix_id: int, session: AsyncSession = Depends(get_session)):
    try:
        prefix = await get_or_404(session, Prefix, prefix_id)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))
    await session.delete(prefix)
    await session.commit()


@router.get("/{prefix_id}/addresses", response_model=IPAddressPage)
async def prefix_addresses(
    prefix_id: int,
    session: AsyncSession = Depends(get_session),
    limit: int = Query(default=5000, le=20000),
    offset: int = 0,
):
    try:
        prefix = await get_or_404(session, Prefix, prefix_id)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))
    rows = (
        await session.execute(
            select(IPAddress)
            .where(IPAddress.prefix_id == prefix_id)
            .order_by(IPAddress.address_int)
            .limit(limit)
            .offset(offset)
        )
    ).scalars().all()
    await stamp_colors(session, "addresses", rows)
    await stamp_range_roles(session, rows)
    net = prefix_math.to_network(prefix.prefix)
    first, last = (None, None)
    if prefix_math.reserves_boundaries(net):
        first, last = str(net.network_address), str(net.broadcast_address)
    return IPAddressPage(
        items=[IPAddressOut.model_validate(r) for r in rows],
        total=net.num_addresses,
        prefix=str(net),
        usable_first=first,
        usable_last=last,
    )


@router.post(
    "/{prefix_id}/available-ips",
    response_model=AvailableIPOut,
    status_code=201,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def allocate_next_available(
    prefix_id: int,
    body: AllocateIPRequest | None = None,
    session: AsyncSession = Depends(get_session),
):
    """Atomically reserve the lowest free IP in the prefix."""
    body = body or AllocateIPRequest()
    try:
        row = await reserve_next_available(
            session,
            prefix_id,
            status=body.status,
            hostname=body.hostname,
            mac_address=body.mac_address,
            notes=body.notes,
        )
        await session.commit()
    except IPAMError as e:
        await session.rollback()
        raise HTTPException(e.status_code, str(e))
    return AvailableIPOut(
        id=row.id,
        address=str(row.address).split("/")[0],
        status=row.status.value,
        prefix_id=row.prefix_id,
        vrf_id=row.vrf_id,
    )


@router.get("/{prefix_id}/split", response_model=PrefixSplitOut)
async def split_prefix(
    prefix_id: int,
    mask: int = Query(..., description="new prefix length, e.g. 25"),
    session: AsyncSession = Depends(get_session),
):
    try:
        prefix = await get_or_404(session, Prefix, prefix_id)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))
    net = prefix_math.to_network(prefix.prefix)
    if net.prefixlen < mask <= net.max_prefixlen:
        # Reject before materializing: children() builds a real list, so a
        # /8 -> /32 request would allocate 16.7M network objects.
        cap = get_settings().ipambox_max_split_children
        count = 1 << (mask - net.prefixlen)
        if count > cap:
            raise HTTPException(
                422,
                f"split into /{mask} would produce {count} children — "
                f"max {cap} per request (IPAMBOX_MAX_SPLIT_CHILDREN)",
            )
    try:
        kids = prefix_math.children(net, mask)
    except ValueError as e:
        raise HTTPException(422, str(e))
    siblings = (
        await session.execute(select(Prefix).where(Prefix.vrf_id == prefix.vrf_id))
    ).scalars().all()
    existing_nets = {str(prefix_math.to_network(s.prefix)) for s in siblings}
    return PrefixSplitOut(
        mask=mask,
        children=[str(k) for k in kids],
        existing=[str(k) for k in kids if str(k) in existing_nets],
    )
