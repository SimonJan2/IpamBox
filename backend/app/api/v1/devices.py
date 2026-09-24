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

from app.api.v1.list_params import (
    parse_enum_set,
    parse_int_set,
    parse_str_set,
    parse_token_set,
)
from app.core.db import get_session
from app.core.deps import DATA_DELETE, DATA_WRITE, require_perm
from app.models.asset import Asset
from app.models.cabling import DeviceInterface
from app.models.device import Device
from app.models.ip_address import IPAddress
from app.models.rack import Rack, RackFace
from app.models.site import Site
from app.schemas.cabling import (
    DeviceInterfaceCreate,
    DeviceInterfaceOut,
    DeviceInterfaceUpdate,
    InterfaceGenerateBody,
)
from app.schemas.common import Page, ReorderBody, ip_display
from app.schemas.device import (
    DeviceCreate,
    DeviceDetail,
    DeviceIpRef,
    DeviceOut,
    DeviceUpdate,
)
from app.schemas.rack import LinkedRef
from app.services.cabling import (
    cable_for,
    interface_stats,
    pair_of,
    peers_for,
    stamp_connected_ips,
)
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
    out.interface_count, out.cabled_count = (
        await interface_stats(session, [device.id])
    )[device.id]
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


# wiring facet classes — computed over interface_stats after the aggregate
# pass, same class as the health rollup. `uncabled` includes devices with no
# interfaces at all (zero cabled ports is zero cabled ports).
_WIRING_CLASSES = ("cabled", "partial", "uncabled")


def _wiring_class(interface_count: int, cabled_count: int) -> str:
    if cabled_count == 0:
        return "uncabled"
    if cabled_count >= interface_count:
        return "cabled"
    return "partial"


