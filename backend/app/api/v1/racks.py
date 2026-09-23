"""Rack elevations: racks + nested devices + Rackula import.

Not a `_crud_router` — device collision validation, resolved asset/ip
summaries on the detail response, and the transactional import endpoint
don't fit the factory.

Devices are first-class entities now: these routes keep the v1 shape (the
rack UI barely notices) but manipulate `devices` rows' placement columns.
A rack-device DELETE *unracks* (placement NULL) — real deletion lives on
/devices/{id}; a rack delete leaves its devices behind as unracked
inventory instead of cascading them away.
"""
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.deps import DATA_DELETE, DATA_READ, DATA_WRITE, require_perm
from app.models.asset import Asset
from app.models.device import Device
from app.models.ip_address import IPAddress
from app.models.rack import Rack, RackFace, RackGroup
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
from app.services.devices import health_ip, ips_by_device
from app.services.ipam import IPAMError, get_or_404
from app.services.ordering import ordered, reorder
from app.services.racks import (
    apply_device_patch,
    check_placement,
    find_free_u,
    inherit_carrier,
    rack_devices,
    resolve_carrier,
    stamp_rack_stats,
)
from app.services.workbook.normalize import fold_hebrew

router = APIRouter(prefix="/racks", tags=["racks"])


async def _devices(session: AsyncSession, rack_id: int) -> list[Device]:
    return await rack_devices(session, rack_id)


async def _next_group_position(session: AsyncSession, group_id: int) -> int:
    """Append slot at the row's right end for a rack joining without an
    explicit group_position."""
    top = await session.scalar(
        select(func.coalesce(func.max(Rack.group_position), 0)).where(
            Rack.group_id == group_id
        )
    )
    return (top or 0) + 1


# Scalar columns only — the relation-backed fields (asset/ip) and derived
# transients (ip_address_id/ip_status/ip_last_seen) are stamped below; a
# blanket model_validate would read Device.asset into LinkedRef and crash.
_RACK_DEVICE_COLS = (
    "id", "rack_id", "name", "device_type", "u_position", "u_height",
    "face", "colour", "category", "manufacturer", "model", "asset_id",
    "source", "carrier_id", "slot", "slot_layout", "watts", "weight_kg",
    "notes", "created_at", "updated_at",
)


async def _device_out(
    session: AsyncSession, d: Device, ips: list[IPAddress] | None = None
) -> RackDeviceOut:
    """Device -> the v1 rack-device payload.

    The single-IP fields now describe the device's *health IP* — the
    worst-status address across ip_addresses.device_id (offline >
    discovered > dhcp > reserved > active). ip_status is the whole box's
    health rollup; None = unmonitored.
    """
    out = RackDeviceOut.model_validate(
        {f: getattr(d, f) for f in _RACK_DEVICE_COLS}
    )
    if d.asset_id is not None:
        # session.get, not d.asset: identity-map hits skip selectin loaders
        # and a lazy relationship load here would raise MissingGreenlet.
        a = await session.get(Asset, d.asset_id)
        if a is not None:
            label = " ".join(p for p in (a.vendor, a.model) if p) or a.serial_number or f"asset#{a.id}"
            out.asset = LinkedRef(id=a.id, label=label)
    ip = health_ip(ips or [])
    if ip is not None:
        label = ip_display(ip.address) or ""
        if ip.hostname:
            label = f"{label} ({ip.hostname})"
        out.ip = IpRef(id=ip.id, label=label, prefix_id=ip.prefix_id)
        out.ip_address_id = ip.id
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


_UNSET = object()


async def _link_single_ip(
    session: AsyncSession, device: Device, ip_id: int | None
) -> None:
    """`ip_address_id` write semantics: replace the device's IP set.

    The rack form's single "Linked IP" field behaves like the old scalar —
    patching it makes {ip_id} the device's whole set (null clears all).
    Multi-IP management lives on /devices detail + PATCH /addresses
    device_id, which is additive per-IP.
    """
    current = (
        await session.execute(
            select(IPAddress).where(IPAddress.device_id == device.id)
        )
    ).scalars().all()
    for ip in current:
        if ip.id != ip_id:
            ip.device_id = None
    if ip_id is not None:
        ip = await session.get(IPAddress, ip_id)
        if ip is not None:
            ip.device_id = device.id


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
    # One grouped IP query for the health rollup — no per-device N+1.
    ips = await ips_by_device(session, [d.id for d in devices])
    await stamp_rack_stats(session, [rack])
    await stamp_colors(session, "racks", [rack])
    out = RackDetail.model_validate(rack)
    out.devices = [
        await _device_out(session, d, ips.get(d.id, [])) for d in devices
    ]
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
            if d.u_position is not None
            and d.u_position + (d.u_height or 1) - 1 > patch["height_u"]
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
    """Devices survive: they're unracked, not deleted.

    Done at ORM level (not just the FK's SET NULL) so u_position clears too
    and every device gets a changelog update. Carrier children stay mounted
    to their tray — it still physically holds them, just outside any rack.
    """
    rack = await _get_rack(session, rack_id)
    for d in await _devices(session, rack.id):
        d.rack_id = None
        d.u_position = None
        if d.carrier_id is None:
            d.slot = None
    await session.delete(rack)
    await session.commit()


