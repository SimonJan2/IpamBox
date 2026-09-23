"""Rack device placement: U-range bounds + face-aware collision rules.

Occupied span of a device is [u_position, u_position + u_height) in integer
U slots. Two rack-level devices conflict iff their spans overlap AND their
faces collide: `both` collides with everything, same faces collide,
front/rear never collide (opposite faces share U space legally).

Carriers: a rack-level device with `slot_layout` set is a tray whose
children mount into `slot` indices (halves=2, quarters=4, shelf=1).
Children (`carrier_id` set) never touch rack-level collision space — the
carrier already reserved its whole span — they only conflict with siblings
occupying the same slot.

Devices vs racks: a Device exists without a rack (rack_id NULL = unracked
inventory). Placement math only ever sees racked rows — callers filter by
rack_id before reaching this module.
"""
from collections.abc import Iterable
from typing import Literal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.device import Device
from app.models.rack import Rack, RackFace, RackGroup
from app.services.ipam import ConflictError, IPAMError, NotFoundError


class PlacementBoundsError(IPAMError):
    status_code = 422


class CarrierError(IPAMError):
    status_code = 422


SLOT_LAYOUTS = {"halves": 2, "quarters": 4, "shelf": 1}

# Columns that describe where the device sits — all NULL when unracked.
PLACEMENT_FIELDS = {
    "rack_id",
    "u_position",
    "u_height",
    "face",
    "carrier_id",
    "slot",
    "slot_layout",
}

# Fields mirrored onto the merged candidate used for placement checks.
_DEVICE_FIELD_NAMES = (
    "name",
    "device_type",
    "u_position",
    "u_height",
    "face",
    "colour",
    "category",
    "manufacturer",
    "model",
    "asset_id",
    "source",
    "carrier_id",
    "slot",
    "slot_layout",
    "watts",
    "weight_kg",
    "notes",
)


def _faces_collide(a: RackFace, b: RackFace) -> bool:
    return RackFace.BOTH in (a, b) or a == b


def device_fields(device: Device) -> dict:
    """Snapshot of the placement-relevant columns for merged candidates."""
    return {field: getattr(device, field) for field in _DEVICE_FIELD_NAMES}


async def rack_devices(session: AsyncSession, rack_id: int) -> list[Device]:
    """All devices placed in a rack (unracked devices never qualify)."""
    return list(
        (
            await session.execute(
                select(Device)
                .where(Device.rack_id == rack_id)
                .order_by(Device.u_position, Device.id)
            )
        )
        .scalars()
        .all()
    )


async def carrier_children(session: AsyncSession, carrier_id: int) -> list[Device]:
    """Devices mounted on a carrier — queried globally, not per-rack, so
    children that stayed mounted to an unracked tray are still found."""
    return list(
        (
            await session.execute(
                select(Device).where(Device.carrier_id == carrier_id)
            )
        )
        .scalars()
        .all()
    )


def resolve_carrier(
    devices: Iterable[Device], carrier_id: int
) -> Device | None:
    """The carrier row within this rack's devices, else None."""
    return next((d for d in devices if d.id == carrier_id), None)


def placement_conflicts(
    devices: Iterable[Device],
    candidate: Device,
    exclude_id: int | None = None,
) -> list[Device]:
    """Existing devices that collide with `candidate`.

    Children collide only with siblings in the same (carrier_id, slot);
    rack-level candidates collide only with rack-level devices (the carrier
    counts as its whole U span + face, its children are invisible here).
    """
    out = []
    if candidate.carrier_id is not None:
        for d in devices:
            if exclude_id is not None and d.id == exclude_id:
                continue
            if d.carrier_id == candidate.carrier_id and d.slot == candidate.slot:
                out.append(d)
        return out
    lo, hi = candidate.u_position, candidate.u_position + (candidate.u_height or 1)
    for d in devices:
        if exclude_id is not None and d.id == exclude_id:
            continue
        if d.carrier_id is not None:
            continue
        if lo < d.u_position + (d.u_height or 1) and d.u_position < hi:
            if _faces_collide(d.face, candidate.face):
                out.append(d)
    return out


