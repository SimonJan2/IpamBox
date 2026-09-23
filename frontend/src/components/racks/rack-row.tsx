"use client";

/** Bayed-row rendering: one rack column inside a group's horizontal strip.
 *
 *  Drawing reuses the RackElevation primitives (grid, blocks, carrier
 *  frames, slot rects) so a row looks identical to the detail view. In edit
 *  mode the whole strip shares ONE DndContext (owned by the group page), so
 *  a device dragged sideways lands on another rack's U row — the PATCH then
 *  carries rack_id + u_position. No cross-rack carrier-slot drops: mounted
 *  children dragged to a U row unmount, same as the single-rack editor. */
import Link from "next/link";
import { useDroppable, useDraggable } from "@dnd-kit/core";

import { cn } from "@/lib/utils";
import { deviceSums, formatKg, formatWatts } from "@/lib/rack-capacity";
import { freeSlots } from "@/lib/rack-collision";
import type { RackDevice, RackDetail } from "@/types";
import {
  CarrierFrameSvg,
  DeviceBlockSvg,
  deviceImage,
  RackUGrid,
  rackGeom,
  slotRect,
  useLibraryBySlug,
  usedUSlots,
  type RackGeom,
  type SlotRect,
} from "@/components/racks/rack-elevation";

/** Droppable id for a U row inside a rack column — "row:<rackId>:<u>". */
export function rowDropId(rackId: number, u: number): string {
  return `row:${rackId}:${u}`;
}

export function parseRowDrop(
  id: unknown
): { rackId: number; u: number } | null {
  if (typeof id !== "string" || !id.startsWith("row:")) return null;
  const [, r, u] = id.split(":");
  const rackId = Number(r);
  const pos = Number(u);
  return Number.isInteger(rackId) && Number.isInteger(pos)
    ? { rackId, u: pos }
    : null;
}

/** Draggable id for a device block — "dev:<id>" stays distinct from row ids. */
export function rowDevId(id: number): string {
  return `dev:${id}`;
}

export function parseRowDev(id: unknown): number | null {
  if (typeof id !== "string" || !id.startsWith("dev:")) return null;
  const n = Number(id.slice(4));
  return Number.isInteger(n) ? n : null;
}

/** Free start-Us for `d` inside every rack of the strip — powers the
 *  per-column drop tint during a drag. Keyed by rack id. */
export function freeByRack(
  racks: RackDetail[],
  d: Pick<RackDevice, "id" | "u_height" | "face">
): Map<number, Set<number>> {
  const m = new Map<number, Set<number>>();
  for (const r of racks) {
    m.set(r.id, freeSlots(r.devices, r.height_u, d.u_height, d.face, d.id));
  }
  return m;
}

/** One U-row drop target inside a column (edit mode only). */
function RowDropRow({
  rackId,
  u,
  geom,
  tint,
}: {
  rackId: number;
  u: number;
  geom: RackGeom;
  tint: "free" | "blocked" | null;
}) {
  const { setNodeRef, isOver } = useDroppable({ id: rowDropId(rackId, u) });
  return (
    <rect
      ref={(el) => setNodeRef(el as unknown as HTMLElement)}
      x={geom.NUM_W}
      y={geom.uTop(u) + 1}
      width={geom.W - geom.NUM_W - 4}
      height={geom.U - 2}
      rx={2}
      className={cn(
        "transition-colors",
        tint === null
          ? "fill-transparent"
          : tint === "free"
            ? "fill-emerald-500/15"
            : "fill-rose-500/10",
        isOver && tint === "free" && "fill-emerald-500/30",
        isOver && tint === "blocked" && "fill-rose-500/25"
      )}
    />
  );
}

/** A device block wired for the strip: draggable only in edit mode; in view
 *  mode a click jumps to the owning rack's detail page. */
