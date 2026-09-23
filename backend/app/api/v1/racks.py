"""Rack elevations: racks + nested devices + Rackula import.

Not a `_crud_router` — device collision validation, resolved asset/ip
summaries on the detail response, and the transactional import endpoint
don't fit the factory.
"""
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.deps import DATA_DELETE, DATA_READ, DATA_WRITE, require_perm
from app.models.asset import Asset
from app.models.ip_address import IPAddress
from app.models.rack import Rack, RackDevice, RackFace
from app.schemas.common import Page, ReorderBody, ip_display
from app.schemas.rack import (
    IpRef,
    LinkedRef,
    NextFreeUOut,
    RackCreate,
    RackDetail,
    RackDeviceCreate,
    RackDeviceImport,
    RackDeviceOut,
    RackDeviceUpdate,
    RackImportResult,
    RackOut,
    RackUpdate,
    SkippedDevice,
)
from app.services.colors import stamp_colors
from app.services.ipam import IPAMError, get_or_404
from app.services.ordering import ordered, reorder
from app.services.racks import check_placement, find_free_u, used_u
from app.services.workbook.normalize import fold_hebrew

router = APIRouter(prefix="/racks", tags=["racks"])


async def _devices(session: AsyncSession, rack_id: int) -> list[RackDevice]:
    return list(
        (
            await session.execute(
                select(RackDevice)
                .where(RackDevice.rack_id == rack_id)
                .order_by(RackDevice.u_position, RackDevice.id)
            )
        ).scalars().all()
    )


async def _stamp_usage(session: AsyncSession, racks: list[Rack]) -> None:
    """Populate device_count/used_u on Rack rows (transient, not columns).

    Explicit queries over `rack.devices` — a reused session can hold a stale
    collection (deleted members linger until refresh with expire_on_commit
    off), and tests share one session across requests.
    """
    ids = [r.id for r in racks]
    by_rack: dict[int, list[RackDevice]] = {i: [] for i in ids}
    if ids:
        for d in (
            await session.execute(
                select(RackDevice).where(RackDevice.rack_id.in_(ids))
            )
        ).scalars().all():
            by_rack[d.rack_id].append(d)
    for r in racks:
        devs = by_rack[r.id]
        r.device_count = len(devs)
        r.used_u = used_u(devs)


def _device_out(d: RackDevice) -> RackDeviceOut:
    out = RackDeviceOut.model_validate(d)
    if d.asset is not None:
        a = d.asset
        label = " ".join(p for p in (a.vendor, a.model) if p) or a.serial_number or f"asset#{a.id}"
        out.asset = LinkedRef(id=a.id, label=label)
    if d.ip_address is not None:
        ip = d.ip_address
        label = ip_display(ip.address) or ""
        if ip.hostname:
            label = f"{label} ({ip.hostname})"
        out.ip = IpRef(id=ip.id, label=label, prefix_id=ip.prefix_id)
        out.ip_status = ip.status
        out.ip_last_seen = ip.last_seen
    return out


async def _check_refs(session: AsyncSession, body: RackDeviceCreate | RackDeviceUpdate) -> None:
    try:
        if body.asset_id is not None:
            await get_or_404(session, Asset, body.asset_id)
        if body.ip_address_id is not None:
            await get_or_404(session, IPAddress, body.ip_address_id)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))


@router.get("", response_model=Page[RackOut])
async def list_racks(
    q: str = "",
    site_id: int | None = None,
    limit: int | None = Query(default=None, ge=1, le=20000),
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
):
    stmt = select(Rack)
    if site_id is not None:
        stmt = stmt.where(Rack.site_id == site_id)
    if q:
        like = f"%{fold_hebrew(q)}%"
        stmt = stmt.where(
            or_(
                func.translate(Rack.name, "םןץףך", "מנצפכ").ilike(like),
                func.translate(Rack.room, "םןץףך", "מנצפכ").ilike(like),
            )
        )
    stmt = ordered(stmt, Rack, Rack.name, Rack.id)
    total = await session.scalar(
        select(func.count()).select_from(stmt.order_by(None).subquery())
    )
    rows = (await session.execute(stmt.limit(limit).offset(offset))).scalars().all()
    await _stamp_usage(session, rows)
    return Page(
        items=await stamp_colors(session, "racks", rows),
        total=total or 0,
        limit=limit,
        offset=offset,
    )


@router.post(
    "",
    response_model=RackOut,
    status_code=201,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def create_rack(body: RackCreate, session: AsyncSession = Depends(get_session)):
    rack = Rack(**body.model_dump())
    session.add(rack)
    try:
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(409, "duplicate or invalid value") from e
    await session.refresh(rack)
    rack.device_count = 0
    rack.used_u = 0
    await stamp_colors(session, "racks", [rack])
    return rack


# Declared before /{rack_id} so the literal path can't be shadowed.
@router.post(
    "/reorder",
    status_code=204,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def reorder_racks(body: ReorderBody, session: AsyncSession = Depends(get_session)):
    try:
        await reorder(session, Rack, body.ids)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))


async def _get_rack(session: AsyncSession, rack_id: int) -> Rack:
    try:
        return await get_or_404(session, Rack, rack_id)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))


@router.get("/{rack_id}", response_model=RackDetail)
async def get_rack(rack_id: int, session: AsyncSession = Depends(get_session)):
    rack = await _get_rack(session, rack_id)
    devices = await _devices(session, rack.id)
    rack.device_count = len(devices)
    rack.used_u = used_u(devices)
    await stamp_colors(session, "racks", [rack])
    out = RackDetail.model_validate(rack)
    out.devices = [_device_out(d) for d in devices]
    return out


