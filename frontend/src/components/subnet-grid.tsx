"use client";

import { useMemo, useRef } from "react";
import { useVirtualizer } from "@tanstack/react-virtual";

import { cn, intToIp, ipToInt, timeAgo } from "@/lib/utils";
import type { AddressPage, IpAddress } from "@/types";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";

const CELL = 40;
const COLS = 16;

export type CellState =
  | { kind: "free" }
  | { kind: "boundary" }
  | { kind: "used"; addr: IpAddress };

const stateClass: Record<string, string> = {
  free: "bg-zinc-800/40 hover:bg-zinc-700/60 text-zinc-600",
  boundary: "bg-zinc-800 text-zinc-600 [background:repeating-linear-gradient(45deg,transparent,transparent_4px,rgba(255,255,255,0.03)_4px,rgba(255,255,255,0.03)_8px)]",
  active: "bg-emerald-500/25 text-emerald-300 hover:bg-emerald-500/40 border border-emerald-500/30",
  reserved: "bg-amber-500/20 text-amber-300 hover:bg-amber-500/35 border border-amber-500/30",
  dhcp: "bg-cyan-500/20 text-cyan-300 hover:bg-cyan-500/35 border border-cyan-500/30",
  discovered: "bg-violet-500/25 text-violet-300 hover:bg-violet-500/40 border border-violet-500/40",
  offline: "bg-zinc-600/40 text-zinc-500 hover:bg-zinc-600/60 border border-zinc-600/40",
};

export function SubnetGrid({
  page,
  onSelect,
}: {
  page: AddressPage;
  onSelect: (ip: string, addr: IpAddress | null) => void;
}) {
  const parentRef = useRef<HTMLDivElement>(null);

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

  const virtualizer = useVirtualizer({
    count: rows,
    getScrollElement: () => parentRef.current,
    estimateSize: () => CELL + 4,
    overscan: 8,
  });

  function cellState(intIp: number): CellState {
    const addr = byInt.get(intIp);
    if (addr) return { kind: "used", addr };
    if (intIp === firstBound || intIp === lastBound) return { kind: "boundary" };
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
            style={{ top: vRow.start, height: CELL }}
          >
            {Array.from({ length: COLS }, (_, col) => {
              const idx = vRow.index * COLS + col;
              if (idx >= total) return <div key={col} style={{ width: CELL }} />;
              const intIp = base + idx;
              const ip = intToIp(intIp);
              const st = cellState(intIp);
              const last = ip.split(".")[3];
              const cell = (
                <button
                  key={col}
                  onClick={() =>
                    onSelect(ip, st.kind === "used" ? st.addr : null)
                  }
                  className={cn(
                    "flex items-center justify-center rounded text-[10px] font-mono transition-colors",
                    st.kind === "used" ? stateClass[st.addr.status] : stateClass[st.kind]
                  )}
                  style={{ width: CELL, height: CELL }}
                >
                  {last}
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
                      </div>
                    ) : st.kind === "boundary" ? (
                      <div className="text-muted-foreground">
                        network/broadcast — not usable for hosts
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
