"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { useVirtualizer } from "@tanstack/react-virtual";
import {
  ChevronDown,
  ChevronUp,
  ChevronsUpDown,
  LayoutGrid,
  List,
  MoreHorizontal,
  Pencil,
  Radar,
  Trash2,
  Zap,
} from "lucide-react";
import { toast } from "sonner";

import { api } from "@/lib/api";
import type { AddrMapView } from "@/lib/prefs";
import { cn, intToIp, ipToInt, timeAgo } from "@/lib/utils";
import type { AddressPage, IpAddress, IpRange, Tag } from "@/types";
import { IpStatusBadge } from "@/components/status-badge";
import { TagChip, TagPicker } from "@/components/tag-picker";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Switch } from "@/components/ui/switch";
import { TableCell, TableHead, TableRow } from "@/components/ui/table";

// Above this many addresses, expanding free space into per-IP rows is pointless —
// grouping is forced.
const UNGROUPED_CAP = 4096;

type Row =
  | { kind: "addr"; addr: IpAddress; pos: number; key: string }
  | { kind: "free"; start: number; end: number; pos: number; key: string }
  | { kind: "range"; start: number; end: number; range: IpRange; pos: number; key: string }
  | { kind: "boundary"; intIp: number; pos: number; key: string };

type SortKey = "ip" | "status" | "hostname" | "last_seen";

export function AddrMapViewSwitcher({
  view,
  onChange,
}: {
  view: AddrMapView;
  onChange: (v: AddrMapView) => void;
}) {
  const views = [
    { v: "grid" as const, icon: LayoutGrid, label: "Grid view" },
    { v: "list" as const, icon: List, label: "List view" },
  ];
  return (
    <div
      role="group"
      aria-label="Address map view"
      className="flex items-center gap-0.5 rounded-md border p-0.5"
      onKeyDown={(e) => {
        if (e.key === "ArrowLeft" || e.key === "ArrowRight") {
          onChange(view === "grid" ? "list" : "grid");
          e.preventDefault();
        }
      }}
    >
      {views.map(({ v, icon: Icon, label }) => (
        <button
          key={v}
          type="button"
          aria-pressed={view === v}
          title={label}
          onClick={() => onChange(v)}
          className={cn(
            "rounded px-2 py-1 transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring",
            view === v
              ? "bg-accent text-foreground"
              : "text-muted-foreground hover:text-foreground"
          )}
        >
          <Icon className="h-4 w-4" />
        </button>
      ))}
    </div>
  );
}

/** Gap analysis: merge used ints + boundary points + range spans; the
 *  complement inside [base, base+total) yields the free segments. O(n) in the
 *  number of stored addresses — safe even for very large prefixes. */
