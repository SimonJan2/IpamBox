/** Client-side mirror of backend/app/services/racks.py — placement_conflicts
 *  and check_placement. THE TWO MUST STAY IN SYNC: the backend remains the
 *  source of truth for validation; these pure functions only drive editor UX
 *  (drop-slot tinting, keyboard-move gating). A 409/422 from PATCH always
 *  wins and rolls the optimistic move back. */

import type { RackFace, SlotLayout } from "@/types";

/** Carrier layouts -> slot count. Mirrors SLOT_LAYOUTS on the backend. */
export const SLOT_LAYOUTS: Record<SlotLayout, number> = {
  halves: 2,
  quarters: 4,
  shelf: 1,
};

export function slotCount(layout: SlotLayout | null | undefined): number {
  return layout ? (SLOT_LAYOUTS[layout] ?? 0) : 0;
}

/** Any placed (or placeable) rack device — RackDevice satisfies this. */
export interface Placed {
  id: number;
  u_position: number;
  u_height: number;
  face: RackFace;
  carrier_id?: number | null;
  slot?: number | null;
  slot_layout?: SlotLayout | null;
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

/** Existing devices colliding with `cand`. `cand.id` doubles as the backend's
 *  exclude_id — the moved device never conflicts with itself.
 *
 *  Carrier rules (mirrors the backend): a mounted child collides only with
 *  siblings in the same (carrier_id, slot); rack-level candidates never see
 *  children — the carrier already reserved the span. */
export function conflicts<T extends Placed>(devices: T[], cand: Placed): T[] {
  return devices.filter((d) => {
    if (d.id === cand.id) return false;
    if (cand.carrier_id != null) {
      return d.carrier_id === cand.carrier_id && d.slot === cand.slot;
    }
    return (
      d.carrier_id == null &&
      rangesOverlap(d, cand) &&
      facesCollide(d.face, cand.face)
    );
  });
}

/** In-bounds AND collision-free — the same gate check_placement applies.
 *  (For a mounted child, u_position is the carrier's own — bounds were
 *  already proven when the carrier was placed.) */
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

/** May `cand` mount into `carrier`'s `slot`? Single level (carriers can't
 *  nest), child no taller than its carrier, one child per slot. */
export function canMount<T extends Placed>(
  devices: T[],
  carrier: T,
  slot: number,
  cand: Placed
): boolean {
  if (cand.id === carrier.id || cand.slot_layout) return false;
  if (cand.u_height > carrier.u_height) return false;
  if (slot < 0 || slot >= slotCount(carrier.slot_layout)) return false;
  return !devices.some(
    (d) => d.id !== cand.id && d.carrier_id === carrier.id && d.slot === slot
  );
}

/** Droppable ids for carrier slots — kept distinct from numeric U-row ids. */
export function slotDropId(carrierId: number, slot: number): string {
  return `slot:${carrierId}:${slot}`;
}

export function parseSlotDrop(
  id: unknown
): { carrierId: number; slot: number } | null {
  if (typeof id !== "string" || !id.startsWith("slot:")) return null;
  const [, c, s] = id.split(":");
  const carrierId = Number(c);
  const slot = Number(s);
  return Number.isInteger(carrierId) && Number.isInteger(slot)
    ? { carrierId, slot }
    : null;
}

/** Human slot label — halves are left/right, quarters numbered, shelf = tray. */
export function slotLabel(layout: SlotLayout | null | undefined, slot: number): string {
  if (layout === "halves") return slot === 0 ? "left" : "right";
  if (layout === "shelf") return "tray";
  return `slot ${slot + 1}`;
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
