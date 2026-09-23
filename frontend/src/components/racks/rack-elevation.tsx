"use client";

import {
  useEffect,
  useId,
  useMemo,
  useState,
  type ComponentProps,
} from "react";

import { cn } from "@/lib/utils";
import { STATUS_TOKENS } from "@/lib/status-tokens";
import { slotLabel } from "@/lib/rack-collision";
import {
  libraryBySlug,
  libraryImage,
  loadRackLibrary,
  type LibraryDevice,
} from "@/lib/rack-library";
import { useAsyncData } from "@/lib/use-async-data";
import type { IpStatus, RackDevice, RackFace } from "@/types";

export const FACE_BADGE: Record<RackFace, string> = { front: "F", rear: "R", both: "F+R" };

/** Saved UI pref for the health overlay — same `ipambox:` key namespace as
 *  the tree-expansion state. */
export const HEALTH_KEY = "ipambox:rack-health";

/** Readable label color over a device's fill colour. */
export function textOn(hex: string | null): string {
  const m = /^#([0-9a-f]{6})$/i.exec(hex ?? "");
  if (!m) return "#f8fafc";
  const v = parseInt(m[1], 16);
  const lum = (0.2126 * ((v >> 16) & 255) + 0.7152 * ((v >> 8) & 255) + 0.0722 * (v & 255)) / 255;
  return lum > 0.55 ? "#0f172a" : "#f8fafc";
}

/** Distinct U slots occupied on either face (front+rear pair counts once). */
export function usedUSlots(devices: Pick<RackDevice, "u_position" | "u_height">[]): number {
  const slots = new Set<number>();
  for (const d of devices) {
    for (let u = d.u_position; u < d.u_position + d.u_height; u++) slots.add(u);
  }
  return slots.size;
}

/** Elevation geometry shared by the read-only view and the editor. U1 sits
 *  at the bottom; every row is `U` px tall inside a `W x H` viewBox. */
export function rackGeom(heightU: number) {
  const U = Math.min(24, Math.max(10, Math.floor(880 / Math.max(heightU, 1))));
  const NUM_W = 30;
  const W = NUM_W + 240;
  const H = heightU * U + 8;
  /** SVG y of the TOP edge of row `u`. */
  const uTop = (u: number) => H - 4 - u * U;
  /** SVG y of a device block whose span starts at `pos` and is `h` U tall.
   *  The block's top edge is the top edge of its topmost row (pos+h-1). */
  const blockY = (pos: number, h: number) => uTop(pos + h - 1) + 1;
  return { U, NUM_W, W, H, uTop, blockY };
}
export type RackGeom = ReturnType<typeof rackGeom>;

export interface SlotRect {
  x: number;
  y: number;
  w: number;
  h: number;
}

/** Module-scope hook shared by the elevation + editor: the bundled device
 *  library keyed by slug (manifest load is cached by loadRackLibrary). */
export function useLibraryBySlug(): Map<string, LibraryDevice> {
  const libQ = useAsyncData(loadRackLibrary, []);
  return useMemo(() => libraryBySlug(libQ.data ?? []), [libQ.data]);
}

/** Image URL for a device viewed from `view`, when its `device_type` slug
 *  matches a manifest entry that bundles one. Undefined -> colour block. */
export function deviceImage(
  d: Pick<RackDevice, "device_type">,
  view: "front" | "rear",
  bySlug: Map<string, LibraryDevice>
): string | undefined {
  return libraryImage(d.device_type ? bySlug.get(d.device_type) : undefined, view);
}

/** Sub-rect of a carrier's block for `slot`: halves split left/right,
 *  quarters tile 2×2 (row-major, slot 0 top-left), shelf is the whole block. */
