import ipaddress

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

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
from app.services.csv_export import csv_response
from app.services.ipam import (
    IPAMError,
    build_tree,
    check_overlap,
    get_or_404,
    prefix_stats,
    reserve_next_available,
)

router = APIRouter(prefix="/prefixes", tags=["prefixes"])


async def _with_stats(session: AsyncSession, p: Prefix) -> PrefixOut:
    return PrefixOut.model_validate(p).model_copy(update=await prefix_stats(session, p))


@router.get("/tree")
async def prefix_tree(session: AsyncSession = Depends(get_session)):
    """Site -> VRF -> nested prefix containment hierarchy."""
    return await build_tree(session)


@router.get("/export.csv")
async def export_prefixes(session: AsyncSession = Depends(get_session)):
    rows = (
        await session.execute(
            select(Prefix).options(selectinload(Prefix.vlan), selectinload(Prefix.vrf))
        )
    ).scalars().all()
    return csv_response(
        "prefixes.csv",
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
    session: AsyncSession = Depends(get_session),
):
    q_stmt = select(Prefix).options(selectinload(Prefix.vlan)).order_by(Prefix.prefix)
    if vrf_id is not None:
        q_stmt = q_stmt.where(Prefix.vrf_id == vrf_id)
    if site_id is not None:
        q_stmt = q_stmt.where(Prefix.site_id == site_id)
    if status is not None:
        q_stmt = q_stmt.where(Prefix.status == status)
    if tag_id is not None:
        q_stmt = q_stmt.where(
            Prefix.id.in_(
                select(TagAssignment.object_id).where(
                    TagAssignment.object_type == "Prefix",
                    TagAssignment.tag_id == tag_id,
                )
            )
        )
    rows = (await session.execute(q_stmt)).scalars().all()
    if q:
        rows = [p for p in rows if q.lower() in str(p.prefix)]
    # order by network address integer for a natural hierarchy view
    rows.sort(key=lambda p: int(prefix_math.to_network(p.prefix).network_address))
    return [await _with_stats(session, p) for p in rows]


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
