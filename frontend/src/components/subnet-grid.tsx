"use client";

import { useCallback, useEffect, useId, useMemo, useRef, useState } from "react";
import { useVirtualizer } from "@tanstack/react-virtual";

import { usePrefs } from "@/lib/prefs";
import { useRowNavMove } from "@/lib/row-nav";
import { GRID_CELL_TOKENS, STATUS_TOKENS } from "@/lib/status-tokens";
import { cn, intToIp, ipToInt, timeAgo } from "@/lib/utils";
import type {
  AddressPage,
  IpAddress,
  IpRange,
  IpStatus,
  Tag,
} from "@/types";
import { TagChip } from "@/components/tag-picker";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";

const COLS = 16;
/** Subnet-grid cell edge (px) per density pref — compact packs more in. */
const CELL_SIZE = { comfortable: 40, compact: 28 } as const;
/** Grids at or below this many cells render every row — cheap and makes
 *  keyboard navigation trivial. Larger grids keep row virtualization and
 *  move focus via scrollToIndex + a pending-focus pass after render. */
const VIRTUALIZE_ABOVE = 256;

export type CellState =
  | { kind: "free" }
  | { kind: "boundary" }
  | { kind: "range"; range: IpRange }
  | { kind: "used"; addr: IpAddress };

const STATUS_ORDER: IpStatus[] = [
  "active",
  "reserved",
  "dhcp",
  "discovered",
  "offline",
];

/** Technical-address marker → cell glyph (V6.1). The backend stamps
 *  `custom_fields.technical` on the protected rows it manages. */
const TECH_GLYPHS: Record<string, string> = { gateway: "⌂", dns: "≋" };

function techMarker(addr: IpAddress): string | null {
  const t = addr.custom_fields?.technical;
  return typeof t === "string" ? t : null;
}

function cellLabel(ip: string, st: CellState): string {
  switch (st.kind) {
    case "used": {
      const parts = [`${ip} — ${st.addr.status}`];
      const tech = techMarker(st.addr);
      if (tech) parts.push(tech === "dns" ? "DNS resolver" : tech);
      if (st.addr.hostname) parts.push(`host ${st.addr.hostname}`);
      if (st.addr.mac_address) parts.push(`mac ${st.addr.mac_address}`);
      return parts.join(", ");
    }
    case "boundary":
      return `${ip} — network/broadcast, not usable for hosts`;
    case "range":
      return `${ip} — ${st.range.role} range ${st.range.start_address}–${st.range.end_address}${
        st.range.description ? `, ${st.range.description}` : ""
      }`;
    case "free":
      return `${ip} — free, click to reserve`;
  }
}

/** Legend swatches are driven by the same tokens as the cells, so a new
 *  status automatically appears here. */
function GridLegend({ id }: { id: string }) {
  return (
    <div
      id={id}
      className="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-muted-foreground"
    >
      {STATUS_ORDER.map((s) => (
        <span key={s} className="inline-flex items-center gap-1">
          <span
            aria-hidden="true"
            className={cn(
              "inline-flex h-3.5 w-3.5 items-center justify-center rounded-sm text-[8px] leading-none",
              STATUS_TOKENS[s].cell
            )}
          >
            {STATUS_TOKENS[s].glyph}
          </span>
          {s}
        </span>
      ))}
      {(["free", "boundary", "range"] as const).map((k) => (
        <span key={k} className="inline-flex items-center gap-1">
          <span
            aria-hidden="true"
            className={cn(
              "inline-flex h-3.5 w-3.5 items-center justify-center rounded-sm text-[8px] leading-none",
              GRID_CELL_TOKENS[k].cell
            )}
          />
          {GRID_CELL_TOKENS[k].label}
        </span>
      ))}
      <span className="ml-auto text-[10px]">
        Tab enters grid · arrow keys move · Enter selects
      </span>
    </div>
  );
}

