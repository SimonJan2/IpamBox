"""Rack device placement: U-range bounds + face-aware collision rules.

Occupied span of a device is [u_position, u_position + u_height) in integer
U slots. Two devices conflict iff their spans overlap AND their faces
collide: `both` collides with everything, same faces collide, front/rear
never collide (opposite faces share U space legally).
"""
from collections.abc import Iterable
from typing import Literal

from app.models.rack import Rack, RackDevice, RackFace
from app.services.ipam import ConflictError, IPAMError


class PlacementBoundsError(IPAMError):
    status_code = 422


def _faces_collide(a: RackFace, b: RackFace) -> bool:
    return RackFace.BOTH in (a, b) or a == b


def placement_conflicts(
    devices: Iterable[RackDevice],
    candidate: RackDevice,
    exclude_id: int | None = None,
) -> list[RackDevice]:
    """Existing devices that collide with `candidate` (by span + face)."""
    lo, hi = candidate.u_position, candidate.u_position + candidate.u_height
    out = []
    for d in devices:
        if exclude_id is not None and d.id == exclude_id:
            continue
        if lo < d.u_position + d.u_height and d.u_position < hi:
            if _faces_collide(d.face, candidate.face):
                out.append(d)
    return out


def check_placement(
    rack: Rack,
    devices: Iterable[RackDevice],
    candidate: RackDevice,
    exclude_id: int | None = None,
) -> None:
    """Raise 422 on out-of-bounds placement, 409 on a face collision."""
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
    """Distinct U slots occupied on either face (front+rear pair counts once)."""
    slots: set[int] = set()
    for d in devices:
        slots.update(range(d.u_position, d.u_position + d.u_height))
    return len(slots)


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