function RowDevice({
  d,
  rackId,
  geom,
  health,
  edit,
  rect,
  compact = false,
  image,
  onOpenRack,
}: {
  d: RackDevice;
  rackId: number;
  geom: RackGeom;
  health: boolean;
  edit: boolean;
  rect?: SlotRect;
  compact?: boolean;
  image?: string;
  onOpenRack: (rackId: number, deviceId: number) => void;
}) {
  const { attributes, listeners, setNodeRef, isDragging } = useDraggable({
    id: rowDevId(d.id),
    disabled: !edit,
  });
  const top = d.u_position + d.u_height - 1;
  const label = `${d.name} — U${d.u_position}${d.u_height > 1 ? `–${top}` : ""}, ${d.face}`;
  const shared = {
    d,
    geom,
    u: undefined,
    ghost: (isDragging ? "drag" : null) as "drag" | null,
    ref: (el: SVGGElement | null) => setNodeRef(el as unknown as HTMLElement),
    ...(edit ? { ...attributes, ...listeners } : {}),
    onClick: () => {
      if (!edit) onOpenRack(rackId, d.id);
    },
    className: cn(
      "outline-none",
      edit ? "cursor-grab touch-none active:cursor-grabbing" : "cursor-pointer"
    ),
    role: "button" as const,
    "aria-label": edit ? `${label}. Drag sideways to move between racks.` : label,
  };
  return d.slot_layout != null ? (
    <CarrierFrameSvg {...shared} />
  ) : (
    <DeviceBlockSvg
      {...shared}
      health={health}
      rect={rect}
      compact={compact}
      image={image}
    />
  );
}

/** One rack column: name link + occupancy/power line + the elevation svg.
 *  Bottom-aligned by the strip's `items-end` so tall and short racks stand
 *  on the same floor line, like a real bayed row. */
export function RackRowColumn({
  rack,
  view,
  health,
  edit,
  tint,
  onOpenRack,
}: {
  rack: RackDetail;
  view: "front" | "rear";
  health: boolean;
  edit: boolean;
  /** Per-U tint during a drag — null outside a drag session. */
  tint: Set<number> | null;
  onOpenRack: (rackId: number, deviceId: number) => void;
}) {
  const libBySlug = useLibraryBySlug();
  const geom = rackGeom(rack.height_u);
  const visible = rack.devices.filter(
    (d) => d.face === "both" || d.face === view
  );
  const carriers = new Map(
    visible.filter((d) => d.slot_layout != null).map((d) => [d.id, d])
  );
  const topLevel = visible.filter((d) => d.carrier_id == null);
  const slotted = visible.filter(
    (d) => d.carrier_id != null && carriers.has(d.carrier_id)
  );
  const sums = deviceSums(rack.devices);
  // Recomputed from live devices so optimistic cross-rack moves repaint
  // immediately rather than waiting on a refetch.
  const usedU = usedUSlots(rack.devices);

  return (
    <div className="w-60 shrink-0 space-y-2">
      <div className="min-w-0 px-0.5">
        <Link
          href={`/racks/${rack.id}`}
          className="block truncate font-medium text-emerald-400 hover:underline"
          dir="auto"
        >
          {rack.name}
        </Link>
        <div className="truncate text-xs text-muted-foreground">
          {usedU}/{rack.height_u}U
          {sums.watts != null && ` · Σ ${formatWatts(sums.watts)}`}
          {sums.kg != null && ` · ${formatKg(sums.kg)}`}
          {rack.group_position != null && ` · #${rack.group_position}`}
        </div>
      </div>
      <svg
        viewBox={`0 0 ${geom.W} ${geom.H}`}
        className="w-full rounded-lg border bg-card"
        role="img"
        aria-label={`${view} elevation of ${rack.name}`}
      >
        <RackUGrid heightU={rack.height_u} geom={geom} />
        {edit &&
          Array.from({ length: rack.height_u }, (_, i) => i + 1).map((u) => (
            <RowDropRow
              key={u}
              rackId={rack.id}
              u={u}
              geom={geom}
              tint={tint === null ? null : tint.has(u) ? "free" : "blocked"}
            />
          ))}
        {topLevel.map((d) => (
          <RowDevice
            key={d.id}
            d={d}
            rackId={rack.id}
            geom={geom}
            health={health}
            edit={edit}
            image={deviceImage(d, view, libBySlug)}
            onOpenRack={onOpenRack}
          />
        ))}
        {slotted.map((d) => {
          const carrier = carriers.get(d.carrier_id!)!;
          return (
            <RowDevice
              key={d.id}
              d={d}
              rackId={rack.id}
              geom={geom}
              health={health}
              edit={edit}
              compact
              image={deviceImage(d, view, libBySlug)}
              rect={slotRect(geom, carrier, d.slot ?? 0)}
              onOpenRack={onOpenRack}
            />
          );
        })}
      </svg>
    </div>
  );
}