export function SubnetGrid({
  page,
  ranges = [],
  onSelect,
  tags,
  matchIds = null,
  highlight,
  focusInt = null,
  spanSel = null,
  onSpanSelect,
  onClearSpan,
  spanSelectable = false,
  liveFound = null,
}: {
  page: AddressPage;
  ranges?: IpRange[];
  onSelect: (ip: string, addr: IpAddress | null) => void;
  tags?: Map<number, Tag[]>;
  matchIds?: Set<number> | null;
  highlight?: Map<number, string>;
  focusInt?: number | null;
  /** Committed drag-selection span as address-int bounds (data, not DOM). */
  spanSel?: { lo: number; hi: number } | null;
  onSpanSelect?: (lo: number, hi: number) => void;
  onClearSpan?: () => void;
  /** Gate drag-select on the caller's write permission; touch devices are
   *  excluded automatically below (drag fights scroll). */
  spanSelectable?: boolean;
  /** Address ints reported live by a running scan (F15) — cells pulse with
   *  an emerald ring when nothing is documented there yet, sky when the IP
   *  already has an address row. */
  liveFound?: Set<number> | null;
}) {
  const parentRef = useRef<HTMLDivElement>(null);
  const cellRefs = useRef(new Map<number, HTMLButtonElement>());
  const pendingFocus = useRef<number | null>(null);
  const legendId = useId();
  const [prefs] = usePrefs();
  const cellSize = CELL_SIZE[prefs.density];

  // Drag-select state: `drag` is the in-progress gesture (cell indices),
  // `dragSpan` is the live preview as address-int bounds. Coarse pointers
  // (touch) get no drag-select — it fights scroll; row actions cover it.
  const drag = useRef<{ start: number; end: number; moved: boolean } | null>(
    null
  );
  const justDragged = useRef(false);
  const [dragSpan, setDragSpan] = useState<{ lo: number; hi: number } | null>(
    null
  );
  const coarse = useMemo(
    () =>
      typeof window !== "undefined" &&
      window.matchMedia("(pointer: coarse)").matches,
    []
  );
  const dragOk = spanSelectable && !coarse;

  const byInt = useMemo(() => {
    const m = new Map<number, IpAddress>();
    for (const a of page.items) m.set(Number(a.address_int), a);
    return m;
  }, [page.items]);

  const base = useMemo(() => {
    const [cidr] = (page.prefix ?? "0.0.0.0/0").split("/");
    return ipToInt(cidr);
  }, [page.prefix]);

  const total = page.total;
  const firstBound = page.usable_first ? ipToInt(page.usable_first) : null;
  const lastBound = page.usable_last ? ipToInt(page.usable_last) : null;
  const rows = Math.ceil(total / COLS);
  const virtualized = total > VIRTUALIZE_ABOVE;

  // Roving tabindex — index of the cell that owns the single Tab stop.
  const [focusIdx, setFocusIdx] = useState(0);

  const rangeSpans = useMemo(
    () => ranges.map((r) => ({ ...r, s: Number(r.start_int), e: Number(r.end_int) })),
    [ranges]
  );

  const virtualizer = useVirtualizer({
    count: rows,
    getScrollElement: () => parentRef.current,
    estimateSize: () => cellSize + 4,
    overscan: 8,
  });

  // Re-measure cached row positions when the density pref changes cell size.
  useEffect(() => {
    virtualizer.measure();
  }, [cellSize, virtualizer]);

  const focusCell = useCallback(
    (idx: number) => {
      setFocusIdx(idx);
      const el = cellRefs.current.get(idx);
      if (el) {
        el.focus();
        return;
      }
      // Target row isn't mounted — only possible on virtualized grids.
      pendingFocus.current = idx;
      virtualizer.scrollToIndex(Math.floor(idx / COLS), { align: "auto" });
    },
    [virtualizer]
  );

  // Flush a pending arrow-key focus once the virtualizer mounts the row.
  useEffect(() => {
    const idx = pendingFocus.current;
    if (idx == null) return;
    const el = cellRefs.current.get(idx);
    if (el) {
      pendingFocus.current = null;
      el.focus();
    }
  });

  useEffect(() => {
    if (focusInt == null) return;
    const idx = focusInt - base;
    const row = Math.floor(idx / COLS);
    if (row >= 0 && row < rows) {
      setFocusIdx(idx);
      if (virtualized) virtualizer.scrollToIndex(row, { align: "center" });
      else
        cellRefs.current
          .get(idx)
          ?.scrollIntoView({ block: "nearest" });
    }
  }, [focusInt, base, rows, virtualized, virtualizer]);

  // Global j/k move one grid row — the grid owns row-nav while mounted.
  const moveRow = useCallback(
    (d: number) => {
      const cur = Math.min(focusIdx, total - 1);
      focusCell(Math.min(Math.max(cur + d * COLS, 0), total - 1));
    },
    [focusIdx, total, focusCell]
  );
  useRowNavMove(moveRow);

  // Commit/cancel a drag on pointerup/cancel anywhere — release may land on a
  // different cell or outside the grid entirely.
  useEffect(() => {
    if (!dragOk) return;
    const finish = () => {
      const d = drag.current;
      drag.current = null;
      setDragSpan(null);
      if (d?.moved) {
        const lo = base + Math.min(d.start, d.end);
        const hi = base + Math.max(d.start, d.end);
        // Suppress the click that follows pointerup — a drag is not a select.
        justDragged.current = true;
        setTimeout(() => {
          justDragged.current = false;
        }, 0);
        onSpanSelect?.(lo, hi);
      }
    };
    const cancel = () => {
      drag.current = null;
      setDragSpan(null);
    };
    window.addEventListener("pointerup", finish);
    window.addEventListener("pointercancel", cancel);
    return () => {
      window.removeEventListener("pointerup", finish);
      window.removeEventListener("pointercancel", cancel);
    };
  }, [dragOk, base, onSpanSelect]);

  function cellState(intIp: number): CellState {
    const addr = byInt.get(intIp);
    if (addr) return { kind: "used", addr };
    if (intIp === firstBound || intIp === lastBound) return { kind: "boundary" };
    const range = rangeSpans.find((r) => intIp >= r.s && intIp <= r.e);
    if (range) return { kind: "range", range };
    return { kind: "free" };
  }

  const onGridKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Escape") {
      drag.current = null;
      setDragSpan(null);
      onClearSpan?.();
      return;
    }
    const idx = Math.min(focusIdx, total - 1);
    let target: number | null = null;
    switch (e.key) {
      case "ArrowRight":
        target = Math.min(idx + 1, total - 1);
        break;
      case "ArrowLeft":
        target = Math.max(idx - 1, 0);
        break;
      case "ArrowDown":
        target = Math.min(idx + COLS, total - 1);
        break;
      case "ArrowUp":
        target = Math.max(idx - COLS, 0);
        break;
      case "Home":
        target = idx - (idx % COLS);
        break;
      case "End":
        target = Math.min(idx - (idx % COLS) + COLS - 1, total - 1);
        break;
      case "PageDown":
        target = Math.min(idx + COLS * 8, total - 1);
        break;
      case "PageUp":
        target = Math.max(idx - COLS * 8, 0);
        break;
      default:
        return;
    }
    e.preventDefault();
    if (target !== idx) focusCell(target);
  };

  const rowList = virtualized
    ? virtualizer
        .getVirtualItems()
        .map((v) => ({ index: v.index, start: v.start, key: v.key }))
    : Array.from({ length: rows }, (_, i) => ({
        index: i,
        start: i * (cellSize + 4),
        key: i,
      }));

  // If the roving cell scrolled out of the DOM (or the prefix shrank),
  // hand the Tab stop to the first rendered cell so the grid stays reachable.
  const clampedFocus = Math.min(focusIdx, total - 1);
  const focusRowRendered = rowList.some(
    (r) => r.index === Math.floor(clampedFocus / COLS)
  );
  const tabbableIdx = focusRowRendered
    ? clampedFocus
    : rowList.length > 0
      ? rowList[0].index * COLS
      : -1;

  return (
    <>
      <div
        ref={parentRef}
        className="max-h-[65vh] overflow-auto rounded-lg border p-3"
      >
        <div
          role="grid"
          aria-label={
            page.prefix ? `Subnet map for ${page.prefix}` : "Subnet map"
          }
          aria-describedby={legendId}
          aria-rowcount={rows}
          aria-colcount={COLS}
          onKeyDown={onGridKeyDown}
          style={{ height: virtualizer.getTotalSize(), position: "relative" }}
          className="w-fit"
        >
          {rowList.map((vRow) => (
            <div
              key={vRow.key}
              role="row"
              aria-rowindex={vRow.index + 1}
              className="absolute left-0 flex gap-1"
              style={{ top: vRow.start, height: cellSize }}
            >
              {Array.from({ length: COLS }, (_, col) => {
                const idx = vRow.index * COLS + col;
                if (idx >= total)
                  return (
                    <div
                      key={col}
                      aria-hidden="true"
                      style={{ width: cellSize }}
                    />
                  );
                const intIp = base + idx;
                const ip = intToIp(intIp);
                const st = cellState(intIp);
                // Live drag preview wins over the committed span for display.
                const sel = dragSpan ?? spanSel;
                const inSpan =
                  sel != null && intIp >= sel.lo && intIp <= sel.hi;
                const last = ip.split(".")[3];
                const cellTags =
                  st.kind === "used" ? (tags?.get(st.addr.id) ?? []) : [];
                const matched =
                  st.kind === "used" &&
                  matchIds != null &&
                  matchIds.has(st.addr.id);
                const dimmed = matchIds != null && !matched;
                const hl = matched
                  ? (highlight?.get(st.addr.id) ?? "#38bdf8")
                  : null;
                const glyph =
                  st.kind === "used" ? STATUS_TOKENS[st.addr.status].glyph : "";
                const techGlyph =
                  st.kind === "used"
                    ? (TECH_GLYPHS[techMarker(st.addr) ?? ""] ?? null)
                    : null;
                const liveHit = liveFound?.has(intIp) ?? false;
                const cell = (
                  <button
                    key={col}
                    type="button"
                    role="gridcell"
                    aria-rowindex={vRow.index + 1}
                    aria-colindex={col + 1}
                    aria-label={
                      cellLabel(ip, st) +
                      (liveHit ? ", just found by live scan" : "")
                    }
                    tabIndex={idx === tabbableIdx ? 0 : -1}
                    aria-selected={inSpan || undefined}
                    ref={(el) => {
                      if (el) cellRefs.current.set(idx, el);
                      else cellRefs.current.delete(idx);
                    }}
                    onFocus={() => setFocusIdx(idx)}
                    onPointerDown={(e) => {
                      if (!dragOk || e.pointerType === "touch" || e.button !== 0)
                        return;
                      drag.current = { start: idx, end: idx, moved: false };
                      justDragged.current = false;
                    }}
                    onPointerEnter={() => {
                      const d = drag.current;
                      if (!d) return;
                      // Crossing into another cell makes it a drag — a ~4px+
                      // move by construction (cells are >=28px), so plain
                      // clicks stay plain clicks.
                      if (idx !== d.start) d.moved = true;
                      if (d.moved) {
                        d.end = idx;
                        setDragSpan({
                          lo: base + Math.min(d.start, d.end),
                          hi: base + Math.max(d.start, d.end),
                        });
                      }
                    }}
                    onClick={() => {
                      if (justDragged.current) {
                        justDragged.current = false;
                        return;
                      }
                      onSelect(ip, st.kind === "used" ? st.addr : null);
                    }}
                    className={cn(
                      "relative flex items-center justify-center rounded text-[10px] font-mono transition-colors",
                      st.kind === "used"
                        ? STATUS_TOKENS[st.addr.status].cell
                        : GRID_CELL_TOKENS[st.kind].cell,
                      dimmed && "opacity-25",
                      inSpan && "ipcell-sel",
                      liveHit &&
                        (st.kind === "used"
                          ? "ipcell-found-known"
                          : "ipcell-found-new")
                    )}
                    style={{
                      width: cellSize,
                      height: cellSize,
                      ...(hl ? { boxShadow: `inset 0 0 0 2px ${hl}` } : {}),
                    }}
                  >
                    {glyph && (
                      <span
                        aria-hidden="true"
                        className="absolute left-0.5 top-0.5 text-[8px] leading-none opacity-80"
                      >
                        {glyph}
                      </span>
                    )}
                    {techGlyph && (
                      <span
                        aria-hidden="true"
                        className="absolute bottom-0.5 left-0.5 text-[9px] leading-none opacity-90"
                      >
                        {techGlyph}
                      </span>
                    )}
                    {last}
                    {cellTags.length > 0 && (
                      <span className="absolute bottom-0.5 right-0.5 flex gap-0.5">
                        {cellTags.slice(0, 3).map((t) => (
                          <i
                            key={t.id}
                            className="h-1 w-1 rounded-full"
                            style={{ background: t.color }}
                          />
                        ))}
                      </span>
                    )}
                  </button>
                );
                return (
                  <Tooltip key={col}>
                    <TooltipTrigger asChild>{cell}</TooltipTrigger>
                    <TooltipContent side="top" className="w-56 space-y-1">
                      <div className="font-mono text-sm text-foreground">{ip}</div>
                      {liveHit && (
                        <div className="text-emerald-600 dark:text-emerald-400">
                          found by the running scan
                          {st.kind === "used" ? " — already documented" : " — new"}
                        </div>
                      )}
                      {st.kind === "used" ? (
                        <div className="space-y-0.5 text-muted-foreground">
                          {techMarker(st.addr) === "gateway" && (
                            <div className="text-sky-400">gateway</div>
                          )}
                          {techMarker(st.addr) === "dns" && (
                            <div className="text-sky-400">DNS resolver</div>
                          )}
                          {st.addr.range_role && (
                            <div>
                              in {st.addr.range_role} pool
                            </div>
                          )}
                          {st.addr.hostname && <div>host: {st.addr.hostname}</div>}
                          {st.addr.mac_address && <div>mac: {st.addr.mac_address}</div>}
                          {st.addr.vendor && <div>vendor: {st.addr.vendor}</div>}
                          <div>
                            status: <span className="capitalize">{st.addr.status}</span>
                            {" · "}seen {timeAgo(st.addr.last_seen)}
                          </div>
                          {st.addr.notes && <div>notes: {st.addr.notes}</div>}
                          {cellTags.length > 0 && (
                            <div className="flex flex-wrap gap-1 pt-1">
                              {cellTags.map((t) => (
                                <TagChip key={t.id} tag={t} />
                              ))}
                            </div>
                          )}
                        </div>
                      ) : st.kind === "boundary" ? (
                        <div className="text-muted-foreground">
                          network/broadcast — not usable for hosts
                        </div>
                      ) : st.kind === "range" ? (
                        <div className="text-muted-foreground">
                          <div>
                            in range{" "}
                            <span className="text-range font-mono">
                              {st.range.start_address}–{st.range.end_address}
                            </span>
                          </div>
                          <div>
                            role: {st.range.role}
                            {st.range.description ? ` · ${st.range.description}` : ""}
                          </div>
                        </div>
                      ) : (
                        <div className="text-muted-foreground">free — click to reserve</div>
                      )}
                    </TooltipContent>
                  </Tooltip>
                );
              })}
            </div>
          ))}
        </div>
      </div>
      <GridLegend id={legendId} />
    </>
  );
}