function buildRows(
  page: AddressPage,
  ranges: IpRange[],
  groupFree: boolean
): { rows: Row[]; freeCount: number } {
  const cidr = page.prefix ?? "0.0.0.0/0";
  const v4 = !cidr.includes(":");
  const rows: Row[] = page.items.map((a) => ({
    kind: "addr",
    addr: a,
    pos: Number(a.address_int),
    key: `a${a.id}`,
  }));
  if (!v4) return { rows, freeCount: 0 };

  const base = ipToInt(cidr.split("/")[0]);
  const last = base + page.total - 1;
  const used = new Set(page.items.map((a) => Number(a.address_int)));

  const boundFirst = page.usable_first ? ipToInt(page.usable_first) : null;
  const boundLast = page.usable_last ? ipToInt(page.usable_last) : null;
  const covered = new Set(used);
  for (const b of [boundFirst, boundLast]) {
    if (b != null) {
      covered.add(b);
      if (!used.has(b)) {
        rows.push({ kind: "boundary", intIp: b, pos: b, key: `b${b}` });
      }
    }
  }

  // Range rows: split each IpRange around covered points so used addresses
  // keep precedence (same rule as the grid).
  const coveredIn = (s: number, e: number) =>
    [...covered].filter((i) => i >= s && i <= e).sort((a, b) => a - b);
  for (const r of ranges) {
    const s = Math.max(Number(r.start_int), base);
    const e = Math.min(Number(r.end_int), last);
    if (s > e) continue;
    let cur = s;
    for (const p of coveredIn(s, e)) {
      if (p > cur) {
        rows.push({ kind: "range", start: cur, end: p - 1, range: r, pos: cur, key: `r${r.id}-${cur}` });
      }
      cur = p + 1;
    }
    if (cur <= e) {
      rows.push({ kind: "range", start: cur, end: e, range: r, pos: cur, key: `r${r.id}-${cur}` });
    }
  }

  // Occupied = covered points ∪ range spans → free gaps are the complement.
  const occ: [number, number][] = [...covered].map((i) => [i, i]);
  for (const r of ranges) {
    const s = Math.max(Number(r.start_int), base);
    const e = Math.min(Number(r.end_int), last);
    if (s <= e) occ.push([s, e]);
  }
  occ.sort((a, b) => a[0] - b[0]);

  const gaps: [number, number][] = [];
  let cur = base;
  for (const [s, e] of occ) {
    if (e < cur || s > last) continue;
    if (s > cur) gaps.push([cur, Math.min(s - 1, last)]);
    cur = Math.max(cur, e + 1);
    if (cur > last) break;
  }
  if (cur <= last) gaps.push([cur, last]);

  const freeCount = gaps.reduce((n, [s, e]) => n + e - s + 1, 0);
  const ungrouped = !groupFree && page.total <= UNGROUPED_CAP;
  for (const [s, e] of gaps) {
    if (ungrouped) {
      for (let i = s; i <= e; i++) {
        rows.push({ kind: "free", start: i, end: i, pos: i, key: `f${i}` });
      }
    } else {
      rows.push({ kind: "free", start: s, end: e, pos: s, key: `f${s}` });
    }
  }

  rows.sort((a, b) => a.pos - b.pos);
  return { rows, freeCount };
}

function sortAddr(rows: Row[], key: SortKey, dir: 1 | -1): Row[] {
  const val = (a: IpAddress): string | number =>
    key === "ip"
      ? Number(a.address_int)
      : key === "status"
        ? a.status
        : key === "hostname"
          ? (a.hostname ?? "")
          : (a.last_seen ?? "");
  const addrs = rows.filter((r): r is Extract<Row, { kind: "addr" }> => r.kind === "addr");
  addrs.sort((x, y) => {
    const a = val(x.addr);
    const b = val(y.addr);
    const c =
      typeof a === "number" && typeof b === "number"
        ? a - b
        : String(a).localeCompare(String(b));
    return c * dir;
  });
  return addrs;
}

