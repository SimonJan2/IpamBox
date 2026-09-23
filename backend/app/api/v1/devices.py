"""Devices — first-class hosts: unracked inventory plus rack placement.

Not a `_crud_router` — placement changes run through services.racks
(apply_device_patch, shared with the rack route), and the detail response
carries the device's IPs + asset + rack context.

Semantics: rack_id NULL = unracked inventory. PATCH rack_id=X places /
re-homes (validated), PATCH rack_id=null unracks, DELETE removes the row
for real (IPs unlink via SET NULL, carrier children unmount).
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.deps import DATA_DELETE, DATA_WRITE, require_perm
from app.models.asset import Asset
from app.models.device import Device
from app.models.rack import Rack, RackFace
from app.models.site import Site
from app.schemas.common import Page, ReorderBody, ip_display
from app.schemas.device import (
    DeviceCreate,
    DeviceDetail,
    DeviceIpRef,
    DeviceOut,
    DeviceUpdate,
)
from app.schemas.rack import LinkedRef
from app.services.colors import stamp_colors
from app.services.devices import device_health, ips_by_device
from app.services.ipam import IPAMError, get_or_404
from app.services.ordering import ordered, reorder
from app.services.racks import (
    apply_device_patch,
    carrier_children,
    check_placement,
    rack_devices,
)
from app.services.workbook.normalize import fold_hebrew

router = APIRouter(prefix="/devices", tags=["devices"])


async def _get_device(session: AsyncSession, device_id: int) -> Device:
    try:
        return await get_or_404(session, Device, device_id)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))


async def _check_refs(session: AsyncSession, data: dict) -> None:
    """Existence checks for the linkable FKs on create/patch payloads."""
    try:
        if data.get("site_id") is not None:
            await get_or_404(session, Site, data["site_id"])
        if data.get("asset_id") is not None:
            await get_or_404(session, Asset, data["asset_id"])
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))


def _asset_ref(asset: Asset | None) -> LinkedRef | None:
    if asset is None:
        return None
    label = (
        " ".join(p for p in (asset.vendor, asset.model) if p)
        or asset.serial_number
        or f"asset#{asset.id}"
    )
    return LinkedRef(id=asset.id, label=label)


async def _detail(session: AsyncSession, device: Device) -> DeviceDetail:
    """Device -> DeviceDetail: IPs, asset, site/rack/carrier context,
    health rollup — the /devices/{id} payload."""
    # Scalar columns via DeviceOut first — model_validate(device) directly
    # would try to read ips/asset/site/rack/carrier relationships into the
    # LinkedRef/IpRef fields and crash on linked rows.
    out = DeviceDetail(**DeviceOut.model_validate(device).model_dump())
    ips = (await ips_by_device(session, [device.id]))[device.id]
    out.ip_count = len(ips)
    out.health = device_health(ips)
    out.ips = [
        DeviceIpRef(
            id=i.id,
            label=(ip_display(i.address) or "")
            + (f" ({i.hostname})" if i.hostname else ""),
            address=ip_display(i.address) or "",
            hostname=i.hostname,
            status=i.status,
            last_seen=i.last_seen,
            prefix_id=i.prefix_id,
        )
        for i in ips
    ]
    # FK refs resolved via session.get, not the relationships — identity-map
    # hits (device created in this same session) skip selectin loaders and
    # a lazy load here would raise MissingGreenlet.
    if device.asset_id is not None:
        out.asset = _asset_ref(await session.get(Asset, device.asset_id))
    if device.site_id is not None:
        site = await session.get(Site, device.site_id)
        if site is not None:
            out.site = LinkedRef(id=site.id, label=site.name)
    if device.rack_id is not None:
        rack = await session.get(Rack, device.rack_id)
        if rack is not None:
            out.rack = LinkedRef(id=rack.id, label=rack.name)
    if device.carrier_id is not None:
        carrier = await session.get(Device, device.carrier_id)
        if carrier is not None:
            out.carrier = LinkedRef(id=carrier.id, label=carrier.name)
    return out


@router.get("", response_model=Page[DeviceOut])
async def list_devices(
    q: str = "",
    rack_id: int | None = None,
    site_id: int | None = None,
    unracked: bool = False,
    limit: int | None = Query(default=None, ge=1, le=20000),
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
):
    stmt = select(Device)
    if rack_id is not None:
        stmt = stmt.where(Device.rack_id == rack_id)
    if site_id is not None:
        stmt = stmt.where(Device.site_id == site_id)
    if unracked:
        stmt = stmt.where(Device.rack_id.is_(None))
    if q:
        like = f"%{fold_hebrew(q)}%"
        stmt = stmt.where(
            or_(
                func.translate(Device.name, "םןץףך", "מנצפכ").ilike(like),
                func.translate(Device.model, "םןץףך", "מנצפכ").ilike(like),
                func.translate(Device.serial_number, "םןץףך", "מנצפכ").ilike(like),
            )
        )
    stmt = ordered(stmt, Device, Device.name, Device.id)
    total = await session.scalar(
        select(func.count()).select_from(stmt.order_by(None).subquery())
    )
    rows = (await session.execute(stmt.limit(limit).offset(offset))).scalars().all()
    await stamp_colors(session, "devices", rows)
    # Health + counts in one grouped IP query — never per-row.
    ips = await ips_by_device(session, [d.id for d in rows])
    items = []
    for d in rows:
        out = DeviceOut.model_validate(d)
        out.health = device_health(ips[d.id])
        out.ip_count = len(ips[d.id])
        items.append(out)
    return Page(items=items, total=total or 0, limit=limit, offset=offset)


@router.post(
    "",
    response_model=DeviceDetail,
    status_code=201,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def create_device(
    body: DeviceCreate, session: AsyncSession = Depends(get_session)
):
    """Create a device — unracked inventory by default, or placed directly
    when rack_id (or carrier_id) is supplied."""
    data = body.model_dump()
    await _check_refs(session, data)
    carrier_row = None
    if data.get("carrier_id") is not None:
        carrier_row = await session.get(Device, data["carrier_id"])
        if carrier_row is None or carrier_row.rack_id is None:
            raise HTTPException(422, f"carrier {data['carrier_id']} is not racked")
        data["rack_id"] = carrier_row.rack_id
        data["u_position"] = carrier_row.u_position
        data["face"] = carrier_row.face
    if data.get("rack_id") is not None:
        try:
            rack = await get_or_404(session, Rack, data["rack_id"])
        except IPAMError as e:
            raise HTTPException(e.status_code, str(e))
        if data["u_position"] is None and data["carrier_id"] is None:
            raise HTTPException(
                422,
                "u_position is required unless the device mounts into a carrier",
            )
        data["u_height"] = data["u_height"] or 1
        data["face"] = data["face"] or RackFace.FRONT
        device = Device(**data)
        try:
            check_placement(
                rack, await rack_devices(session, rack.id), device
            )
        except IPAMError as e:
            raise HTTPException(e.status_code, str(e))
    else:
        if data.get("u_position") is not None or data.get("slot") is not None:
            raise HTTPException(422, "set rack_id to place the device")
        device = Device(**data)
    session.add(device)
    try:
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(409, "duplicate or invalid value") from e
    await session.refresh(device)
    return await _detail(session, device)


# Declared before /{device_id} so the literal path can't be shadowed.
@router.post(
    "/reorder",
    status_code=204,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def reorder_devices(
    body: ReorderBody, session: AsyncSession = Depends(get_session)
):
    try:
        await reorder(session, Device, body.ids)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))


@router.get("/{device_id}", response_model=DeviceDetail)
async def get_device(device_id: int, session: AsyncSession = Depends(get_session)):
    device = await _get_device(session, device_id)
    await stamp_colors(session, "devices", [device])
    return await _detail(session, device)


@router.patch(
    "/{device_id}",
    response_model=DeviceDetail,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def update_device(
    device_id: int, body: DeviceUpdate, session: AsyncSession = Depends(get_session)
):
    device = await _get_device(session, device_id)
    patch = body.model_dump(exclude_unset=True)
    await _check_refs(session, patch)
    try:
        await apply_device_patch(session, device, patch)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))
    try:
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(409, "duplicate or invalid value") from e
    await session.refresh(device)
    return await _detail(session, device)


@router.delete(
    "/{device_id}",
    status_code=204,
    dependencies=[Depends(require_perm(DATA_DELETE))],
)
async def delete_device(
    device_id: int, session: AsyncSession = Depends(get_session)
):
    """The real delete: IPs unlink (SET NULL), carrier children unmount."""
    device = await _get_device(session, device_id)
    for child in await carrier_children(session, device.id):
        child.carrier_id = None
        child.slot = None
    await session.delete(device)
    await session.commit()
