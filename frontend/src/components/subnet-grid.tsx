"use client";

import { useEffect, useMemo, useRef } from "react";
import { useVirtualizer } from "@tanstack/react-virtual";

import { usePrefs } from "@/lib/prefs";
import { GRID_CELL_TOKENS, STATUS_TOKENS } from "@/lib/status-tokens";
import { cn, intToIp, ipToInt, timeAgo } from "@/lib/utils";
import type { AddressPage, IpAddress, IpRange, Tag } from "@/types";
import { TagChip } from "@/components/tag-picker";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";

const COLS = 16;
/** Subnet-grid cell edge (px) per density pref — compact packs more in. */
const CELL_SIZE = { comfortable: 40, compact: 28 } as const;

export type CellState =
  | { kind: "free" }
  | { kind: "boundary" }
  | { kind: "range"; range: IpRange }
  | { kind: "used"; addr: IpAddress };

export function SubnetGrid({
  page,
  ranges = [],
  onSelect,
  tags,
  matchIds = null,
  highlight,
  focusInt = null,
}: {
  page: AddressPage;
  ranges?: IpRange[];
  onSelect: (ip: string, addr: IpAddress | null) => void;
  tags?: Map<number, Tag[]>;
  matchIds?: Set<number> | null;
  highlight?: Map<number, string>;
  focusInt?: number | null;
}) {
  const parentRef = useRef<HTMLDivElement>(null);
  const [prefs] = usePrefs();
  const cellSize = CELL_SIZE[prefs.density];

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

  useEffect(() => {
    if (focusInt == null) return;
    const row = Math.floor((focusInt - base) / COLS);
    if (row >= 0 && row < rows) {
      virtualizer.scrollToIndex(row, { align: "center" });
    }
  }, [focusInt, base, rows, virtualizer]);

  function cellState(intIp: number): CellState {
    const addr = byInt.get(intIp);
    if (addr) return { kind: "used", addr };
    if (intIp === firstBound || intIp === lastBound) return { kind: "boundary" };
    const range = rangeSpans.find((r) => intIp >= r.s && intIp <= r.e);
    if (range) return { kind: "range", range };
    return { kind: "free" };
  }

  return (
    <div ref={parentRef} className="max-h-[65vh] overflow-auto rounded-lg border p-3">
      <div
        style={{ height: virtualizer.getTotalSize(), position: "relative" }}
        className="w-fit"
      >
        {virtualizer.getVirtualItems().map((vRow) => (
          <div
            key={vRow.key}
            className="absolute left-0 flex gap-1"
            style={{ top: vRow.start, height: cellSize }}
          >
            {Array.from({ length: COLS }, (_, col) => {
              const idx = vRow.index * COLS + col;
              if (idx >= total) return <div key={col} style={{ width: cellSize }} />;
              const intIp = base + idx;
              const ip = intToIp(intIp);
              const st = cellState(intIp);
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
              const cell = (
                <button
                  key={col}
                  onClick={() =>
                    onSelect(ip, st.kind === "used" ? st.addr : null)
                  }
                  className={cn(
                    "relative flex items-center justify-center rounded text-[10px] font-mono transition-colors",
                    st.kind === "used"
                      ? STATUS_TOKENS[st.addr.status].cell
                      : GRID_CELL_TOKENS[st.kind],
                    dimmed && "opacity-25"
                  )}
                  style={{
                    width: cellSize,
                    height: cellSize,
                    ...(hl ? { boxShadow: `inset 0 0 0 2px ${hl}` } : {}),
                  }}
                >
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
                    {st.kind === "used" ? (
                      <div className="space-y-0.5 text-muted-foreground">
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
  );
}
