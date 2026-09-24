"use client";

import type { ReactNode } from "react";
import { Check, X } from "lucide-react";

import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";

/** Shared building blocks for the entity filter panels
 *  (device-filter-panel / rack-filter-panel) — the AddressFilterPanel
 *  look: pill toggles with live counts, check rows, removable chips. */

export function FacetSection({
  label,
  children,
}: {
  label: string;
  children: ReactNode;
}) {
  return (
    <div>
      <div className="mb-1.5 text-xs font-medium text-muted-foreground">
        {label}
      </div>
      {children}
    </div>
  );
}

/** Round toggle pill with an optional status dot and a live count. */
export function FacetPill({
  on,
  onClick,
  dot,
  count,
  children,
}: {
  on: boolean;
  onClick: () => void;
  dot?: string;
  count?: number;
  children: ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      aria-pressed={on}
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border px-2 py-0.5 text-xs transition-colors",
        on
          ? "border-foreground/40 bg-accent text-foreground"
          : "border-transparent text-muted-foreground hover:bg-accent/50"
      )}
    >
      {dot !== undefined && (
        <i className={cn("h-2 w-2 rounded-full", dot)} />
      )}
      {children}
      {count !== undefined && (
        <span className="text-muted-foreground">{count}</span>
      )}
    </button>
  );
}

/** Full-width option row — check on the active entry, count at the end. */
export function FacetOption({
  on,
  dim,
  onClick,
  count,
  italic,
  children,
}: {
  on: boolean;
  dim?: boolean;
  onClick: () => void;
  count?: number;
  italic?: boolean;
  children: ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      className={cn(
        "flex w-full items-center gap-2 rounded-md px-2 py-1 text-sm transition-colors",
        on ? "bg-accent" : "hover:bg-accent/50",
        dim && !on && "opacity-50"
      )}
    >
      <span
        dir="auto"
        className={cn(
          "flex-1 truncate text-left",
          italic && "italic text-muted-foreground"
        )}
      >
        {children}
      </span>
      {on && <Check className="h-3.5 w-3.5" />}
      {count !== undefined && (
        <span className="text-xs text-muted-foreground">{count}</span>
      )}
    </button>
  );
}

/** Active-facet chip in the toolbar row — X clears that facet. */
export function FilterChip({
  label,
  onClear,
}: {
  label: string;
  onClear: () => void;
}) {
  return (
    <Badge variant="secondary" className="gap-1.5">
      <span dir="auto">{label}</span>
      <button aria-label={`Clear filter: ${label}`} onClick={onClear}>
        <X className="h-3 w-3" />
      </button>
    </Badge>
  );
}

export function toggleIn<T>(set: Set<T>, v: T): Set<T> {
  const next = new Set(set);
  if (next.has(v)) next.delete(v);
  else next.add(v);
  return next;
}

/** Chip label helper: first value's label, "+n" when more are selected. */
export function chipSummary(labels: string[]): string {
  if (labels.length <= 1) return labels[0] ?? "";
  return `${labels[0]} +${labels.length - 1}`;
}
