"use client";

import { useEffect, useMemo, useState } from "react";

import { cn } from "@/lib/utils";
import { STATUS_TOKENS } from "@/lib/status-tokens";
import type { IpStatus, RackDevice, RackFace } from "@/types";

const FACE_BADGE: Record<RackFace, string> = { front: "F", rear: "R", both: "F+R" };

/** Saved UI pref for the health overlay — same `ipambox:` key namespace as
 *  the tree-expansion state. */
const HEALTH_KEY = "ipambox:rack-health";

/** Readable label color over a device's fill colour. */
function textOn(hex: string | null): string {
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

  const U = Math.min(24, Math.max(10, Math.floor(880 / Math.max(heightU, 1))));
  const NUM_W = 30;
  const W = NUM_W + 240;
  const H = heightU * U + 8;

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
        viewBox={`0 0 ${W} ${H}`}
        className="w-full max-w-sm rounded-lg border bg-card"
        role="img"
        aria-label={`${effView} elevation of ${name}`}
      >
        {/* U grid + numbers, bottom-up */}
        {Array.from({ length: heightU }, (_, i) => {
          const u = i + 1;
          const y = H - 4 - u * U;
          return (
            <g key={u}>
              <line
                x1={NUM_W}
                x2={W - 4}
                y1={y}
                y2={y}
                className="stroke-border"
                strokeWidth={0.5}
              />
              <text
                x={NUM_W - 4}
                y={y + U / 2}
                textAnchor="end"
                dominantBaseline="central"
                className="fill-muted-foreground"
                fontSize={Math.min(10, U * 0.55)}
              >
                {u}
              </text>
            </g>
          );
        })}
        <line
          x1={NUM_W}
          x2={W - 4}
          y1={H - 4}
          y2={H - 4}
          className="stroke-border"
          strokeWidth={0.5}
        />

        {visible.map((d) => {
          const top = d.u_position + d.u_height - 1;
          const y = H - 4 - (top + 1) * U + 1;
          const h = d.u_height * U - 2;
          const fill = d.colour ?? "#334155";
          const fg = textOn(d.colour);
          const selected = d.id === selectedId;
          const label =
            d.name.length > 30 ? `${d.name.slice(0, 29)}…` : d.name;
          return (
            <g
              key={d.id}
              onClick={() => onSelect?.(selected ? null : d)}
              className={onSelect ? "cursor-pointer" : undefined}
              role={onSelect ? "button" : undefined}
              aria-label={`${d.name} — U${d.u_position}${d.u_height > 1 ? `–${top}` : ""}, ${d.face}`}
            >
              <rect
                x={NUM_W + 2}
                y={y}
                width={W - NUM_W - 8}
                height={h}
                rx={2}
                fill={fill}
                fillOpacity={d.face === "both" ? 1 : 0.85}
                className={cn(
                  "stroke-border transition-all",
                  selected && "stroke-emerald-400"
                )}
                strokeWidth={selected ? 2 : 0.5}
              />
              {health && (
                <circle
                  cx={NUM_W + 9}
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
                x={NUM_W + 2 + (W - NUM_W - 8) / 2}
                y={y + h / 2}
                textAnchor="middle"
                dominantBaseline="central"
                fill={fg}
                fontSize={Math.min(11, Math.max(8, U * 0.5))}
                className="pointer-events-none select-none"
              >
                {label}
              </text>
              <text
                x={W - 12}
                y={y + Math.min(9, h / 2)}
                textAnchor="end"
                dominantBaseline="central"
                fill={fg}
                fillOpacity={0.75}
                fontSize={8}
                className="pointer-events-none select-none"
              >
                {FACE_BADGE[d.face]}
              </text>
            </g>
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
