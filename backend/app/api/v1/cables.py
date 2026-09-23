"""Cables + top-level interface routes (V4A).

Device-scoped interface CRUD/generate lives under /devices/{id}/interfaces
(devices.py); this module owns /cables (list/create/patch/delete + the L1
trace) and /interfaces/{id} + the legacy free-text matcher.

Cable uniqueness: an interface terminates at most one cable — validated
across both end columns at the app layer (409 carrying the existing cable
id), with the per-column UNIQUE constraints as the race-condition backstop.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.deps import DATA_DELETE, DATA_WRITE, require_perm
from app.models.cabling import Cable, DeviceInterface
from app.models.device import Device
from app.models.rack import Rack
from app.schemas.cabling import (
    CableCreate,
    CableOut,
    CableTraceHop,
    CableUpdate,
    DeviceInterfaceOut,
    MatchFreeTextOut,
)
from app.schemas.common import Page
from app.services.cabling import (
    cable_ends_for,
    cable_for,
    match_free_text,
    peers_for,
    stamp_connected_ips,
    trace_path,
)
from app.services.ipam import IPAMError, get_or_404

router = APIRouter(prefix="/cables", tags=["cables"])
interfaces_router = APIRouter(prefix="/interfaces", tags=["interfaces"])


async def _get_interface(
    session: AsyncSession, interface_id: int
) -> DeviceInterface:
    try:
        return await get_or_404(session, DeviceInterface, interface_id)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))


async def _get_cable(session: AsyncSession, cable_id: int) -> Cable:
    try:
        return await get_or_404(session, Cable, cable_id)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))


async def _cable_out(session: AsyncSession, cable: Cable) -> CableOut:
    out = CableOut.model_validate(cable)
    a, b = (await cable_ends_for(session, [cable])).get(cable.id, (None, None))
    out.a, out.b = a, b
    return out


async def _check_ends(
    session: AsyncSession,
    a_id: int,
    b_id: int,
    ignore_cable_id: int | None = None,
) -> None:
    """Shared create/patch validation: ends exist, differ, and are free."""
    if a_id == b_id:
        raise HTTPException(422, "a and b must be different interfaces")
    for iface_id in (a_id, b_id):
        iface = await _get_interface(session, iface_id)
        existing = await cable_for(session, iface_id)
        if existing is not None and existing.id != ignore_cable_id:
            raise HTTPException(
                409,
                f"interface '{iface.name}' (id {iface.id}) already has a "
                f"cable (existing cable {existing.id})",
            )


@router.get("", response_model=Page[CableOut])
async def list_cables(
    device_id: int | None = None,
    site_id: int | None = None,
    q: str = "",
    limit: int | None = Query(default=None, ge=1, le=20000),
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
):
    stmt = select(Cable)
    if device_id is not None or site_id is not None:
        dev_ids = select(Device.id).outerjoin(
            Rack, Device.rack_id == Rack.id
        )
        if device_id is not None:
            dev_ids = dev_ids.where(Device.id == device_id)
        if site_id is not None:
            # Effective site: an explicit device site_id wins; a racked
            # device otherwise inherits its rack's site.
            dev_ids = dev_ids.where(
                func.coalesce(Device.site_id, Rack.site_id) == site_id
            )
        iface_ids = select(DeviceInterface.id).where(
            DeviceInterface.device_id.in_(dev_ids)
        )
        stmt = stmt.where(
            or_(
                Cable.a_interface_id.in_(iface_ids),
                Cable.b_interface_id.in_(iface_ids),
            )
        )
    if q:
        stmt = stmt.where(
            or_(
                Cable.label.ilike(f"%{q}%"),
                Cable.color.ilike(f"%{q}%"),
                Cable.notes.ilike(f"%{q}%"),
            )
        )
    stmt = stmt.order_by(Cable.id)
    total = await session.scalar(
        select(func.count()).select_from(stmt.order_by(None).subquery())
    )
    rows = (await session.execute(stmt.limit(limit).offset(offset))).scalars().all()
    ends = await cable_ends_for(session, list(rows))
    items = []
    for c in rows:
        out = CableOut.model_validate(c)
        out.a, out.b = ends.get(c.id, (None, None))
        items.append(out)
    return Page(items=items, total=total or 0, limit=limit, offset=offset)


@router.post(
    "",
    response_model=CableOut,
    status_code=201,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def create_cable(
    body: CableCreate, session: AsyncSession = Depends(get_session)
):
    await _check_ends(session, body.a_interface_id, body.b_interface_id)
    cable = Cable(**body.model_dump())
    session.add(cable)
    try:
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(409, "an end of this cable is already cabled") from e
    await session.refresh(cable)
    return await _cable_out(session, cable)


# Declared before /{cable_id} so the literal path can't be shadowed.
@router.get("/trace", response_model=list[CableTraceHop])
async def trace(
    interface_id: int = Query(...), session: AsyncSession = Depends(get_session)
):
    """Walk the documented L1 path from an interface: cable → peer → (patch
    port → its same-device pair) → repeat. Both directions from the start
    so mid-chain starts still surface the full path; bounded at 10 hops."""
    iface = await _get_interface(session, interface_id)
    return await trace_path(session, iface)


@router.patch(
    "/{cable_id}",
    response_model=CableOut,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def update_cable(
    cable_id: int, body: CableUpdate, session: AsyncSession = Depends(get_session)
):
    cable = await _get_cable(session, cable_id)
    patch = body.model_dump(exclude_unset=True)
    if "a_interface_id" in patch or "b_interface_id" in patch:
        await _check_ends(
            session,
            patch.get("a_interface_id") or cable.a_interface_id,
            patch.get("b_interface_id") or cable.b_interface_id,
            ignore_cable_id=cable.id,
        )
    for field, value in patch.items():
        setattr(cable, field, value)
    try:
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(409, "an end of this cable is already cabled") from e
    await session.refresh(cable)
    return await _cable_out(session, cable)


@router.delete(
    "/{cable_id}",
    status_code=204,
    dependencies=[Depends(require_perm(DATA_DELETE))],
)
async def delete_cable(
    cable_id: int, session: AsyncSession = Depends(get_session)
):
    cable = await _get_cable(session, cable_id)
    await session.delete(cable)
    await session.commit()


# ---------------------------------------------------------------------------
# /interfaces — single-interface fetch + the free-text transition helper.
# Device-scoped interface CRUD/generate lives in api.v1.devices.
# ---------------------------------------------------------------------------


# Declared before /{interface_id} so the literal path can't be shadowed.
@interfaces_router.post(
    "/match-free-text",
    response_model=MatchFreeTextOut,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def interfaces_match_free_text(
    session: AsyncSession = Depends(get_session),
):
    """Transition helper: switch_name/switch_port → connected_interface_id.

    Exact-name matching only — a device whose name equals switch_name AND
    owns an interface named exactly switch_port. One candidate links, zero
    reports unmatched, several report ambiguous; the text columns are never
    touched. Runs stay reviewable: every link is a changelog update.
    """
    report = await match_free_text(session)
    await session.commit()
    return MatchFreeTextOut(
        matched=len(report["matched"]),
        ambiguous=len(report["ambiguous"]),
        unmatched=len(report["unmatched"]),
        matched_ids=report["matched"],
        ambiguous_ids=report["ambiguous"],
        unmatched_ids=report["unmatched"],
    )


@interfaces_router.get(
    "/{interface_id}", response_model=DeviceInterfaceOut
)
async def get_interface(
    interface_id: int, session: AsyncSession = Depends(get_session)
):
    iface = await _get_interface(session, interface_id)
    out = DeviceInterfaceOut.model_validate(iface)
    out.peer = (await peers_for(session, [iface])).get(iface.id)
    await stamp_connected_ips(session, [out])
    return out