export function slotRect(
  geom: RackGeom,
  carrier: Pick<RackDevice, "u_position" | "u_height" | "slot_layout">,
  slot: number
): SlotRect {
  const x0 = geom.NUM_W + 2;
  const w = geom.W - geom.NUM_W - 8;
  const y = geom.blockY(carrier.u_position, carrier.u_height);
  const h = carrier.u_height * geom.U - 2;
  if (carrier.slot_layout === "halves") {
    return { x: x0 + (slot * w) / 2, y, w: w / 2, h };
  }
  if (carrier.slot_layout === "quarters") {
    const col = slot % 2;
    const row = Math.floor(slot / 2); // row 0 is the top pair
    return { x: x0 + (col * w) / 2, y: y + (row * h) / 2, w: w / 2, h: h / 2 };
  }
  return { x: x0, y, w, h };
}

/** U-number column + row grid lines, bottom-up. */
export function RackUGrid({ heightU, geom }: { heightU: number; geom: RackGeom }) {
  return (
    <>
      {Array.from({ length: heightU }, (_, i) => {
        const u = i + 1;
        const y = geom.uTop(u);
        return (
          <g key={u}>
            <line
              x1={geom.NUM_W}
              x2={geom.W - 4}
              y1={y}
              y2={y}
              className="stroke-border"
              strokeWidth={0.5}
            />
            <text
              x={geom.NUM_W - 4}
              y={y + geom.U / 2}
              textAnchor="end"
              dominantBaseline="central"
              className="fill-muted-foreground"
              fontSize={Math.min(10, geom.U * 0.55)}
            >
              {u}
            </text>
          </g>
        );
      })}
      <line
        x1={geom.NUM_W}
        x2={geom.W - 4}
        y1={geom.H - 4}
        y2={geom.H - 4}
        className="stroke-border"
        strokeWidth={0.5}
      />
    </>
  );
}

/** One placed device: colour block + health dot + name + face badge.
 *  `u`/`face` overrides preview a pending move; `ghost` restyles the block
 *  (dimmed drag source, dashed valid/invalid outline) without changing its
 *  span. Extra props land on the <g> so callers can wire dnd/click/keyboard. */