def _check_carrier_mount(
    devices: Iterable[Device],
    candidate: Device,
    exclude_id: int | None,
) -> None:
    """422s on every way a carrier mount can be malformed (single level,
    slot in range, child no taller than its carrier)."""
    if exclude_id is not None and candidate.carrier_id == exclude_id:
        raise CarrierError("a device can't be its own carrier")
    if candidate.slot_layout is not None:
        raise CarrierError("a carrier can't mount inside another carrier")
    carrier = resolve_carrier(devices, candidate.carrier_id)
    if carrier is None:
        raise CarrierError(
            f"carrier {candidate.carrier_id} not found in this rack"
        )
    if carrier.carrier_id is not None:
        raise CarrierError("carriers can't nest — pick a rack-level carrier")
    count = SLOT_LAYOUTS.get(carrier.slot_layout or "")
    if count is None:
        raise CarrierError(
            f"{carrier.name or f'#{carrier.id}'} is not a carrier"
        )
    if candidate.slot is None or not 0 <= candidate.slot < count:
        raise CarrierError(
            f"slot must be 0–{count - 1} for a {carrier.slot_layout} carrier"
        )
    if (candidate.u_height or 1) > (carrier.u_height or 1):
        raise CarrierError(
            f"child is taller than its carrier ({carrier.u_height}U)"
        )


def check_placement(
    rack: Rack,
    devices: Iterable[Device],
    candidate: Device,
    exclude_id: int | None = None,
) -> None:
    """Raise 422 on out-of-bounds/malformed placement, 409 on a collision."""
    devices = list(devices)  # carrier lookup + conflict pass both iterate
    if candidate.carrier_id is not None:
        # The carrier already passed rack-bounds; children inherit its span.
        _check_carrier_mount(devices, candidate, exclude_id)
    else:
        if candidate.slot is not None:
            raise CarrierError("slot requires carrier_id")
        top = candidate.u_position + (candidate.u_height or 1) - 1
        if candidate.u_position < 1 or top > rack.height_u:
            raise PlacementBoundsError(
                f"U{candidate.u_position}–U{top} exceeds rack height {rack.height_u}U"
            )
    conflicts = placement_conflicts(devices, candidate, exclude_id)
    if conflicts:
        names = ", ".join(d.name or f"#{d.id}" for d in conflicts[:5])
        raise ConflictError(f"placement conflicts with: {names}")


def inherit_carrier(devices: Iterable[Device], patch: dict) -> Device | None:
    """Derive the carrier for patch['carrier_id'] and copy its u_position/
    face into the patch. Returns the carrier row or None."""
    carrier = (
        resolve_carrier(devices, patch["carrier_id"])
        if patch.get("carrier_id") is not None
        else None
    )
    if carrier is not None:
        patch["u_position"] = carrier.u_position
        patch["face"] = carrier.face
    return carrier


def check_layout_change(children: list[Device], device: Device, patch: dict) -> None:
    """A carrier's slot_layout can only shrink/clear when no mounted child
    sits in a slot the new layout doesn't have."""
    if "slot_layout" not in patch:
        return
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


async def apply_device_patch(
    session: AsyncSession, device: Device, patch: dict
) -> None:
    """Validate + apply an attribute/placement patch to `device` in-session.

    Shared by the rack route (UI compat) and PATCH /devices/{id}:

    - ``rack_id=None`` unracks: placement clears, mounted children leave the
      rack with their carrier but stay mounted to it (the tray still holds
      them — re-racking the carrier re-racks the children).
    - ``rack_id=X`` re-homes, validated against the target's occupancy.
    - Placement edits on an unracked device without rack_id are rejected —
      set rack_id (or carrier_id, which implies its rack) to place it.
    """
    # Explicit unrack.
    if "rack_id" in patch and patch["rack_id"] is None:
        for field, value in patch.items():
            if field != "rack_id":
                setattr(device, field, value)
        # Placement clears after the attribute patch — stray placement keys
        # in the same patch can't resurrect a partial placement.
        device.rack_id = None
        device.u_position = None
        device.carrier_id = None
        device.slot = None
        for child in await carrier_children(session, device.id):
            child.rack_id = None
            child.u_position = None
        return

    # A bare carrier_id on an unracked device implies its carrier's rack.
    if patch.get("carrier_id") is not None and (
        patch.get("rack_id", device.rack_id) is None
    ):
        carrier_row = await session.get(Device, patch["carrier_id"])
        if carrier_row is None or carrier_row.rack_id is None:
            raise CarrierError(
                f"carrier {patch['carrier_id']} is not racked"
            )
        patch["rack_id"] = carrier_row.rack_id

    target_rack_id = patch.get("rack_id", device.rack_id)
    if target_rack_id is None:
        # Unracked device, attribute-only patch. u_height/face/slot_layout
        # are device attributes; u_position/carrier_id/slot need a rack.
        bad = [
            k
            for k, v in patch.items()
            if k in ("u_position", "carrier_id", "slot") and v is not None
        ]
        if bad:
            raise PlacementBoundsError(
                "set rack_id to place the device (fields: "
                + ", ".join(sorted(bad))
                + ")"
            )
        for field, value in patch.items():
            setattr(device, field, value)
        return

    target_rack = await session.get(Rack, target_rack_id)
    if target_rack is None:
        raise NotFoundError(f"Rack {target_rack_id} not found")
    target_devices = await rack_devices(session, target_rack.id)
    if target_rack_id != device.rack_id and "carrier_id" not in patch:
        # Moving racks unmounts unless a new carrier is named in the same patch.
        patch["carrier_id"] = None
    if patch.get("carrier_id", "unset") is None and "slot" not in patch:
        patch["slot"] = None
    merged = {**device_fields(device), **patch}
    merged.pop("rack_id", None)
    if merged["u_position"] is None and merged["carrier_id"] is None:
        raise PlacementBoundsError(
            "u_position is required unless the device mounts into a carrier"
        )
    merged["u_height"] = merged["u_height"] or 1
    merged["face"] = merged["face"] or RackFace.FRONT
    carrier = inherit_carrier(target_devices, merged)
    candidate = Device(rack_id=target_rack.id, **merged)
    check_placement(target_rack, target_devices, candidate, exclude_id=device.id)
    children = await carrier_children(session, device.id)
    check_layout_change(children, device, patch)
    moved_racks = target_rack.id != device.rack_id
    for field, value in patch.items():
        setattr(device, field, value)
    if device.u_height is None:
        device.u_height = 1
    if device.face is None:
        device.face = RackFace.FRONT
    if carrier is not None:
        device.u_position = carrier.u_position
        device.face = carrier.face
    # Carrier children mirror span/face and follow across racks.
    if device.slot_layout is not None and (
        "u_position" in patch or "face" in patch or moved_racks
    ):
        for child in children:
            child.u_position = device.u_position
            child.face = device.face
            child.rack_id = target_rack.id