@router.get("", response_model=Page[DeviceOut])
async def list_devices(
    q: str = "",
    rack_id: str | None = Query(
        default=None, description="rack id or comma-separated rack ids"
    ),
    site_id: str | None = Query(
        default=None, description="site id or comma-separated site ids"
    ),
    group_id: str | None = Query(
        default=None,
        description="rack-group id(s) — resolves through the device's rack",
    ),
    unracked: bool | None = None,
    mounted: bool | None = Query(
        default=None, description="carrier_id IS (NOT) NULL — carrier children"
    ),
    face: str | None = Query(
        default=None, description="front|rear|both or comma-separated set"
    ),
    manufacturer: str = "",
    model: str = "",
    category: str = "",
    device_type: str = "",
    source: str = "",
    has_ip: bool | None = Query(
        default=None, description="EXISTS / NOT EXISTS on ip_addresses.device_id"
    ),
    wiring: str | None = Query(
        default=None,
        description="cabled|partial|uncabled or CSV — post-aggregate filter",
    ),
    limit: int | None = Query(default=None, ge=1, le=20000),
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
):
    rack_ids = parse_int_set(rack_id, "rack_id")
    site_ids = parse_int_set(site_id, "site_id")
    group_ids = parse_int_set(group_id, "group_id")
    faces = parse_enum_set(face, "face", RackFace)
    sources = parse_str_set(source)
    wirings = parse_token_set(wiring, "wiring", _WIRING_CLASSES)

    stmt = select(Device)
    if rack_ids:
        stmt = stmt.where(Device.rack_id.in_(rack_ids))
    if site_ids:
        stmt = stmt.where(Device.site_id.in_(site_ids))
    if group_ids:
        stmt = stmt.where(
            Device.rack_id.in_(
                select(Rack.id).where(Rack.group_id.in_(group_ids))
            )
        )
    if unracked is not None:
        stmt = stmt.where(
            Device.rack_id.is_(None) if unracked else Device.rack_id.isnot(None)
        )
    if mounted is not None:
        stmt = stmt.where(
            Device.carrier_id.isnot(None)
            if mounted
            else Device.carrier_id.is_(None)
        )
    if faces:
        # face defaults to FRONT even when unracked — the facet means
        # "placement face", so it only applies to placed devices.
        stmt = stmt.where(
            Device.rack_id.isnot(None), Device.face.in_(faces)
        )
    for col, val in (
        (Device.manufacturer, manufacturer),
        (Device.model, model),
        (Device.category, category),
        (Device.device_type, device_type),
    ):
        if val:
            like = f"%{fold_hebrew(val)}%"
            stmt = stmt.where(
                func.translate(col, "םןץףך", "מנצפכ").ilike(like)
            )
    if sources:
        stmt = stmt.where(Device.source.in_(sources))
    if has_ip is not None:
        stmt = stmt.where(
            Device.ips.any() if has_ip else ~Device.ips.any()
        )
    if q:
        # Same haystack as the page's client-side q: device fields plus the
        # rack/site names, so V5B exports replay the identical set.
        like = f"%{fold_hebrew(q)}%"
        stmt = (
            stmt.outerjoin(Rack, Device.rack_id == Rack.id)
            .outerjoin(Site, Device.site_id == Site.id)
            .where(
                or_(
                    func.translate(Device.name, "םןץףך", "מנצפכ").ilike(like),
                    func.translate(Device.device_type, "םןץףך", "מנצפכ").ilike(like),
                    func.translate(Device.serial_number, "םןץףך", "מנצפכ").ilike(like),
                    func.translate(Device.manufacturer, "םןץףך", "מנצפכ").ilike(like),
                    func.translate(Device.model, "םןץףך", "מנצפכ").ilike(like),
                    func.translate(Device.mac_address, "םןץףך", "מנצפכ").ilike(like),
                    func.translate(Device.category, "םןץףך", "מנצפכ").ilike(like),
                    func.translate(Device.notes, "םןץףך", "מנצפכ").ilike(like),
                    func.translate(Rack.name, "םןץףך", "מנצפכ").ilike(like),
                    func.translate(Site.name, "םןץףך", "מנצפכ").ilike(like),
                )
            )
        )
    stmt = ordered(stmt, Device, Device.name, Device.id)

    # Computed-field filters (wiring today; health joins on the export side)
    # apply after the aggregate pass — so when one is active the SQL page has
    # to wait: fetch the full SQL-matching set, facet it, then slice. `total`
    # stays the honest filtered count either way.
    if wirings is None:
        total = await session.scalar(
            select(func.count()).select_from(stmt.order_by(None).subquery())
        )
        rows = list(
            (await session.execute(stmt.limit(limit).offset(offset)))
            .scalars()
            .all()
        )
    else:
        rows = list((await session.execute(stmt)).scalars().all())
    istats = await interface_stats(session, [d.id for d in rows])
    if wirings is not None:
        rows = [
            d for d in rows if _wiring_class(*istats[d.id]) in wirings
        ]
        total = len(rows)
        rows = rows[offset : offset + limit if limit else None]
    await stamp_colors(session, "devices", rows)
    # Health + counts in grouped queries — never per-row.
    ips = await ips_by_device(session, [d.id for d in rows])
    items = []
    for d in rows:
        out = DeviceOut.model_validate(d)
        out.health = device_health(ips[d.id])
        out.ip_count = len(ips[d.id])
        out.interface_count, out.cabled_count = istats[d.id]
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


# ---------------------------------------------------------------------------
# Interfaces — the L1 layer. Ports live under their device; cables +
# single-interface fetches live in api.v1.cables.
# ---------------------------------------------------------------------------


async def _get_iface(
    session: AsyncSession, device_id: int, iface_id: int
) -> DeviceInterface:
    iface = await session.get(DeviceInterface, iface_id)
    if iface is None or iface.device_id != device_id:
        raise HTTPException(
            404, f"Interface {iface_id} not found on this device"
        )
    return iface


async def _iface_outs(
    session: AsyncSession, ifaces: list[DeviceInterface]
) -> list[DeviceInterfaceOut]:
    """Interfaces -> DeviceInterfaceOut with resolved peer + connected IP."""
    peers = await peers_for(session, ifaces)
    outs = [DeviceInterfaceOut.model_validate(i) for i in ifaces]
    for out in outs:
        out.peer = peers.get(out.id)
    await stamp_connected_ips(session, outs)
    return outs


