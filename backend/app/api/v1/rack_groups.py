"""Rack groups — bayed rows: ordered sets of racks rendered side by side.

Not a `_crud_router` — the detail response carries the member racks (with
devices + occupancy/capacity aggregates, ordered by group_position) for the
row view, which the factory can't produce.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.racks import _device_out
from app.core.db import get_session
from app.core.deps import DATA_DELETE, DATA_WRITE, require_perm
from app.models.rack import Rack, RackGroup
from app.models.site import Site
from app.services.cabling import interface_stats
from app.services.devices import ips_by_device
from app.schemas.common import ReorderBody
from app.schemas.rack import (
    RackDetail,
    RackGroupCreate,
    RackGroupDetail,
    RackGroupOut,
    RackGroupUpdate,
    RackOut,
)
from app.services.colors import stamp_colors
from app.services.ipam import IPAMError, get_or_404
from app.services.ordering import ordered, reorder
from app.services.rack_io import bundle_sheets, workbook_response
from app.services.racks import stamp_rack_stats

router = APIRouter(prefix="/rack-groups", tags=["rack-groups"])


async def _get_group(session: AsyncSession, group_id: int) -> RackGroup:
    try:
        return await get_or_404(session, RackGroup, group_id)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))


async def _check_site(session: AsyncSession, site_id: int | None) -> None:
    if site_id is None:
        return
    try:
        await get_or_404(session, Site, site_id)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))


def _ordered_racks(stmt):
    """group_position order; unpositioned racks park at the row's end."""
    return stmt.order_by(
        Rack.group_position.asc().nulls_last(), Rack.name, Rack.id
    )


async def _rack_detail(session: AsyncSession, rack: Rack) -> RackDetail:
    """Rack -> RackDetail with its (selectin-loaded) devices serialized,
    each carrying the device-wide IP health rollup."""
    # Scalar fields only — devices are stamped below; validating the ORM
    # relationship would feed Device.asset/ip into LinkedRef and crash.
    out = RackDetail(**RackOut.model_validate(rack).model_dump())
    ips = await ips_by_device(session, [d.id for d in rack.devices])
    istats = await interface_stats(session, [d.id for d in rack.devices])
    out.devices = [
        await _device_out(session, d, ips.get(d.id, []), istats)
        for d in rack.devices
    ]
    return out


@router.get("", response_model=list[RackGroupOut])
async def list_rack_groups(
    site_id: int | None = None,
    session: AsyncSession = Depends(get_session),
):
    stmt = (
        select(RackGroup, func.count(Rack.id).label("rack_count"))
        .outerjoin(Rack, Rack.group_id == RackGroup.id)
        .group_by(RackGroup.id)
    )
    if site_id is not None:
        stmt = stmt.where(RackGroup.site_id == site_id)
    stmt = ordered(stmt, RackGroup, RackGroup.name, RackGroup.id)
    out = []
    for group, count in (await session.execute(stmt)).all():
        group.rack_count = count
        out.append(group)
    return await stamp_colors(session, "rack_groups", out)


@router.post(
    "",
    response_model=RackGroupOut,
    status_code=201,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def create_rack_group(
    body: RackGroupCreate, session: AsyncSession = Depends(get_session)
):
    await _check_site(session, body.site_id)
    g = RackGroup(**body.model_dump())
    session.add(g)
    try:
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(409, "duplicate or invalid value") from e
    await session.refresh(g)
    await stamp_colors(session, "rack_groups", [g])
    return g


# Declared before /{group_id} so the literal path can't be shadowed.
@router.post(
    "/reorder",
    status_code=204,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def reorder_rack_groups(
    body: ReorderBody, session: AsyncSession = Depends(get_session)
):
    try:
        await reorder(session, RackGroup, body.ids)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))


@router.get("/{group_id}/export.xlsx")
async def export_rack_group_xlsx(
    group_id: int, session: AsyncSession = Depends(get_session)
):
    """The group file: group row + member racks in group_position order +
    every device (+ wiring). Re-imports as the same tree."""
    g = await _get_group(session, group_id)
    racks = list(
        (
            await session.execute(
                _ordered_racks(select(Rack).where(Rack.group_id == g.id))
            )
        ).scalars()
    )
    # the bundle's groups sheet holds exactly the groups these racks
    # reference — for a group file that's this one.
    return workbook_response(
        f"{g.name}.xlsx", await bundle_sheets(session, racks)
    )


@router.get("/{group_id}", response_model=RackGroupDetail)
async def get_rack_group(
    group_id: int, session: AsyncSession = Depends(get_session)
):
    """Group + member racks (group_position order) with devices and the
    per-rack occupancy/capacity aggregates — the row view's payload."""
    g = await _get_group(session, group_id)
    racks = (
        await session.execute(
            _ordered_racks(select(Rack).where(Rack.group_id == g.id))
        )
    ).scalars().all()
    await stamp_rack_stats(session, racks)
    await stamp_colors(session, "rack_groups", [g])
    g.rack_count = len(racks)
    out = RackGroupDetail(**RackGroupOut.model_validate(g).model_dump())
    out.racks = [await _rack_detail(session, r) for r in racks]
    return out


@router.patch(
    "/{group_id}",
    response_model=RackGroupOut,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def update_rack_group(
    group_id: int,
    body: RackGroupUpdate,
    session: AsyncSession = Depends(get_session),
):
    g = await _get_group(session, group_id)
    patch = body.model_dump(exclude_unset=True)
    await _check_site(session, patch.get("site_id"))
    for field, value in patch.items():
        setattr(g, field, value)
    try:
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(409, "duplicate or invalid value") from e
    await session.refresh(g)
    g.rack_count = await session.scalar(
        select(func.count(Rack.id)).where(Rack.group_id == g.id)
    )
    await stamp_colors(session, "rack_groups", [g])
    return g


@router.delete(
    "/{group_id}",
    status_code=204,
    dependencies=[Depends(require_perm(DATA_DELETE))],
)
async def delete_rack_group(
    group_id: int, session: AsyncSession = Depends(get_session)
):
    """Deleting a group never deletes racks — membership clears via SET NULL."""
    g = await _get_group(session, group_id)
    await session.delete(g)
    await session.commit()
