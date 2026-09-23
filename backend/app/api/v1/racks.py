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
from app.models.rack import Rack, RackDevice, RackFace, RackGroup
from app.schemas.common import Page, ReorderBody, ip_display
from app.schemas.rack import (
    IpRef,
    LinkedRef,
    NextFreeUOut,
    RackCreate,
    RackDetail,
    RackDeviceCreate,
    RackDeviceImport,
    RackDeviceImportItem,
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
from app.services.racks import (
    SLOT_LAYOUTS,
    CarrierError,
    check_placement,
    find_free_u,
    resolve_carrier,
    stamp_rack_stats,
)
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


async def _next_group_position(session: AsyncSession, group_id: int) -> int:
    """Append slot at the row's right end for a rack joining without an
    explicit group_position."""
    top = await session.scalar(
        select(func.coalesce(func.max(Rack.group_position), 0)).where(
            Rack.group_id == group_id
        )
    )
    return (top or 0) + 1


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


def _inherit_carrier(
    devices: list[RackDevice], fields: dict
) -> RackDevice | None:
    """When `carrier_id` is set, derive u_position/face from the carrier —
    a child's own values are display-only and never trusted off the wire.
    Returns the carrier row (check_placement re-validates it) or None."""
    carrier_id = fields.get("carrier_id")
    if carrier_id is None:
        return None
    carrier = resolve_carrier(devices, carrier_id)
    if carrier is not None:
        fields["u_position"] = carrier.u_position
        fields["face"] = carrier.face
    return carrier


@router.get("", response_model=Page[RackOut])
async def list_racks(
    q: str = "",
    site_id: int | None = None,
    group_id: int | None = None,
    limit: int | None = Query(default=None, ge=1, le=20000),
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
):
    stmt = select(Rack)
    if site_id is not None:
        stmt = stmt.where(Rack.site_id == site_id)
    if group_id is not None:
        stmt = stmt.where(Rack.group_id == group_id)
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
    await stamp_rack_stats(session, rows)
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
    data = body.model_dump()
    if data["group_id"] is not None:
        try:
            await get_or_404(session, RackGroup, data["group_id"])
        except IPAMError as e:
            raise HTTPException(e.status_code, str(e))
        if data["group_position"] is None:
            data["group_position"] = await _next_group_position(
                session, data["group_id"]
            )
    rack = Rack(**data)
    session.add(rack)
    try:
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(409, "duplicate or invalid value") from e
    await session.refresh(rack)
    await stamp_rack_stats(session, [rack])
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
    await stamp_rack_stats(session, [rack])
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
    # Group moves are plain patches — no special endpoint. Joining without an
    # explicit position appends at the row's right end; leaving the group
    # clears the (now meaningless) position unless one was sent along.
    if "group_id" in patch:
        gid = patch["group_id"]
        if gid is None:
            patch.setdefault("group_position", None)
        else:
            try:
                await get_or_404(session, RackGroup, gid)
            except IPAMError as e:
                raise HTTPException(e.status_code, str(e))
            if patch.get("group_position") is None:
                patch["group_position"] = await _next_group_position(
                    session, gid
                )
    for field, value in patch.items():
        setattr(rack, field, value)
    try:
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(409, "duplicate or invalid value") from e
    await session.refresh(rack)
    await stamp_rack_stats(session, [rack])
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
    devices = await _devices(session, rack.id)
    fields = body.model_dump()
    if fields["u_position"] is None and fields["carrier_id"] is None:
        raise HTTPException(
            422, "u_position is required unless the device mounts into a carrier"
        )
    _inherit_carrier(devices, fields)
    device = RackDevice(rack_id=rack.id, **fields)
    try:
        check_placement(rack, devices, device)
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
    if patch.get("rack_id") is None:
        patch.pop("rack_id", None)  # a device always belongs to a rack
    devices = await _devices(session, rack.id)

    # Cross-rack move: rack_id re-homes the device (a device leaving its rack
    # leaves its carrier behind too, unless the patch re-seats it onto a
    # carrier in the target rack). Placement validates against the target.
    target_rack = rack
    target_devices = devices
    if patch.get("rack_id") is not None and patch["rack_id"] != rack_id:
        try:
            target_rack = await get_or_404(session, Rack, patch["rack_id"])
        except IPAMError as e:
            raise HTTPException(e.status_code, str(e))
        target_devices = await _devices(session, target_rack.id)
        if "carrier_id" not in patch:
            patch["carrier_id"] = None

    # Unmounting (explicit carrier_id: null) clears the slot too, unless the
    # client re-seated it in the same patch.
    if patch.get("carrier_id", "unset") is None and "slot" not in patch:
        patch["slot"] = None
    merged = {**_device_fields(device), **patch}
    merged.pop("rack_id", None)  # carried by target_rack, not the candidate
    if merged["u_position"] is None and merged["carrier_id"] is None:
        raise HTTPException(
            422, "u_position is required unless the device mounts into a carrier"
        )
    carrier = _inherit_carrier(target_devices, merged)
    candidate = RackDevice(rack_id=target_rack.id, **merged)
    try:
        check_placement(
            target_rack, target_devices, candidate, exclude_id=device.id
        )
        _check_layout_change(devices, device, patch)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))
    for field, value in patch.items():
        setattr(device, field, value)
    if carrier is not None:
        # u_position/face weren't necessarily in the patch — apply the
        # carrier-derived values the candidate was validated with.
        device.u_position = carrier.u_position
        device.face = carrier.face
    moved_racks = device.rack_id != rack_id
    if device.slot_layout is not None and (
        "u_position" in patch or "face" in patch or moved_racks
    ):
        # Carrier moved — children mirror its span + face (and follow it
        # across racks: the tray physically carries them).
        for c in devices:
            if c.carrier_id == device.id:
                c.u_position = device.u_position
                c.face = device.face
                if moved_racks:
                    c.rack_id = device.rack_id
    try:
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(409, "duplicate or invalid value") from e
    await session.refresh(device)
    return _device_out(device)