async def _check_iface_refs(
    session: AsyncSession,
    device: Device,
    data: dict,
    iface_id: int | None = None,
) -> None:
    """Existence + compatibility checks for interface FK fields.

    connected_ip_id must serve one of this device's own IPs (a port can't
    bind another box's address); pair_interface_id must be an unpaired
    interface on the same device (a panel position's two sides live on one
    panel).
    """
    if data.get("connected_ip_id") is not None:
        try:
            ip = await get_or_404(
                session, IPAddress, data["connected_ip_id"]
            )
        except IPAMError as e:
            raise HTTPException(e.status_code, str(e))
        if ip.device_id is not None and ip.device_id != device.id:
            raise HTTPException(
                422,
                f"{ip_display(ip.address)} belongs to another device — a "
                "port can only serve its own device's IPs",
            )
    if data.get("pair_interface_id") is not None:
        pid = data["pair_interface_id"]
        if pid == iface_id:
            raise HTTPException(422, "an interface cannot be its own pair")
        pair = await session.get(DeviceInterface, pid)
        if pair is None:
            raise HTTPException(404, f"Interface {pid} not found")
        if pair.device_id != device.id:
            raise HTTPException(
                422, "a pair must be an interface on the same device"
            )
        if (
            pair.pair_interface_id is not None
            and pair.pair_interface_id != iface_id
        ):
            raise HTTPException(
                409, f"interface '{pair.name}' is already paired"
            )


@router.get("/{device_id}/interfaces", response_model=list[DeviceInterfaceOut])
async def list_interfaces(
    device_id: int, session: AsyncSession = Depends(get_session)
):
    device = await _get_device(session, device_id)
    ifaces = (
        (
            await session.execute(
                select(DeviceInterface)
                .where(DeviceInterface.device_id == device.id)
                .order_by(
                    DeviceInterface.position,
                    DeviceInterface.name,
                    DeviceInterface.id,
                )
            )
        )
        .scalars()
        .all()
    )
    return await _iface_outs(session, list(ifaces))