export function DeviceBlockSvg({
  d,
  geom,
  health,
  selected = false,
  u,
  face,
  ghost = null,
  focused = false,
  rect,
  compact = false,
  image,
  ...gProps
}: {
  d: RackDevice;
  geom: RackGeom;
  health: boolean;
  selected?: boolean;
  /** Preview position — defaults to the device's real u_position. */
  u?: number;
  /** Preview face — defaults to the device's real face. */
  face?: RackFace;
  /** "drag" = dimmed source during a pointer drag; "ok"/"bad" = dashed
   *  validity outline for a pending/ghosted placement. */
  ghost?: "drag" | "ok" | "bad" | null;
  /** Keyboard focus ring (edit mode). */
  focused?: boolean;
  /** Override the block's geometry — carrier children render inside their
   *  slot rect instead of spanning the full block width. */
  rect?: SlotRect;
  /** Slot rendering: tighter label, no face badge (inherited anyway). */
  compact?: boolean;
  /** Bundled product image (`/rack-library/...`) — drawn inside the block
   *  over the colour rect, which stays as backdrop/fallback. */
  image?: string;
} & Omit<ComponentProps<"g">, "d">) {
  // useId's `:r0:` colons break url(#…) fragment refs in some browsers.
  const clipId = useId().replace(/[^a-zA-Z0-9_-]/g, "");
  const pos = u ?? d.u_position;
  const f = face ?? d.face;
  const r = rect ?? {
    x: geom.NUM_W + 2,
    y: geom.blockY(pos, d.u_height),
    w: geom.W - geom.NUM_W - 8,
    h: d.u_height * geom.U - 2,
  };
  const fill = d.colour ?? "#334155";
  const fg = image ? "#f8fafc" : textOn(d.colour);
  const maxChars = compact ? 14 : 30;
  const label =
    d.name.length > maxChars ? `${d.name.slice(0, maxChars - 1)}…` : d.name;
  const fontSize = compact
    ? Math.min(9, Math.max(6.5, geom.U * 0.4))
    : Math.min(11, Math.max(8, geom.U * 0.5));
  /** Name chip over the photo — sized to the (approximate) label box so it
   *  stays readable without hiding more of the image than needed. */
  const chipW = image
    ? Math.min(r.w - 3, label.length * fontSize * 0.58 + 6)
    : 0;
  const chipH = image ? Math.min(r.h - 2, fontSize * 1.45) : 0;
  const stroke = ghost === "bad"
    ? "stroke-rose-400"
    : ghost === "ok" || selected
      ? "stroke-emerald-400"
      : focused
        ? "stroke-sky-400"
        : "stroke-border";
  return (
    <g {...gProps}>
      <rect
        x={r.x}
        y={r.y}
        width={r.w}
        height={r.h}
        rx={2}
        fill={fill}
        fillOpacity={ghost === "drag" ? 0.35 : f === "both" ? 1 : 0.85}
        className={cn("transition-all", stroke)}
        strokeWidth={ghost || selected ? 2 : focused ? 1.5 : 0.5}
        strokeDasharray={ghost === "ok" || ghost === "bad" ? "4 2" : undefined}
      />
      {image && (
        <>
          <clipPath id={clipId}>
            <rect x={r.x} y={r.y} width={r.w} height={r.h} rx={2} />
          </clipPath>
          <image
            href={image}
            x={r.x}
            y={r.y}
            width={r.w}
            height={r.h}
            preserveAspectRatio="xMidYMid meet"
            clipPath={`url(#${clipId})`}
            opacity={ghost === "drag" ? 0.35 : 1}
            className="pointer-events-none select-none"
          />
        </>
      )}
      {health && (
        <circle
          cx={r.x + (compact ? 6 : 7)}
          cy={r.y + Math.min(compact ? 6 : 9, r.h / 2)}
          r={compact ? 2 : 3}
          className={cn(
            "pointer-events-none",
            d.ip_status
              ? STATUS_TOKENS[d.ip_status].dotFill
              : "fill-muted-foreground/40"
          )}
        />
      )}
      {image && (
        <rect
          x={r.x + (r.w - chipW) / 2}
          y={r.y + (r.h - chipH) / 2}
          width={chipW}
          height={chipH}
          rx={2}
          fill="#0f172a"
          fillOpacity={0.62}
          className="pointer-events-none"
        />
      )}
      <text
        x={r.x + r.w / 2}
        y={r.y + r.h / 2}
        textAnchor="middle"
        dominantBaseline="central"
        fill={fg}
        fontSize={fontSize}
        className="pointer-events-none select-none"
      >
        {label}
      </text>
      {!compact && (
        <text
          x={geom.W - 12}
          y={r.y + Math.min(9, r.h / 2)}
          textAnchor="end"
          dominantBaseline="central"
          fill={fg}
          fillOpacity={0.75}
          fontSize={8}
          className="pointer-events-none select-none"
        >
          {FACE_BADGE[f]}
        </text>
      )}
    </g>
  );
}

/** A carrier tray's frame: the device block itself (muted — children get the
 *  spotlight) plus slot divider lines. Children render on top as sibling
 *  blocks positioned by slotRect. Accepts the same interaction props as
 *  DeviceBlockSvg so the editor can drag/select/ghost it as one unit. */
