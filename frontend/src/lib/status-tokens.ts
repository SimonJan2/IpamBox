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
  },
  reserved: {
    dot: "bg-amber-500/70",
    cell: "ipcell-reserved",
    badge: "amber",
  },
  dhcp: {
    dot: "bg-cyan-500/70",
    cell: "ipcell-dhcp",
    badge: "cyan",
  },
  discovered: {
    dot: "bg-violet-500/70",
    cell: "ipcell-discovered",
    badge: "violet",
  },
  offline: {
    dot: "bg-zinc-500/70",
    cell: "ipcell-offline",
    badge: "zinc",
  },
};

/** Grid cells that carry no IpStatus — same `.ipcell-*` theme-aware classes. */
export const GRID_CELL_TOKENS = {
  free: "ipcell-free",
  boundary: "ipcell-boundary",
  range: "ipcell-range",
} as const;