@router.post(
    "/{device_id}/interfaces",
    response_model=DeviceInterfaceOut,
    status_code=201,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def create_interface(
    device_id: int,
    body: DeviceInterfaceCreate,
    session: AsyncSession = Depends(get_session),
):
    device = await _get_device(session, device_id)
    data = body.model_dump()
    await _check_iface_refs(session, device, data)
    dup = await session.scalar(
        select(DeviceInterface.id).where(
            DeviceInterface.device_id == device.id,
            DeviceInterface.name == data["name"],
        )
    )
    if dup is not None:
        raise HTTPException(
            409, f"interface '{data['name']}' already exists on this device"
        )
    if data.get("position") is None:
        data["position"] = (
            await session.scalar(
                select(
                    func.coalesce(func.max(DeviceInterface.position), -1)
                ).where(DeviceInterface.device_id == device.id)
            )
        ) + 1
    iface = DeviceInterface(device_id=device.id, **data)
    session.add(iface)
    try:
        await session.flush()
        await _reciprocate_pair(session, iface)
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(
            409, f"interface '{data['name']}' already exists on this device"
        ) from e
    await session.refresh(iface)
    return (await _iface_outs(session, [iface]))[0]


async def _reciprocate_pair(
    session: AsyncSession, iface: DeviceInterface
) -> None:
    """When a pair target has no link back, complete it — one-sided links
    resolve in the trace regardless, but bidirectional data stays honest.
    Flush-level helper: callers own the commit."""
    if iface.pair_interface_id is None:
        return
    pair = await session.get(DeviceInterface, iface.pair_interface_id)
    if pair is not None and pair.pair_interface_id is None:
        pair.pair_interface_id = iface.id
        await session.flush()


# Declared before /{device_id}/interfaces/{iface_id} so the literal path
# can't be shadowed.
@router.post(
    "/{device_id}/interfaces/generate",
    response_model=list[DeviceInterfaceOut],
    status_code=201,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def generate_interfaces(
    device_id: int,
    body: InterfaceGenerateBody,
    session: AsyncSession = Depends(get_session),
):
    """One-click port factory: Gi1/0/1..48-style names in a single call.

    With `pair_prefix` a second same-indexed row per port is created and
    paired 1:1 — a patch panel's front+back sides in one shot.
    """
    device = await _get_device(session, device_id)
    if body.pair_prefix is not None and body.pair_prefix == body.prefix:
        raise HTTPException(422, "pair_prefix must differ from prefix")
    indexes = range(body.start_index, body.start_index + body.count)
    names = [f"{body.prefix}{i}" for i in indexes]
    pair_names = (
        [f"{body.pair_prefix}{i}" for i in indexes]
        if body.pair_prefix is not None
        else []
    )
    all_names = names + pair_names
    if len(set(all_names)) != len(all_names):
        raise HTTPException(422, "generated names contain duplicates")
    conflicts = set(
        (
            await session.execute(
                select(DeviceInterface.name).where(
                    DeviceInterface.device_id == device.id,
                    DeviceInterface.name.in_(all_names),
                )
            )
        ).scalars()
    )
    if conflicts:
        raise HTTPException(
            409,
            f"interface '{sorted(conflicts)[0]}' already exists on this "
            f"device ({len(conflicts)} conflict(s))",
        )
    fronts = [
        DeviceInterface(
            device_id=device.id,
            name=n,
            kind=body.kind,
            speed_mbps=body.speed_mbps,
            position=i,
        )
        for i, n in zip(indexes, names)
    ]
    backs = [
        DeviceInterface(
            device_id=device.id,
            name=n,
            kind=body.kind,
            speed_mbps=body.speed_mbps,
            # Same position as the paired front — the port grid keeps a
            # position's front/back ports adjacent.
            position=i,
        )
        for i, n in zip(indexes, pair_names)
    ]
    session.add_all(fronts + backs)
    try:
        await session.flush()
        for f, b in zip(fronts, backs):
            f.pair_interface_id = b.id
            b.pair_interface_id = f.id
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(
            409, "generated name conflicts with an existing interface"
        ) from e
    # Re-select: commit expired the in-memory objects and lazy refresh
    # can't run under pydantic's sync attribute access.
    ids = [i.id for i in fronts + backs]
    fresh = (
        (
            await session.execute(
                select(DeviceInterface).where(DeviceInterface.id.in_(ids))
            )
        )
        .scalars()
        .all()
    )
    by_id = {i.id: i for i in fresh}
    return await _iface_outs(session, [by_id[i] for i in ids])


@router.patch(
    "/{device_id}/interfaces/{iface_id}",
    response_model=DeviceInterfaceOut,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def update_interface(
    device_id: int,
    iface_id: int,
    body: DeviceInterfaceUpdate,
    session: AsyncSession = Depends(get_session),
):
    device = await _get_device(session, device_id)
    iface = await _get_iface(session, device.id, iface_id)
    patch = body.model_dump(exclude_unset=True)
    await _check_iface_refs(session, device, patch, iface_id=iface.id)
    if patch.get("name") and patch["name"] != iface.name:
        dup = await session.scalar(
            select(DeviceInterface.id).where(
                DeviceInterface.device_id == device.id,
                DeviceInterface.name == patch["name"],
                DeviceInterface.id != iface.id,
            )
        )
        if dup is not None:
            raise HTTPException(
                409,
                f"interface '{patch['name']}' already exists on this device",
            )
    # Re-pairing unlinks the old partner's side so links stay reciprocal.
    if (
        "pair_interface_id" in patch
        and iface.pair_interface_id is not None
        and iface.pair_interface_id != patch["pair_interface_id"]
    ):
        old = await session.get(DeviceInterface, iface.pair_interface_id)
        if old is not None and old.pair_interface_id == iface.id:
            old.pair_interface_id = None
    for field, value in patch.items():
        setattr(iface, field, value)
    try:
        await session.flush()
        await _reciprocate_pair(session, iface)
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(409, "duplicate or invalid value") from e
    await session.refresh(iface)
    return (await _iface_outs(session, [iface]))[0]


@router.delete(
    "/{device_id}/interfaces/{iface_id}",
    status_code=204,
    dependencies=[Depends(require_perm(DATA_DELETE))],
)
async def delete_interface(
    device_id: int,
    iface_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Delete a port. Its cable goes too (deleted at ORM level so the cable
    gets a changelog row; the DB CASCADE is the backstop) and the panel
    partner is unpaired first."""
    device = await _get_device(session, device_id)
    iface = await _get_iface(session, device.id, iface_id)
    cable = await cable_for(session, iface.id)
    if cable is not None:
        await session.delete(cable)
    pair = await pair_of(session, iface)
    if pair is not None:
        pair.pair_interface_id = None
    await session.delete(iface)
    await session.commit()