export function CarrierFrameSvg({
  d,
  geom,
  selected = false,
  u,
  ghost = null,
  focused = false,
  ...gProps
}: {
  d: RackDevice;
  geom: RackGeom;
  selected?: boolean;
  u?: number;
  ghost?: "drag" | "ok" | "bad" | null;
  focused?: boolean;
} & Omit<ComponentProps<"g">, "d">) {
  const pos = u ?? d.u_position;
  const r = {
    x: geom.NUM_W + 2,
    y: geom.blockY(pos, d.u_height),
    w: geom.W - geom.NUM_W - 8,
    h: d.u_height * geom.U - 2,
  };
  const fill = d.colour ?? "#334155";
  const fg = textOn(d.colour);
  const label = d.name.length > 30 ? `${d.name.slice(0, 29)}…` : d.name;
  const stroke = ghost === "bad"
    ? "stroke-rose-400"
    : ghost === "ok" || selected
      ? "stroke-emerald-400"
      : focused
        ? "stroke-sky-400"
        : "stroke-border";
  return (
    <g {...gProps}>
      <rect
        x={r.x}
        y={r.y}
        width={r.w}
        height={r.h}
        rx={2}
        fill={fill}
        fillOpacity={ghost === "drag" ? 0.15 : 0.35}
        className={cn("transition-all", stroke)}
        strokeWidth={ghost || selected ? 2 : focused ? 1.5 : 0.5}
        strokeDasharray={ghost === "ok" || ghost === "bad" ? "4 2" : undefined}
      />
      {d.slot_layout === "halves" && (
        <line
          x1={r.x + r.w / 2}
          x2={r.x + r.w / 2}
          y1={r.y}
          y2={r.y + r.h}
          className="stroke-border"
          strokeWidth={0.5}
        />
      )}
      {d.slot_layout === "quarters" && (
        <>
          <line
            x1={r.x + r.w / 2}
            x2={r.x + r.w / 2}
            y1={r.y}
            y2={r.y + r.h}
            className="stroke-border"
            strokeWidth={0.5}
          />
          <line
            x1={r.x}
            x2={r.x + r.w}
            y1={r.y + r.h / 2}
            y2={r.y + r.h / 2}
            className="stroke-border"
            strokeWidth={0.5}
          />
        </>
      )}
      <text
        x={r.x + r.w / 2}
        y={r.y + r.h / 2}
        textAnchor="middle"
        dominantBaseline="central"
        fill={fg}
        fillOpacity={0.8}
        fontSize={Math.min(10, Math.max(7, geom.U * 0.45))}
        className="pointer-events-none select-none"
      >
        {label}
      </text>
    </g>
  );
}

/**
 * Read-only SVG rack elevation. U1 is at the bottom; devices render as
 * colour blocks with centered name labels and a face badge. The front/rear
 * toggle filters which face's gear is drawn — no editing here by design.
 *
 * The Health toggle (persisted) overlays the linked IP's scan status as a
 * dot on each block, using the same STATUS_TOKENS palette as the addresses
 * table. `forceView` pins a face and swaps the title — the print view uses
 * it to render front and rear side by side.
 */
