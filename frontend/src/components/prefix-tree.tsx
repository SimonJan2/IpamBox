"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useVirtualizer } from "@tanstack/react-virtual";
import {
  Building2,
  ChevronDown,
  ChevronRight,
  Copy,
  Waypoints,
} from "lucide-react";
import { toast } from "sonner";

import { cn } from "@/lib/utils";
import type { PrefixNode, SiteNode, VrfNode } from "@/types";
import { PrefixStatusBadge } from "@/components/status-badge";
import { Progress } from "@/components/ui/progress";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";

export const siteKey = (id: number | null) => `site-${id ?? "none"}`;
export const vrfKey = (id: number) => `vrf-${id}`;
export const prefixKey = (id: number) => `p-${id}`;

// Same thresholds as the utilization column in app/prefixes/page.tsx.
export function utilColor(pct: number) {
  if (pct > 80) return "bg-rose-500";
  if (pct > 50) return "bg-amber-500";
  return "bg-emerald-500";
}

export interface TreeRow {
  key: string;
  kind: "site" | "vrf" | "prefix";
  depth: number;
  level: number;
  posInSet: number;
  setSize: number;
  parentKey: string | null;
  expandable: boolean;
  prefixId?: number;
  site?: SiteNode;
  vrf?: VrfNode;
  node?: PrefixNode;
  count?: number;
  used?: number;
  usable?: number;
}

function vrfAgg(v: VrfNode) {
  let used = 0;
  let usable = 0;
  let count = 0;
  for (const p of v.prefixes) {
    used += p.agg_used_ips;
    usable += p.usable_ips;
    count += 1 + p.descendant_count;
  }
  return { used, usable, count };
}

/** Every expandable node key mapped to its depth (site=0, vrf=1, prefixes 2+). */
export function collectExpandableKeys(sites: SiteNode[]): Map<string, number> {
  const m = new Map<string, number>();
  for (const s of sites) {
    m.set(siteKey(s.id), 0);
    for (const v of s.vrfs) {
      if (v.prefixes.length > 0) m.set(vrfKey(v.id), 1);
      const walk = (n: PrefixNode, depth: number) => {
        if (n.children.length > 0) m.set(prefixKey(n.id), depth);
        n.children.forEach((c) => walk(c, depth + 1));
      };
      v.prefixes.forEach((p) => walk(p, 2));
    }
  }
  return m;
}

/** Pre-order flatten of the visible portion of the tree for virtualization. */
export function flattenTree(
  sites: SiteNode[],
  expanded: Set<string>,
  visible: Set<string> | null
): TreeRow[] {
  const rows: TreeRow[] = [];
  const filtering = visible !== null;
  const show = (k: string) => !filtering || visible.has(k);
  const open = (k: string) => filtering || expanded.has(k);

  const visSites = sites.filter((s) => show(siteKey(s.id)));
  visSites.forEach((site, si) => {
    const sKey = siteKey(site.id);
    const visVrfs = site.vrfs.filter((v) => show(vrfKey(v.id)));
    const sAgg = { used: 0, usable: 0, count: 0 };
    for (const v of site.vrfs) {
      const a = vrfAgg(v);
      sAgg.used += a.used;
      sAgg.usable += a.usable;
      sAgg.count += a.count;
    }
    rows.push({
      key: sKey,
      kind: "site",
      depth: 0,
      level: 1,
      posInSet: si + 1,
      setSize: visSites.length,
      parentKey: null,
      expandable: visVrfs.length > 0 || site.vrfs.length > 0,
      site,
      count: sAgg.count,
      used: sAgg.used,
      usable: sAgg.usable,
    });
    if (!open(sKey)) return;
    visVrfs.forEach((vrf, vi) => {
      const vKey = vrfKey(vrf.id);
      const vAgg = vrfAgg(vrf);
      const roots = vrf.prefixes.filter((p) => show(prefixKey(p.id)));
      rows.push({
        key: vKey,
        kind: "vrf",
        depth: 1,
        level: 2,
        posInSet: vi + 1,
        setSize: visVrfs.length,
        parentKey: sKey,
        expandable: roots.length > 0,
        vrf,
        count: vAgg.count,
        used: vAgg.used,
        usable: vAgg.usable,
      });
      if (!open(vKey)) return;
      const walk = (n: PrefixNode, depth: number, parent: string, idx: number, sibs: number) => {
        const key = prefixKey(n.id);
        const kids = n.children.filter((c) => show(prefixKey(c.id)));
        rows.push({
          key,
          kind: "prefix",
          depth,
          level: depth + 1,
          posInSet: idx + 1,
          setSize: sibs,
          parentKey: parent,
          expandable: kids.length > 0,
          node: n,
          prefixId: n.id,
        });
        if (open(key)) kids.forEach((c, ci) => walk(c, depth + 1, key, ci, kids.length));
      };
      roots.forEach((r, ri) => walk(r, 2, vKey, ri, roots.length));
    });
  });
  return rows;
}

