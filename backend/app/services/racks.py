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
"""
from collections.abc import Iterable
from typing import Literal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.rack import Rack, RackDevice, RackFace, RackGroup
from app.services.ipam import ConflictError, IPAMError


class PlacementBoundsError(IPAMError):
    status_code = 422


class CarrierError(IPAMError):
    status_code = 422


SLOT_LAYOUTS = {"halves": 2, "quarters": 4, "shelf": 1}


def _faces_collide(a: RackFace, b: RackFace) -> bool:
    return RackFace.BOTH in (a, b) or a == b


def resolve_carrier(
    devices: Iterable[RackDevice], carrier_id: int
) -> RackDevice | None:
    """The carrier row within this rack's devices, else None."""
    return next((d for d in devices if d.id == carrier_id), None)


def placement_conflicts(
    devices: Iterable[RackDevice],
    candidate: RackDevice,
    exclude_id: int | None = None,
) -> list[RackDevice]:
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
    lo, hi = candidate.u_position, candidate.u_position + candidate.u_height
    for d in devices:
        if exclude_id is not None and d.id == exclude_id:
            continue
        if d.carrier_id is not None:
            continue
        if lo < d.u_position + d.u_height and d.u_position < hi:
            if _faces_collide(d.face, candidate.face):
                out.append(d)
    return out


def _check_carrier_mount(
    devices: Iterable[RackDevice],
    candidate: RackDevice,
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
    if candidate.u_height > carrier.u_height:
        raise CarrierError(
            f"child is taller than its carrier ({carrier.u_height}U)"
        )


def check_placement(
    rack: Rack,
    devices: Iterable[RackDevice],
    candidate: RackDevice,
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
        top = candidate.u_position + candidate.u_height - 1
        if candidate.u_position < 1 or top > rack.height_u:
            raise PlacementBoundsError(
                f"U{candidate.u_position}–U{top} exceeds rack height {rack.height_u}U"
            )
    conflicts = placement_conflicts(devices, candidate, exclude_id)
    if conflicts:
        names = ", ".join(d.name or f"#{d.id}" for d in conflicts[:5])
        raise ConflictError(f"placement conflicts with: {names}")


def used_u(devices: Iterable[RackDevice]) -> int:
    """Distinct U slots occupied on either face (front+rear pair counts once).

    Children share their carrier's span, so they never add a slot.
    """
    slots: set[int] = set()
    for d in devices:
        slots.update(range(d.u_position, d.u_position + d.u_height))
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
    by_rack: dict[int, list[RackDevice]] = {i: [] for i in ids}
    if ids:
        rows = (
            await session.execute(
                select(RackDevice).where(RackDevice.rack_id.in_(ids))
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
    devices: Iterable[RackDevice],
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
        candidate = RackDevice(
            rack_id=rack.id, name="", u_position=u, u_height=height, face=face
        )
        if not placement_conflicts(existing, candidate):
            return u
    return None
