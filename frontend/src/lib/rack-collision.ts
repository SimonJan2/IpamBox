/** Client-side mirror of backend/app/services/racks.py — placement_conflicts
 *  and check_placement. THE TWO MUST STAY IN SYNC: the backend remains the
 *  source of truth for validation; these pure functions only drive editor UX
 *  (drop-slot tinting, keyboard-move gating). A 409/422 from PATCH always
 *  wins and rolls the optimistic move back. */

import type { RackFace } from "@/types";

/** Any placed (or placeable) rack device — RackDevice satisfies this. */
export interface Placed {
  id: number;
  u_position: number;
  u_height: number;
  face: RackFace;
}

/** Spans [u_position, u_position + u_height) overlap. */
export function rangesOverlap(a: Placed, b: Placed): boolean {
  return (
    a.u_position < b.u_position + b.u_height &&
    b.u_position < a.u_position + a.u_height
  );
}

/** `both` collides with everything; equal faces collide; front/rear never do. */
export function facesCollide(a: RackFace, b: RackFace): boolean {
  return a === "both" || b === "both" || a === b;
}

/** Existing devices colliding with `cand` (span + face). `cand.id` doubles as
 *  the backend's exclude_id — the moved device never conflicts with itself. */
export function conflicts<T extends Placed>(devices: T[], cand: Placed): T[] {
  return devices.filter(
    (d) =>
      d.id !== cand.id && rangesOverlap(d, cand) && facesCollide(d.face, cand.face)
  );
}

/** In-bounds AND collision-free — the same gate check_placement applies. */
export function canPlace(
  devices: Placed[],
  cand: Placed,
  heightU: number
): boolean {
  const top = cand.u_position + cand.u_height - 1;
  return (
    cand.u_position >= 1 && top <= heightU && conflicts(devices, cand).length === 0
  );
}

/** Every legal start-U for a `height`-U `face` device — powers the drop
 *  highlight. `excludeId` mirrors the backend's exclude_id (the device being
 *  moved); omitted, no device is skipped. */
export function freeSlots(
  devices: Placed[],
  heightU: number,
  height: number,
  face: RackFace,
  excludeId?: number
): Set<number> {
  const out = new Set<number>();
  for (let u = 1; u + height - 1 <= heightU; u++) {
    const cand: Placed = {
      id: excludeId ?? -1,
      u_position: u,
      u_height: height,
      face,
    };
    if (conflicts(devices, cand).length === 0) out.add(u);
  }
  return out;
}