function Highlight({ text, q }: { text: string; q: string }) {
  const i = q ? text.toLowerCase().indexOf(q.toLowerCase()) : -1;
  if (i < 0) return <>{text}</>;
  return (
    <>
      {text.slice(0, i)}
      <mark className="rounded-sm bg-amber-500/30 text-inherit">
        {text.slice(i, i + q.length)}
      </mark>
      {text.slice(i + q.length)}
    </>
  );
}

export function PrefixTree({
  sites,
  expanded,
  onToggle,
  visible,
  matchKeys,
  query,
  flashKey,
}: {
  sites: SiteNode[];
  expanded: Set<string>;
  onToggle: (key: string) => void;
  visible: Set<string> | null;
  matchKeys: Set<string>;
  query: string;
  flashKey: string | null;
}) {
  const router = useRouter();
  const parentRef = useRef<HTMLDivElement>(null);
  const [activeIndex, setActiveIndex] = useState(0);
  const [flash, setFlash] = useState<string | null>(null);

  const filtering = visible !== null;
  const isOpen = (key: string) => filtering || expanded.has(key);

  const rows = useMemo(
    () => flattenTree(sites, expanded, visible),
    [sites, expanded, visible]
  );
  const keyIndex = useMemo(
    () => new Map(rows.map((r, i) => [r.key, i])),
    [rows]
  );

  const virtualizer = useVirtualizer({
    count: rows.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 36,
    overscan: 12,
    getItemKey: (i) => rows[i].key,
  });

  useEffect(() => {
    if (activeIndex >= rows.length) setActiveIndex(Math.max(0, rows.length - 1));
  }, [rows.length, activeIndex]);

  useEffect(() => {
    if (!flashKey) return;
    const i = keyIndex.get(flashKey);
    if (i == null) return;
    virtualizer.scrollToIndex(i, { align: "center" });
    setActiveIndex(i);
    setFlash(flashKey);
    const t = setTimeout(() => setFlash(null), 2200);
    return () => clearTimeout(t);
  }, [flashKey, keyIndex, virtualizer]);

  const focusRow = (i: number) => {
    requestAnimationFrame(() => {
      parentRef.current
        ?.querySelector<HTMLElement>(`[data-idx="${i}"]`)
        ?.focus();
    });
  };

  const moveActive = (i: number) => {
    const next = Math.max(0, Math.min(i, rows.length - 1));
    setActiveIndex(next);
    virtualizer.scrollToIndex(next);
    focusRow(next);
  };

  const onKeyDown = (e: React.KeyboardEvent) => {
    const row = rows[activeIndex];
    switch (e.key) {
      case "ArrowDown":
        e.preventDefault();
        moveActive(activeIndex + 1);
        break;
      case "ArrowUp":
        e.preventDefault();
        moveActive(activeIndex - 1);
        break;
      case "Home":
        e.preventDefault();
        moveActive(0);
        break;
      case "End":
        e.preventDefault();
        moveActive(rows.length - 1);
        break;
      case "ArrowRight":
        if (!row) break;
        e.preventDefault();
        if (row.expandable && !isOpen(row.key)) onToggle(row.key);
        else if (row.expandable) moveActive(activeIndex + 1);
        break;
      case "ArrowLeft":
        if (!row) break;
        e.preventDefault();
        if (row.expandable && isOpen(row.key)) onToggle(row.key);
        else if (row.parentKey) {
          const pi = keyIndex.get(row.parentKey);
          if (pi != null) moveActive(pi);
        }
        break;
      case "Enter":
        if (!row) break;
        e.preventDefault();
        if (row.kind === "prefix" && row.prefixId != null)
          router.push(`/prefixes/${row.prefixId}`);
        else if (row.expandable) onToggle(row.key);
        break;
      case "c":
        if ((e.ctrlKey || e.metaKey) && row?.kind === "prefix" && row.node) {
          e.preventDefault();
          navigator.clipboard?.writeText(row.node.prefix).catch(() => {});
          toast.success(`Copied ${row.node.prefix}`);
        }
        break;
    }
  };

  const chevron = (row: TreeRow, label: string) =>
    row.expandable ? (
      <button
        type="button"
        tabIndex={-1}
        aria-label={`${isOpen(row.key) ? "Collapse" : "Expand"} ${label}`}
        onClick={(e) => {
          e.stopPropagation();
          onToggle(row.key);
        }}
        className="flex h-5 w-5 shrink-0 items-center justify-center rounded hover:bg-accent focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-emerald-500"
      >
        {isOpen(row.key) ? (
          <ChevronDown className="h-3.5 w-3.5" />
        ) : (
          <ChevronRight className="h-3.5 w-3.5" />
        )}
      </button>
    ) : (
      <span className="h-5 w-5 shrink-0" aria-hidden="true" />
    );

  const aggBar = (used: number, usable: number) => {
    const pct = usable > 0 ? Math.round((1000 * used) / usable) / 10 : 0;
    return (
      <Tooltip>
        <TooltipTrigger asChild>
          <div className="flex w-36 shrink-0 items-center gap-2">
            <Progress
              value={pct}
              className="h-1.5"
              indicatorClassName={utilColor(pct)}
            />
            <span className="whitespace-nowrap text-xs text-muted-foreground">
              {pct}%
            </span>
          </div>
        </TooltipTrigger>
        <TooltipContent>
          {used.toLocaleString()} / {usable.toLocaleString()} IPs used
        </TooltipContent>
      </Tooltip>
    );
  };

  const renderRow = (row: TreeRow) => {
    if (row.kind === "site" && row.site) {
      const s = row.site;
      return (
        <>
          {chevron(row, s.name)}
          <Building2 className="h-4 w-4 shrink-0 text-emerald-400" />
          <span className="truncate font-medium">
            <Highlight text={s.name} q={matchKeys.has(row.key) ? query : ""} />
          </span>
          <span className="shrink-0 text-xs text-muted-foreground">
            {s.vrfs.length} VRF{s.vrfs.length === 1 ? "" : "s"} · {row.count}{" "}
            prefix{row.count === 1 ? "" : "es"}
          </span>
          <div className="ml-auto">{aggBar(row.used ?? 0, row.usable ?? 0)}</div>
        </>
      );
    }
    if (row.kind === "vrf" && row.vrf) {
      const v = row.vrf;
      return (
        <>
          {chevron(row, v.name)}
          <Waypoints className="h-4 w-4 shrink-0 text-cyan-400" />
          <span className="truncate text-sm font-medium">
            <Highlight text={v.name} q={matchKeys.has(row.key) ? query : ""} />
          </span>
          {v.rd && (
            <span className="shrink-0 font-mono text-xs text-muted-foreground">
              RD {v.rd}
            </span>
          )}
          <span className="shrink-0 text-xs text-muted-foreground">
            {row.count} prefix{row.count === 1 ? "" : "es"}
          </span>
          <div className="ml-auto">{aggBar(row.used ?? 0, row.usable ?? 0)}</div>
        </>
      );
    }
    const n = row.node;
    if (!n) return null;
    const q = matchKeys.has(row.key) ? query : "";
    const hasKids = n.children.length > 0;
    return (
      <>
        {chevron(row, n.prefix)}
        <Link
          href={`/prefixes/${n.id}`}
          tabIndex={-1}
          onClick={(e) => e.stopPropagation()}
          className="shrink-0 font-mono text-sm text-emerald-400 hover:underline"
        >
          <Highlight text={n.prefix} q={q} />
        </Link>
        <PrefixStatusBadge s={n.status} />
        {n.vlan_vid != null && (
          <span className="shrink-0 text-xs text-muted-foreground">
            VLAN {n.vlan_vid}
            {n.vlan_name ? ` · ${n.vlan_name}` : ""}
          </span>
        )}
        {n.description && (
          <Tooltip>
            <TooltipTrigger asChild>
              <span className="truncate text-xs text-muted-foreground">
                <Highlight text={n.description} q={q} />
              </span>
            </TooltipTrigger>
            <TooltipContent>{n.description}</TooltipContent>
          </Tooltip>
        )}
        <div className="ml-auto flex shrink-0 items-center gap-2">
          {hasKids ? (
            <Tooltip>
              <TooltipTrigger asChild>
                <div className="flex w-40 items-center gap-2">
                  <Progress
                    value={n.allocated_pct}
                    className="h-1.5"
                    indicatorClassName="bg-sky-500"
                  />
                  <span className="whitespace-nowrap text-xs text-muted-foreground">
                    {n.children.length} subnet
                    {n.children.length === 1 ? "" : "s"} · {n.allocated_pct}%
                  </span>
                </div>
              </TooltipTrigger>
              <TooltipContent>
                {n.descendant_count} descendants · {n.agg_used_ips} IPs tracked
              </TooltipContent>
            </Tooltip>
          ) : (
            <Tooltip>
              <TooltipTrigger asChild>
                <div className="flex w-40 items-center gap-2">
                  <Progress
                    value={n.utilization_pct}
                    className="h-1.5"
                    indicatorClassName={utilColor(n.utilization_pct)}
                  />
                  <span className="whitespace-nowrap text-xs text-muted-foreground">
                    {n.used_ips}/{n.usable_ips} · {n.utilization_pct}%
                  </span>
                </div>
              </TooltipTrigger>
              <TooltipContent>
                {Math.max(0, n.usable_ips - n.used_ips).toLocaleString()} free
              </TooltipContent>
            </Tooltip>
          )}
          <button
            type="button"
            tabIndex={-1}
            aria-label={`Copy ${n.prefix}`}
            onClick={(e) => {
              e.stopPropagation();
              navigator.clipboard?.writeText(n.prefix).catch(() => {});
              toast.success(`Copied ${n.prefix}`);
            }}
            className="flex h-5 w-5 shrink-0 items-center justify-center rounded opacity-0 transition-opacity hover:bg-accent focus-visible:opacity-100 focus-visible:outline-none group-hover:opacity-100"
          >
            <Copy className="h-3 w-3" />
          </button>
        </div>
      </>
    );
  };

  return (
    <div
      ref={parentRef}
      role="tree"
      aria-label="Prefix hierarchy"
      onKeyDown={onKeyDown}
      className="min-h-0 flex-1 overflow-auto rounded-md border"
    >
      <div
        style={{
          height: virtualizer.getTotalSize(),
          position: "relative",
        }}
      >
        {virtualizer.getVirtualItems().map((vi) => {
          const row = rows[vi.index];
          const active = vi.index === activeIndex;
          return (
            <div
              key={vi.key}
              data-idx={vi.index}
              role="treeitem"
              aria-level={row.level}
              aria-setsize={row.setSize}
              aria-posinset={row.posInSet}
              aria-expanded={row.expandable ? isOpen(row.key) : undefined}
              aria-selected={active}
              tabIndex={active ? 0 : -1}
              onClick={() => setActiveIndex(vi.index)}
              className={cn(
                "group absolute left-0 top-0 flex h-9 w-full items-center gap-1.5 pr-3 hover:bg-accent/50 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-inset focus-visible:ring-emerald-500",
                row.kind === "site" && "bg-muted/40",
                row.kind === "vrf" && "bg-muted/20",
                active && "bg-accent/40",
                flash === row.key &&
                  "bg-emerald-500/15 ring-1 ring-inset ring-emerald-400"
              )}
              style={{
                transform: `translateY(${vi.start}px)`,
                paddingLeft: row.depth * 18 + 8,
              }}
            >
              {renderRow(row)}
            </div>
          );
        })}
      </div>
    </div>
  );
}