async def _get_device(
    session: AsyncSession, rack_id: int, device_id: int
) -> tuple[Rack, Device]:
    rack = await _get_rack(session, rack_id)
    device = await session.get(Device, device_id)
    if device is None or device.rack_id != rack_id:
        raise HTTPException(404, f"Device {device_id} not found")
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
    ip_link = fields.pop("ip_address_id", None)
    if fields["u_position"] is None and fields["carrier_id"] is None:
        raise HTTPException(
            422, "u_position is required unless the device mounts into a carrier"
        )
    inherit_carrier(devices, fields)
    device = Device(rack_id=rack.id, **fields)
    try:
        check_placement(rack, devices, device)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))
    session.add(device)
    try:
        await session.flush()
        if ip_link is not None:
            await _link_single_ip(session, device, ip_link)
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(409, "duplicate or invalid value") from e
    await session.refresh(device)
    ips = await ips_by_device(session, [device.id])
    return await _device_out(session, device, ips[device.id])


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
    _, device = await _get_device(session, rack_id, device_id)
    await _check_refs(session, body)
    patch = body.model_dump(exclude_unset=True)
    # ip_address_id is a link, not a devices column — apply it after the
    # placement patch so a rejected placement can't half-move links.
    ip_link = patch.pop("ip_address_id", _UNSET)
    try:
        await apply_device_patch(session, device, patch)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))
    if ip_link is not _UNSET:
        await _link_single_ip(session, device, ip_link)
    try:
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(409, "duplicate or invalid value") from e
    await session.refresh(device)
    ips = await ips_by_device(session, [device.id])
    return await _device_out(session, device, ips[device.id])


@router.delete(
    "/{rack_id}/devices/{device_id}",
    status_code=204,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def delete_device(
    rack_id: int, device_id: int, session: AsyncSession = Depends(get_session)
):
    """Unrack, not delete: placement NULLs, the device row lives on.

    Real deletion is DELETE /devices/{id}. Mounted children leave the rack
    with their carrier but stay mounted to it.
    """
    _, device = await _get_device(session, rack_id, device_id)
    try:
        await apply_device_patch(session, device, {"rack_id": None})
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))
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

    `replace` unracks existing devices first (they're first-class rows now —
    wiping would destroy inventory); `merge` keeps them and skips incoming
    rows that collide or fall outside the rack.
    """
    rack = await _get_rack(session, rack_id)
    placed = await _devices(session, rack.id)
    if body.mode == "replace":
        for d in placed:
            await apply_device_patch(session, d, {"rack_id": None})
        await session.flush()
        placed = []
    created = 0
    skipped: list[SkippedDevice] = []
    # carrier_key -> the carrier row created from this payload (children
    # reference it before real ids exist). links defer the ip_address_id
    # writes until the new rows hold real ids.
    carriers: dict[str, Device] = {}
    children: list[RackDeviceImportItem] = []
    links: list[tuple[Device, int | None]] = []
    try:
        for d in body.devices:
            if d.carrier_key and d.slot_layout is None:
                children.append(d)
                continue
            # this endpoint exists for Rackula round-trips — provenance is
            # fixed here rather than trusting the payload's source field.
            fields = d.model_dump(exclude={"carrier_key"})
            ip_link = fields.pop("ip_address_id", None)
            inherit_carrier(placed, fields)
            if fields["u_position"] is None:
                skipped.append(
                    SkippedDevice(
                        name=d.name, u_position=None, reason="no position"
                    )
                )
                continue
            device = Device(
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
            links.append((device, ip_link))
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
                **d.model_dump(exclude={"carrier_key", "ip_address_id"}),
                "carrier_id": carrier.id,
                "u_position": carrier.u_position,
                "face": carrier.face,
                "source": "rackula",
            }
            device = Device(rack_id=rack.id, **fields)
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
        await session.flush()
        for device, ip_id in links:
            if ip_id is not None:
                await _link_single_ip(session, device, ip_id)
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(409, "duplicate or invalid value") from e
    return RackImportResult(created=created, skipped=skipped)
