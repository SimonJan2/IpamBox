import type { IpStatus } from "@/types";

/** Badge variant names used for IP statuses (subset of ui/badge variants). */
type StatusBadgeVariant = "default" | "amber" | "violet" | "cyan" | "zinc";

export interface StatusTokenSet {
  /** Small round dot (filter panel, result lists). */
  dot: string;
  /**
   * Subnet-grid cell surface for a used address. These are the `.ipcell-*`
   * classes defined in globals.css — theme-aware via
   * `:root[data-theme="light"]` overrides, so both themes stay legible.
   */
  cell: string;
  /** `<Badge>` variant for this status. */
  badge: StatusBadgeVariant;
  /**
   * Non-color corner glyph rendered on subnet-grid cells (and the legend),
   * so status is never conveyed by color alone.
   */
  glyph: string;
}

/**
 * Single source of truth for IP-status colors (UX-16). Typed on the IpStatus
 * union — adding a new status is a compile error until every surface is
 * updated here.
 */
export const STATUS_TOKENS: Record<IpStatus, StatusTokenSet> = {
  active: {
    dot: "bg-emerald-500/70",
    cell: "ipcell-active",
    badge: "default",
    glyph: "●",
  },
  reserved: {
    dot: "bg-amber-500/70",
    cell: "ipcell-reserved",
    badge: "amber",
    glyph: "◆",
  },
  dhcp: {
    dot: "bg-cyan-500/70",
    cell: "ipcell-dhcp",
    badge: "cyan",
    glyph: "≈",
  },
  discovered: {
    dot: "bg-violet-500/70",
    cell: "ipcell-discovered",
    badge: "violet",
    glyph: "✦",
  },
  offline: {
    dot: "bg-zinc-500/70",
    cell: "ipcell-offline",
    badge: "zinc",
    glyph: "✕",
  },
};

/** Grid cells that carry no IpStatus — same `.ipcell-*` theme-aware classes.
 *  `label` feeds the grid legend; boundary/range are already encoded
 *  non-chromatically (stripe pattern / dashed border) so they need no glyph. */
export const GRID_CELL_TOKENS: Record<
  "free" | "boundary" | "range",
  { cell: string; label: string }
> = {
  free: { cell: "ipcell-free", label: "free" },
  boundary: { cell: "ipcell-boundary", label: "network/broadcast" },
  range: { cell: "ipcell-range", label: "ip range" },
};