@router.get(
    "/{rack_id}/next-free-u",
    response_model=NextFreeUOut,
    dependencies=[Depends(require_perm(DATA_READ))],
)
async def next_free_u(
    rack_id: int,
    height: int = Query(ge=1),
    face: RackFace = RackFace.FRONT,
    side: Literal["bottom", "top"] = "bottom",
    session: AsyncSession = Depends(get_session),
):
    """Lowest (side=bottom) or highest (side=top) start U where a `height`-U
    `face` device fits — the read-only analog of next-available-IP."""
    rack = await _get_rack(session, rack_id)
    try:
        u = find_free_u(rack, await _devices(session, rack.id), height, face, side)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))
    return NextFreeUOut(u_position=u)


@router.patch(
    "/{rack_id}",
    response_model=RackOut,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def update_rack(
    rack_id: int, body: RackUpdate, session: AsyncSession = Depends(get_session)
):
    rack = await _get_rack(session, rack_id)
    patch = body.model_dump(exclude_unset=True)
    if "height_u" in patch:
        over = [
            d
            for d in await _devices(session, rack.id)
            if d.u_position + d.u_height - 1 > patch["height_u"]
        ]
        if over:
            names = ", ".join(d.name or f"#{d.id}" for d in over[:5])
            raise HTTPException(
                422, f"height {patch['height_u']}U strands devices: {names}"
            )
    for field, value in patch.items():
        setattr(rack, field, value)
    try:
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(409, "duplicate or invalid value") from e
    await session.refresh(rack)
    await _stamp_usage(session, [rack])
    await stamp_colors(session, "racks", [rack])
    return rack


@router.delete(
    "/{rack_id}",
    status_code=204,
    dependencies=[Depends(require_perm(DATA_DELETE))],
)
async def delete_rack(rack_id: int, session: AsyncSession = Depends(get_session)):
    rack = await _get_rack(session, rack_id)
    await session.delete(rack)
    await session.commit()


async def _get_device(
    session: AsyncSession, rack_id: int, device_id: int
) -> tuple[Rack, RackDevice]:
    rack = await _get_rack(session, rack_id)
    device = await session.get(RackDevice, device_id)
    if device is None or device.rack_id != rack_id:
        raise HTTPException(404, f"RackDevice {device_id} not found")
    return rack, device


@router.post(
    "/{rack_id}/devices",
    response_model=RackDeviceOut,
    status_code=201,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def create_device(
    rack_id: int, body: RackDeviceCreate, session: AsyncSession = Depends(get_session)
):
    rack = await _get_rack(session, rack_id)
    await _check_refs(session, body)
    device = RackDevice(rack_id=rack.id, **body.model_dump())
    try:
        check_placement(rack, await _devices(session, rack.id), device)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))
    session.add(device)
    try:
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(409, "duplicate or invalid value") from e
    await session.refresh(device, ["created_at", "updated_at", "asset", "ip_address"])
    return _device_out(device)


@router.patch(
    "/{rack_id}/devices/{device_id}",
    response_model=RackDeviceOut,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def update_device(
    rack_id: int,
    device_id: int,
    body: RackDeviceUpdate,
    session: AsyncSession = Depends(get_session),
):
    rack, device = await _get_device(session, rack_id, device_id)
    await _check_refs(session, body)
    patch = body.model_dump(exclude_unset=True)
    candidate = RackDevice(rack_id=rack_id, **{**_device_fields(device), **patch})
    try:
        check_placement(
            rack, await _devices(session, rack.id), candidate, exclude_id=device.id
        )
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))
    for field, value in patch.items():
        setattr(device, field, value)
    try:
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(409, "duplicate or invalid value") from e
    await session.refresh(device)
    return _device_out(device)


def _device_fields(d: RackDevice) -> dict:
    return {
        f: getattr(d, f)
        for f in (
            "name", "device_type", "u_position", "u_height", "face", "colour",
            "category", "manufacturer", "model", "asset_id", "ip_address_id",
            "source", "notes",
        )
    }


@router.delete(
    "/{rack_id}/devices/{device_id}",
    status_code=204,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def delete_device(
    rack_id: int, device_id: int, session: AsyncSession = Depends(get_session)
):
    _, device = await _get_device(session, rack_id, device_id)
    await session.delete(device)
    await session.commit()


@router.post(
    "/{rack_id}/devices/import",
    response_model=RackImportResult,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def import_devices(
    rack_id: int, body: RackDeviceImport, session: AsyncSession = Depends(get_session)
):
    """Bulk-load parsed Rackula devices in one transaction.

    `replace` wipes existing rows first; `merge` keeps them and skips
    incoming rows that collide or fall outside the rack.
    """
    rack = await _get_rack(session, rack_id)
    placed = await _devices(session, rack.id)
    if body.mode == "replace":
        # ORM deletes so the wipe is audited per device (changelog hooks).
        for d in placed:
            await session.delete(d)
        await session.flush()
        placed = []
    created = 0
    skipped: list[SkippedDevice] = []
    try:
        for d in body.devices:
            # this endpoint exists for Rackula round-trips — provenance is
            # fixed here rather than trusting the payload's source field.
            device = RackDevice(
                rack_id=rack.id, **{**d.model_dump(), "source": "rackula"}
            )
            try:
                check_placement(rack, placed, device)
            except IPAMError as e:
                skipped.append(
                    SkippedDevice(name=d.name, u_position=d.u_position, reason=str(e))
                )
                continue
            session.add(device)
            placed.append(device)
            created += 1
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(409, "duplicate or invalid value") from e
    return RackImportResult(created=created, skipped=skipped)