export function RackElevation({
  name,
  heightU,
  devices,
  selectedId = null,
  onSelect,
  forceView,
}: {
  name: string;
  heightU: number;
  devices: RackDevice[];
  selectedId?: number | null;
  onSelect?: (d: RackDevice | null) => void;
  forceView?: "front" | "rear";
}) {
  const [view, setView] = useState<"front" | "rear">("front");
  const effView = forceView ?? view;
  const [health, setHealth] = useState(true);
  const libBySlug = useLibraryBySlug();
  useEffect(() => {
    try {
      if (localStorage.getItem(HEALTH_KEY) === "0") setHealth(false);
    } catch {}
  }, []);
  const toggleHealth = () =>
    setHealth((h) => {
      const next = !h;
      try {
        localStorage.setItem(HEALTH_KEY, next ? "1" : "0");
      } catch {}
      return next;
    });
  const visible = useMemo(
    () => devices.filter((d) => d.face === "both" || d.face === effView),
    [devices, effView]
  );
  // Children ride inside their carrier's block — they draw in their slot,
  // and only when the carrier itself is visible on this face.
  const carriers = useMemo(
    () =>
      new Map(
        visible.filter((d) => d.slot_layout != null).map((d) => [d.id, d])
      ),
    [visible]
  );
  const topLevel = useMemo(
    () => visible.filter((d) => d.carrier_id == null),
    [visible]
  );
  const slotted = useMemo(
    () =>
      visible.filter(
        (d) => d.carrier_id != null && carriers.has(d.carrier_id)
      ),
    [visible, carriers]
  );
  const usedU = usedUSlots(devices);
  const geom = rackGeom(heightU);

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between gap-2">
        <div className="min-w-0">
          <span dir="auto" className="font-medium">
            {forceView ? `${forceView} face` : name}
          </span>
          <span className="ml-2 text-sm text-muted-foreground">
            {usedU}/{heightU}U used
          </span>
        </div>
        <div className="flex items-center gap-2 print:hidden">
          <button
            type="button"
            aria-pressed={health}
            onClick={toggleHealth}
            title="Overlay linked-IP scan health"
            className={cn(
              "rounded-lg border px-3 py-1 text-sm transition-colors",
              health
                ? "border-emerald-500/40 bg-emerald-500/15 text-emerald-400"
                : "text-muted-foreground hover:text-foreground"
            )}
          >
            Health
          </button>
          {!forceView && (
            <div role="group" aria-label="Rack face" className="flex rounded-lg border p-0.5">
              {(["front", "rear"] as const).map((v) => (
                <button
                  key={v}
                  type="button"
                  onClick={() => setView(v)}
                  className={cn(
                    "rounded-md px-3 py-1 text-sm capitalize transition-colors",
                    view === v
                      ? "bg-emerald-500/15 text-emerald-400"
                      : "text-muted-foreground hover:text-foreground"
                  )}
                >
                  {v}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      <svg
        viewBox={`0 0 ${geom.W} ${geom.H}`}
        className="w-full max-w-sm rounded-lg border bg-card"
        role="img"
        aria-label={`${effView} elevation of ${name}`}
      >
        <RackUGrid heightU={heightU} geom={geom} />

        {topLevel.map((d) => {
          const selected = d.id === selectedId;
          const top = d.u_position + d.u_height - 1;
          const label = `${d.name} — U${d.u_position}${d.u_height > 1 ? `–${top}` : ""}, ${d.face}`;
          return d.slot_layout != null ? (
            <CarrierFrameSvg
              key={d.id}
              d={d}
              geom={geom}
              selected={selected}
              onClick={() => onSelect?.(selected ? null : d)}
              className={onSelect ? "cursor-pointer" : undefined}
              role={onSelect ? "button" : undefined}
              aria-label={`${label} — carrier (${d.slot_layout})`}
            />
          ) : (
            <DeviceBlockSvg
              key={d.id}
              d={d}
              geom={geom}
              health={health}
              selected={selected}
              image={deviceImage(d, effView, libBySlug)}
              onClick={() => onSelect?.(selected ? null : d)}
              className={onSelect ? "cursor-pointer" : undefined}
              role={onSelect ? "button" : undefined}
              aria-label={label}
            />
          );
        })}

        {slotted.map((d) => {
          const carrier = carriers.get(d.carrier_id!)!;
          return (
            <DeviceBlockSvg
              key={d.id}
              d={d}
              geom={geom}
              health={health}
              selected={d.id === selectedId}
              compact
              image={deviceImage(d, effView, libBySlug)}
              rect={slotRect(geom, carrier, d.slot ?? 0)}
              onClick={() => onSelect?.(d.id === selectedId ? null : d)}
              className={onSelect ? "cursor-pointer" : undefined}
              role={onSelect ? "button" : undefined}
              aria-label={`${d.name} — ${carrier.name} ${slotLabel(carrier.slot_layout, d.slot ?? 0)}`}
            />
          );
        })}
      </svg>

      {health && (
        <div className="flex max-w-sm flex-wrap gap-x-3 gap-y-1 text-xs text-muted-foreground">
          {(Object.keys(STATUS_TOKENS) as IpStatus[]).map((s) => (
            <span key={s} className="inline-flex items-center gap-1">
              <span className={cn("h-2 w-2 rounded-full", STATUS_TOKENS[s].dot)} />
              {s}
            </span>
          ))}
          <span className="inline-flex items-center gap-1">
            <span className="h-2 w-2 rounded-full bg-muted-foreground/40" />
            unmonitored
          </span>
        </div>
      )}
    </div>
  );
}