export function AddressList({
  page,
  ranges,
  filtered,
  filtersActive,
  tags,
  allTags,
  highlight,
  focusInt,
  selectable,
  canDelete,
  selected,
  onToggle,
  onToggleAll,
  allChecked,
  onTagsChanged,
  onSelect,
  onSelectFree,
  onChanged,
}: {
  page: AddressPage;
  ranges: IpRange[];
  filtered: IpAddress[];
  filtersActive: boolean;
  tags: Map<number, Tag[]>;
  allTags: Tag[];
  highlight?: Map<number, string>;
  focusInt?: number | null;
  selectable: boolean;
  canDelete: boolean;
  selected: Set<number>;
  onToggle: (id: number, on: boolean) => void;
  onToggleAll: (on: boolean) => void;
  allChecked: boolean;
  onTagsChanged: () => void;
  onSelect: (a: IpAddress) => void;
  onSelectFree: (ip: string) => void;
  onChanged: () => void;
}) {
  const parentRef = useRef<HTMLDivElement>(null);
  const [groupFree, setGroupFree] = useState(true);
  const [sortKey, setSortKey] = useState<SortKey>("ip");
  const [sortDir, setSortDir] = useState<1 | -1>(1);

  const canUngroup = page.total <= UNGROUPED_CAP;
  const colCount = selectable ? 8 : 7;

  const { rows: allRows, freeCount } = useMemo(
    () => buildRows(page, ranges, groupFree),
    [page, ranges, groupFree]
  );

  const rows = useMemo(() => {
    if (filtersActive) {
      // Aggregates can't match filters — show only matching addresses.
      const addrRows: Row[] = filtered.map((a) => ({
        kind: "addr",
        addr: a,
        pos: Number(a.address_int),
        key: `a${a.id}`,
      }));
      if (sortKey !== "ip") return sortAddr(addrRows, sortKey, sortDir);
      return sortDir === 1 ? addrRows : [...addrRows].reverse();
    }
    if (sortKey !== "ip") return sortAddr(allRows, sortKey, sortDir);
    return sortDir === 1 ? allRows : [...allRows].reverse();
  }, [allRows, filtered, filtersActive, sortKey, sortDir]);

  const virtualizer = useVirtualizer({
    count: rows.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 41,
    overscan: 12,
  });

  useEffect(() => {
    if (focusInt == null) return;
    const exact = rows.findIndex(
      (r) => r.kind === "addr" && Number(r.addr.address_int) === focusInt
    );
    const at = exact >= 0 ? exact : rows.findIndex((r) => r.pos >= focusInt);
    if (at >= 0) virtualizer.scrollToIndex(at, { align: "center" });
  }, [focusInt, rows, virtualizer]);

  const toggleSort = (k: SortKey) => {
    if (sortKey === k) setSortDir((d) => (d === 1 ? -1 : 1));
    else {
      setSortKey(k);
      setSortDir(1);
    }
  };

  const sortHead = (k: SortKey, label: string, className?: string) => {
    const active = sortKey === k;
    const Icon = !active ? ChevronsUpDown : sortDir === 1 ? ChevronUp : ChevronDown;
    return (
      <TableHead className={cn("sticky top-0 z-10 bg-card", className)}>
        <button
          type="button"
          onClick={() => toggleSort(k)}
          className={cn(
            "inline-flex items-center gap-1 uppercase tracking-wide",
            active ? "text-foreground" : "text-muted-foreground hover:text-foreground"
          )}
        >
          {label}
          <Icon className="h-3 w-3" />
        </button>
      </TableHead>
    );
  };

  const copy = (ip: string) => {
    navigator.clipboard?.writeText(ip).catch(() => {});
    toast.success(`Copied ${ip}`);
  };

  const scan = async (a: IpAddress) => {
    try {
      await api.post("/api/v1/scans", { cidr: `${a.address}/32` });
      toast.success(`Scan queued for ${a.address}`);
    } catch (e) {
      toast.error("Scan failed", { description: String(e) });
    }
  };

  const release = async (a: IpAddress) => {
    try {
      await api.del(`/api/v1/addresses/${a.id}`);
      toast.success(`${a.address} released`);
      onChanged();
    } catch (e) {
      toast.error("Release failed", { description: String(e) });
    }
  };

  const vItems = virtualizer.getVirtualItems();
  const padTop = vItems.length ? vItems[0].start : 0;
  const padBottom = vItems.length
    ? virtualizer.getTotalSize() - vItems[vItems.length - 1].end
    : 0;

  const renderRow = (row: Row, index: number) => {
    const measure = {
      ref: virtualizer.measureElement,
      "data-index": index,
    } as const;
    if (row.kind === "free") {
      const count = row.end - row.start + 1;
      return (
        <tr
          key={row.key}
          {...measure}
          className="cursor-pointer border-b transition-colors hover:bg-muted/50"
          onClick={() => onSelectFree(intToIp(row.start))}
        >
          {selectable && <TableCell className="py-2" />}
          <TableCell className="py-2 font-mono text-muted-foreground">
            {row.start === row.end
              ? intToIp(row.start)
              : `${intToIp(row.start)} – ${intToIp(row.end)}`}
          </TableCell>
          <TableCell className="py-2">
            <span className="inline-flex items-center rounded-md bg-zinc-500/15 px-2 py-0.5 text-xs font-medium text-zinc-400">
              free
            </span>
          </TableCell>
          <TableCell colSpan={4} className="py-2 text-xs text-muted-foreground">
            {count.toLocaleString()} free address{count > 1 ? "es" : ""}
          </TableCell>
          <TableCell
            className="py-2 text-right"
            onClick={(e) => e.stopPropagation()}
          >
            {selectable && (
              <Button
                size="sm"
                variant="ghost"
                className="h-7 px-2 text-xs"
                onClick={() => onSelectFree(intToIp(row.start))}
              >
                <Zap className="h-3.5 w-3.5" /> Allocate
              </Button>
            )}
          </TableCell>
        </tr>
      );
    }

    if (row.kind === "range") {
      const count = row.end - row.start + 1;
      return (
        <tr key={row.key} {...measure} className="border-b transition-colors">
          {selectable && <TableCell className="py-2" />}
          <TableCell className="py-2 font-mono text-sky-400/80">
            {row.start === row.end
              ? intToIp(row.start)
              : `${intToIp(row.start)} – ${intToIp(row.end)}`}
          </TableCell>
          <TableCell className="py-2">
            <Badge
              variant="outline"
              className="border-dashed border-sky-700/60 text-sky-400"
            >
              {row.range.role}
            </Badge>
          </TableCell>
          <TableCell colSpan={4} className="py-2 text-xs text-muted-foreground">
            range
            {row.range.description ? ` · ${row.range.description}` : ""} ·{" "}
            {count.toLocaleString()} address{count > 1 ? "es" : ""}
          </TableCell>
          <TableCell className="py-2" />
        </tr>
      );
    }

    if (row.kind === "boundary") {
      return (
        <tr key={row.key} {...measure} className="border-b transition-colors">
          {selectable && <TableCell className="py-2" />}
          <TableCell className="py-2 font-mono text-zinc-600">
            {intToIp(row.intIp)}
          </TableCell>
          <TableCell
            colSpan={colCount - (selectable ? 3 : 2)}
            className="py-2 text-xs italic text-zinc-600"
          >
            network/broadcast — not usable for hosts
          </TableCell>
          <TableCell className="py-2" />
        </tr>
      );
    }

    const a = row.addr;
    const assigned = tags.get(a.id) ?? [];
    const hl = highlight?.get(a.id);
    return (
      <tr
        key={row.key}
        {...measure}
        className="cursor-pointer border-b transition-colors hover:bg-muted/50"
        style={hl ? { boxShadow: `inset 3px 0 0 ${hl}` } : undefined}
        onClick={() => onSelect(a)}
      >
        {selectable && (
          <TableCell className="py-2" onClick={(e) => e.stopPropagation()}>
            <Checkbox
              checked={selected.has(a.id)}
              onCheckedChange={(v) => onToggle(a.id, !!v)}
            />
          </TableCell>
        )}
        <TableCell className="py-2">
          <button
            type="button"
            title="Copy IP"
            onClick={(e) => {
              e.stopPropagation();
              copy(a.address);
            }}
            className="font-mono hover:text-emerald-300"
          >
            {a.address}
          </button>
          {a.nat_inside_id != null && (
            <span className="ml-1 text-xs text-sky-400" title="NAT inside">
              ⇄
            </span>
          )}
        </TableCell>
        <TableCell className="py-2">
          <span className="inline-flex items-center gap-1">
            <IpStatusBadge s={a.status} />
            {a.role && (
              <Badge variant="outline" className="text-muted-foreground">
                {a.role}
              </Badge>
            )}
          </span>
        </TableCell>
        <TableCell dir="auto" className="max-w-48 truncate py-2">
          {a.hostname ?? "—"}
        </TableCell>
        <TableCell className="max-w-52 truncate py-2">
          <span dir="ltr" className="font-mono text-xs">
            {a.mac_address ?? "—"}
          </span>
          {!!a.custom_fields?.mac_mismatch && (
            <span
              className="ml-1 text-xs text-amber-400"
              title={`MAC changed: was ${(a.custom_fields.mac_mismatch as { was?: string }).was ?? "?"}`}
            >
              ⚠
            </span>
          )}
          {a.vendor && (
            <span dir="auto" className="text-xs text-muted-foreground">
              {" "}
              · {a.vendor}
            </span>
          )}
        </TableCell>
        <TableCell
          className="max-w-56 py-2"
          onClick={(e) => e.stopPropagation()}
        >
          <div className="flex flex-wrap items-center gap-1">
            {assigned.map((t) => (
              <TagChip key={t.id} tag={t} />
            ))}
            <TagPicker
              objectType="IPAddress"
              objectId={a.id}
              allTags={allTags}
              assigned={assigned}
              onChanged={onTagsChanged}
            />
          </div>
        </TableCell>
        <TableCell className="py-2 text-muted-foreground">
          {timeAgo(a.last_seen)}
        </TableCell>
        <TableCell
          className="py-2 text-right"
          onClick={(e) => e.stopPropagation()}
        >
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon" className="h-7 w-7">
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => onSelect(a)}>
                <Pencil className="h-3.5 w-3.5" /> Edit / details
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => copy(a.address)}>
                Copy IP
              </DropdownMenuItem>
              {selectable && (
                <DropdownMenuItem onClick={() => scan(a)}>
                  <Radar className="h-3.5 w-3.5" /> Scan this IP
                </DropdownMenuItem>
              )}
              {canDelete && (
                <>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem
                    className="text-rose-400"
                    onClick={() => release(a)}
                  >
                    <Trash2 className="h-3.5 w-3.5" /> Release
                  </DropdownMenuItem>
                </>
              )}
            </DropdownMenuContent>
          </DropdownMenu>
        </TableCell>
      </tr>
    );
  };

  return (
    <div>
      <div className="mb-2 flex items-center justify-between text-xs text-muted-foreground">
        <span>
          {page.items.length.toLocaleString()} address
          {page.items.length === 1 ? "" : "es"}
          {freeCount > 0 && ` · ${freeCount.toLocaleString()} free`}
          {filtersActive &&
            ` · ${filtered.length.toLocaleString()} matching`}
        </span>
        {canUngroup && !filtersActive && (
          <label className="flex items-center gap-2">
            Group free
            <Switch checked={groupFree} onCheckedChange={setGroupFree} />
          </label>
        )}
      </div>

      <div
        ref={parentRef}
        className="max-h-[65vh] overflow-auto rounded-lg border"
      >
        <table className="w-full caption-bottom text-sm">
          <thead className="[&_tr]:border-b">
            <TableRow className="hover:bg-transparent">
              {selectable && (
                <TableHead className="sticky top-0 z-10 w-8 bg-card">
                  <Checkbox
                    checked={allChecked}
                    onCheckedChange={(v) => onToggleAll(!!v)}
                  />
                </TableHead>
              )}
              {sortHead("ip", "IP address")}
              {sortHead("status", "Status")}
              {sortHead("hostname", "Hostname")}
              <TableHead className="sticky top-0 z-10 bg-card">
                MAC / Vendor
              </TableHead>
              <TableHead className="sticky top-0 z-10 bg-card">Tags</TableHead>
              {sortHead("last_seen", "Last seen")}
              <TableHead className="sticky top-0 z-10 w-12 bg-card text-right" />
            </TableRow>
          </thead>
          <tbody>
            {padTop > 0 && (
              <tr aria-hidden="true">
                <td style={{ height: padTop, padding: 0 }} />
              </tr>
            )}
            {vItems.map((vi) => renderRow(rows[vi.index], vi.index))}
            {padBottom > 0 && (
              <tr aria-hidden="true">
                <td style={{ height: padBottom, padding: 0 }} />
              </tr>
            )}
            {rows.length === 0 && (
              <TableRow className="hover:bg-transparent">
                <TableCell
                  colSpan={colCount}
                  className="py-10 text-center text-muted-foreground"
                >
                  {filtersActive
                    ? "No addresses match."
                    : "No addresses in this prefix."}
                </TableCell>
              </TableRow>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
