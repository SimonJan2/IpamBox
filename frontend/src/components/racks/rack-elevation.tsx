"use client";

import { useEffect, useMemo, useState, type ComponentProps } from "react";

import { cn } from "@/lib/utils";
import { STATUS_TOKENS } from "@/lib/status-tokens";
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
  /** SVG y of a device block whose span starts at `pos` and is `h` U tall. */
  const blockY = (pos: number, h: number) => uTop(pos + h) + 1;
  return { U, NUM_W, W, H, uTop, blockY };
}
export type RackGeom = ReturnType<typeof rackGeom>;

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
} & Omit<ComponentProps<"g">, "d">) {
  const pos = u ?? d.u_position;
  const f = face ?? d.face;
  const y = geom.blockY(pos, d.u_height);
  const h = d.u_height * geom.U - 2;
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
        x={geom.NUM_W + 2}
        y={y}
        width={geom.W - geom.NUM_W - 8}
        height={h}
        rx={2}
        fill={fill}
        fillOpacity={ghost === "drag" ? 0.35 : f === "both" ? 1 : 0.85}
        className={cn("transition-all", stroke)}
        strokeWidth={ghost || selected ? 2 : focused ? 1.5 : 0.5}
        strokeDasharray={ghost === "ok" || ghost === "bad" ? "4 2" : undefined}
      />
      {health && (
        <circle
          cx={geom.NUM_W + 9}
          cy={y + Math.min(9, h / 2)}
          r={3}
          className={cn(
            "pointer-events-none",
            d.ip_status
              ? STATUS_TOKENS[d.ip_status].dotFill
              : "fill-muted-foreground/40"
          )}
        />
      )}
      <text
        x={geom.NUM_W + 2 + (geom.W - geom.NUM_W - 8) / 2}
        y={y + h / 2}
        textAnchor="middle"
        dominantBaseline="central"
        fill={fg}
        fontSize={Math.min(11, Math.max(8, geom.U * 0.5))}
        className="pointer-events-none select-none"
      >
        {label}
      </text>
      <text
        x={geom.W - 12}
        y={y + Math.min(9, h / 2)}
        textAnchor="end"
        dominantBaseline="central"
        fill={fg}
        fillOpacity={0.75}
        fontSize={8}
        className="pointer-events-none select-none"
      >
        {FACE_BADGE[f]}
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

        {visible.map((d) => {
          const selected = d.id === selectedId;
          const top = d.u_position + d.u_height - 1;
          return (
            <DeviceBlockSvg
              key={d.id}
              d={d}
              geom={geom}
              health={health}
              selected={selected}
              onClick={() => onSelect?.(selected ? null : d)}
              className={onSelect ? "cursor-pointer" : undefined}
              role={onSelect ? "button" : undefined}
              aria-label={`${d.name} — U${d.u_position}${d.u_height > 1 ? `–${top}` : ""}, ${d.face}`}
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
