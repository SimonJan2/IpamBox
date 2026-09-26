"""Device templates (V10.1) — CRUD + instantiate.

Hand-written rather than `_crud_router`: PATCH needs the builtin-fork
rule (editing a ``source='builtin'`` row flips it to ``'manual'`` — the
row becomes your copy, the catalog name is never silently mutated
mid-edit), and instantiate composes device create + placement + template
apply in one transaction. The layout's JSONB shape is enforced by the
pydantic schemas (bad ``kind`` → 422).

``POST /{id}/instantiate`` mirrors ``POST /devices`` — same carrier
inherit + ``check_placement`` rules — then stamps the port layout in the
same commit, so a failed apply leaves no half-created device.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.devices import _check_refs, _detail
from app.core.db import get_session
from app.core.deps import DATA_DELETE, DATA_WRITE, require_perm
from app.models.cabling import DeviceInterface  # noqa: F401 — mapper FK target
from app.models.device import Device
from app.models.device_template import DeviceTemplate
from app.models.ip_address import IPAddress
from app.models.rack import Rack, RackFace
from app.schemas.common import Page
from app.schemas.device_template import (
    DeviceTemplateCreate,
    DeviceTemplateOut,
    DeviceTemplateUpdate,
    TemplateInstantiateIn,
    TemplateInstantiateOut,
    TemplateInterface,
    TemplatePowerPort,
    _validate_layout,
)
from app.services.device_templates import apply_template
from app.services.ipam import IPAMError, get_or_404
from app.services.racks import check_placement, rack_devices
from app.services.workbook.normalize import fold_hebrew

router = APIRouter(prefix="/device-templates", tags=["device-templates"])


async def _get(session: AsyncSession, template_id: int) -> DeviceTemplate:
    try:
        return await get_or_404(session, DeviceTemplate, template_id)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))


@router.get("", response_model=Page[DeviceTemplateOut])
async def list_templates(
    q: str = "",
    limit: int | None = Query(default=None, ge=1, le=20000),
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
):
    stmt = select(DeviceTemplate)
    if q:
        like = f"%{fold_hebrew(q)}%"
        stmt = stmt.where(
            or_(
                *(
                    func.translate(col, "םןץףך", "מנצפכ").ilike(like)
                    for col in (
                        DeviceTemplate.name,
                        DeviceTemplate.manufacturer,
                        DeviceTemplate.model,
                        DeviceTemplate.device_type,
                        DeviceTemplate.category,
                    )
                )
            )
        )
    stmt = stmt.order_by(DeviceTemplate.name, DeviceTemplate.id)
    total = await session.scalar(
        select(func.count()).select_from(stmt.order_by(None).subquery())
    )
    rows = (
        (await session.execute(stmt.limit(limit).offset(offset)))
        .scalars()
        .all()
    )
    return Page(items=rows, total=total or 0, limit=limit, offset=offset)


@router.post(
    "",
    response_model=DeviceTemplateOut,
    status_code=201,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def create_template(
    body: DeviceTemplateCreate, session: AsyncSession = Depends(get_session)
):
    obj = DeviceTemplate(**body.model_dump(mode="json"))
    session.add(obj)
    try:
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(409, "duplicate or invalid value") from e
    await session.refresh(obj)
    return obj


@router.get("/{template_id}", response_model=DeviceTemplateOut)
async def get_template(
    template_id: int, session: AsyncSession = Depends(get_session)
):
    return await _get(session, template_id)


@router.patch(
    "/{template_id}",
    response_model=DeviceTemplateOut,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def update_template(
    template_id: int,
    body: DeviceTemplateUpdate,
    session: AsyncSession = Depends(get_session),
):
    obj = await _get(session, template_id)
    patch = body.model_dump(exclude_unset=True, mode="json")
    # Layout fields cross-validate against each other — re-check the
    # merged pair/interface set so a partial PATCH can't store a layout
    # whose power ports collide with untouched interfaces (or vice versa).
    if "interfaces" in patch or "power_ports" in patch:
        try:
            _validate_layout(
                [
                    TemplateInterface(**i)
                    for i in patch.get("interfaces", obj.interfaces)
                ],
                [
                    TemplatePowerPort(**p)
                    for p in patch.get("power_ports", obj.power_ports) or []
                ]
                or None,
            )
        except ValueError as e:
            raise HTTPException(422, str(e))
    # Editing a builtin forks it: the row becomes the user's manual copy
    # (changelog records source: builtin→manual alongside the field diffs).
    if obj.source == "builtin" and "source" not in patch:
        patch["source"] = "manual"
    for field, value in patch.items():
        setattr(obj, field, value)
    try:
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(409, "duplicate or invalid value") from e
    await session.refresh(obj)
    return obj


@router.delete(
    "/{template_id}",
    status_code=204,
    dependencies=[Depends(require_perm(DATA_DELETE))],
)
async def delete_template(
    template_id: int, session: AsyncSession = Depends(get_session)
):
    obj = await _get(session, template_id)
    await session.delete(obj)
    await session.commit()


@router.post(
    "/{template_id}/instantiate",
    response_model=TemplateInstantiateOut,
    status_code=201,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def instantiate_template(
    template_id: int,
    body: TemplateInstantiateIn,
    session: AsyncSession = Depends(get_session),
):
    """Create the device *and* stamp the layout in one transaction.

    Field rule: explicit payload values win, absent/null inherits the
    template (device_type, manufacturer, model, u_height, face, colour,
    category, watts, weight_kg, notes). Placement is the POST /devices
    rule-set — carrier mounts inherit from the carrier, rack placements
    run check_placement — so a collision refuses before anything writes.
    """
    template = await _get(session, template_id)
    data = {
        "name": body.name,
        "device_type": body.device_type or template.device_type,
        "manufacturer": body.manufacturer or template.manufacturer,
        "model": body.model or template.model,
        "u_height": body.u_height or template.u_height,
        "face": body.face
        if body.face is not None
        else RackFace(template.face_default),
        "colour": body.colour or template.colour,
        "category": body.category or template.category,
        "watts": body.watts if body.watts is not None else template.watts,
        "weight_kg": (
            body.weight_kg
            if body.weight_kg is not None
            else (
                float(template.weight_kg)
                if template.weight_kg is not None
                else None
            )
        ),
        "notes": body.notes if body.notes is not None else template.notes,
        "serial_number": body.serial_number,
        "mac_address": body.mac_address,
        "site_id": body.site_id,
        "asset_id": body.asset_id,
        "rack_id": body.rack_id,
        "u_position": body.u_position,
        "carrier_id": body.carrier_id,
        "slot": body.slot,
        "slot_layout": body.slot_layout,
        # provenance: the row was minted from a template.
        "source": "template",
    }
    # Same reference checks as POST /devices + the rack form's IP field.
    try:
        await _check_refs(session, data)
        if body.ip_address_id is not None:
            await get_or_404(session, IPAddress, body.ip_address_id)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))
    if data.get("carrier_id") is not None:
        carrier_row = await session.get(Device, data["carrier_id"])
        if carrier_row is None or carrier_row.rack_id is None:
            raise HTTPException(
                422, f"carrier {data['carrier_id']} is not racked"
            )
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
        await session.flush()
        if body.ip_address_id is not None:
            ip = await session.get(IPAddress, body.ip_address_id)
            if ip is not None:
                ip.device_id = device.id
        result = await apply_template(session, device, template, mode="merge")
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(409, "duplicate or invalid value") from e
    except IPAMError as e:
        await session.rollback()
        raise HTTPException(e.status_code, str(e))
    await session.refresh(device)
    return TemplateInstantiateOut(
        device=await _detail(session, device), **result
    )