def used_u(devices: Iterable[Device]) -> int:
    """Distinct U slots occupied on either face (front+rear pair counts once).

    Children share their carrier's span, so they never add a slot.
    """
    slots: set[int] = set()
    for d in devices:
        slots.update(range(d.u_position, d.u_position + (d.u_height or 1)))
    return len(slots)


async def stamp_rack_stats(
    session: AsyncSession, racks: Iterable[Rack]
) -> list[Rack]:
    """Set the transient aggregates RackOut serializes: device_count, used_u,
    power_w, weight_kg and group_name.

    power_w/weight_kg stay None when no device supplies a value — the UI
    hides the totals rather than showing a misleading zero. Devices are
    re-queried rather than trusting the ORM collection because tests share a
    session with expire_on_commit=False.
    """
    racks = list(racks)
    ids = [r.id for r in racks]
    by_rack: dict[int, list[Device]] = {i: [] for i in ids}
    if ids:
        rows = (
            await session.execute(
                select(Device).where(Device.rack_id.in_(ids))
            )
        ).scalars().all()
        for d in rows:
            by_rack[d.rack_id].append(d)
    group_ids = {r.group_id for r in racks if r.group_id is not None}
    groups = {}
    if group_ids:
        groups = {
            g.id: g
            for g in (
                await session.execute(
                    select(RackGroup).where(RackGroup.id.in_(group_ids))
                )
            )
            .scalars()
            .all()
        }
    for r in racks:
        devs = by_rack[r.id]
        r.device_count = len(devs)
        r.used_u = used_u(devs)
        watts = [d.watts for d in devs if d.watts is not None]
        r.power_w = sum(watts) if watts else None
        weights = [d.weight_kg for d in devs if d.weight_kg is not None]
        r.weight_kg = float(sum(weights)) if weights else None
        group = groups.get(r.group_id) if r.group_id is not None else None
        r.group_name = group.name if group is not None else None
    return racks


def find_free_u(
    rack: Rack,
    devices: Iterable[Device],
    height: int,
    face: RackFace,
    side: Literal["bottom", "top"] = "bottom",
) -> int | None:
    """Start U where a `height`-U `face` device fits, else None.

    side=bottom scans upward from U1, side=top scans down from the highest
    legal start. Face-aware via placement_conflicts: a front request may
    overlap rear-face devices.
    """
    if height < 1 or height > rack.height_u:
        raise PlacementBoundsError(
            f"height {height}U outside rack height {rack.height_u}U"
        )
    existing = list(devices)  # scanned once per candidate — no generator reuse
    last = rack.height_u - height + 1
    starts = range(1, last + 1) if side == "bottom" else range(last, 0, -1)
    for u in starts:
        candidate = Device(
            rack_id=rack.id, name="", u_position=u, u_height=height, face=face
        )
        if not placement_conflicts(existing, candidate):
            return u
    return None