def _check_layout_change(
    devices: list[RackDevice], device: RackDevice, patch: dict
) -> None:
    """A carrier's slot_layout can only shrink/clear when no mounted child
    sits in a slot the new layout doesn't have."""
    if "slot_layout" not in patch:
        return
    children = [d for d in devices if d.carrier_id == device.id]
    if not children:
        return
    new_layout = patch["slot_layout"]
    count = SLOT_LAYOUTS.get(new_layout or "")
    if count is None:
        raise CarrierError(
            f"{device.name} still has {len(children)} mounted device(s)"
        )
    over = [c for c in children if c.slot is not None and c.slot >= count]
    if over:
        names = ", ".join(c.name or f"#{c.id}" for c in over[:5])
        raise CarrierError(
            f"slot_layout={new_layout} strands mounted devices: {names}"
        )


def _device_fields(d: RackDevice) -> dict:
    return {
        f: getattr(d, f)
        for f in (
            "name", "device_type", "u_position", "u_height", "face", "colour",
            "category", "manufacturer", "model", "asset_id", "ip_address_id",
            "source", "carrier_id", "slot", "slot_layout", "notes",
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
    # Delete mounted children explicitly first — each gets audited; the
    # DB-level ON DELETE CASCADE on carrier_id is the backstop.
    for d in await _devices(session, rack_id):
        if d.carrier_id == device.id:
            await session.delete(d)
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
        # Children first — a carrier delete would DB-cascade them anyway.
        for d in sorted(placed, key=lambda x: x.carrier_id is None):
            await session.delete(d)
        await session.flush()
        placed = []
    created = 0
    skipped: list[SkippedDevice] = []
    # carrier_key -> the carrier row created from this payload (children
    # reference it before real ids exist).
    carriers: dict[str, RackDevice] = {}
    children: list[RackDeviceImportItem] = []
    try:
        for d in body.devices:
            if d.carrier_key and d.slot_layout is None:
                children.append(d)
                continue
            # this endpoint exists for Rackula round-trips — provenance is
            # fixed here rather than trusting the payload's source field.
            fields = d.model_dump(exclude={"carrier_key"})
            _inherit_carrier(placed, fields)
            if fields["u_position"] is None:
                skipped.append(
                    SkippedDevice(
                        name=d.name, u_position=None, reason="no position"
                    )
                )
                continue
            device = RackDevice(
                rack_id=rack.id, **{**fields, "source": "rackula"}
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
            if d.carrier_key:
                carriers[d.carrier_key] = device
            created += 1
        # Flush so payload carriers hold real ids before children mount.
        await session.flush()
        for d in children:
            carrier = (
                resolve_carrier(placed, d.carrier_id)
                if d.carrier_id is not None
                else carriers.get(d.carrier_key or "")
            )
            if carrier is None:
                skipped.append(
                    SkippedDevice(
                        name=d.name,
                        u_position=d.u_position,
                        reason="carrier not in the import payload",
                    )
                )
                continue
            fields = {
                **d.model_dump(exclude={"carrier_key"}),
                "carrier_id": carrier.id,
                "u_position": carrier.u_position,
                "face": carrier.face,
                "source": "rackula",
            }
            device = RackDevice(rack_id=rack.id, **fields)
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
