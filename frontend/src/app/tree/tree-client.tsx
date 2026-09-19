"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { FoldVertical, Network, Search, UnfoldVertical } from "lucide-react";
import { toast } from "sonner";

import { api } from "@/lib/api";
import { cn, foldHebrew } from "@/lib/utils";
import {
  parseCsvSet,
  useUrlParam,
  useUrlParams,
  useUrlText,
} from "@/lib/url-state";
import type { PrefixNode, PrefixStatus, SiteNode, VrfNode } from "@/types";
import {
  PrefixTree,
  collectExpandableKeys,
  prefixKey,
  siteKey,
  vrfKey,
} from "@/components/prefix-tree";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/separator";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

const ALL_STATUSES: PrefixStatus[] = [
  "container",
  "active",
  "reserved",
  "deprecated",
];
const EXPAND_KEY = "ipambox:tree-expanded";

const siteText = (s: SiteNode) => `${s.name} ${s.slug ?? ""}`;
const vrfText = (v: VrfNode) => `${v.name} ${v.rd ?? ""}`;
const prefixText = (n: PrefixNode) =>
  `${n.prefix} ${n.description ?? ""} ${n.vlan_name ?? ""} ${n.vlan_vid ?? ""}`;

export default function TreePage() {
  const [tree, setTree] = useState<SiteNode[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [q, setQ] = useUrlText("q");
  const { searchParams, setParams } = useUrlParams();
  const statusParam = searchParams.get("status");
  // Absent param = all statuses on; "none" = everything off (kept distinct so
  // an all-off URL stays meaningful instead of resetting).
  const statuses = useMemo<Set<PrefixStatus>>(
    () =>
      statusParam === null
        ? new Set(ALL_STATUSES)
        : statusParam === "none"
          ? new Set()
          : parseCsvSet<PrefixStatus>(statusParam),
    [statusParam]
  );
  const setStatuses = (
    s: Set<PrefixStatus> | ((p: Set<PrefixStatus>) => Set<PrefixStatus>)
  ) => {
    const next = typeof s === "function" ? s(statuses) : s;
    setParams({
      status:
        next.size === ALL_STATUSES.length
          ? null
          : next.size === 0
            ? "none"
            : [...next].join(","),
    });
  };
  const [vrfFilter, setVrfFilter] = useUrlParam("vrf", "all");
  const [expanded, setExpanded] = useState<Set<string> | null>(null);
  const [flashKey, setFlashKey] = useState<string | null>(null);
  const focusDone = useRef(false);
  const searchRef = useRef<HTMLInputElement>(null);

  const load = useCallback(() => {
    setError(null);
    api
      .get<SiteNode[]>("/api/v1/prefixes/tree")
      .then(setTree)
      .catch((e) => {
        setError(String(e));
        toast.error("Failed to load hierarchy", { description: String(e) });
      });
  }, []);
  useEffect(load, [load]);

  // Initialize expansion: stored keys win; otherwise open sites + VRFs so the
  // first view shows every root prefix without flooding the screen.
  useEffect(() => {
    if (!tree || expanded !== null) return;
    let stored: unknown = null;
    try {
      stored = JSON.parse(localStorage.getItem(EXPAND_KEY) || "null");
    } catch {}
    if (Array.isArray(stored)) {
      setExpanded(new Set(stored.filter((k) => typeof k === "string")));
      return;
    }
    const keys = new Set<string>();
    for (const s of tree) {
      keys.add(siteKey(s.id));
      for (const v of s.vrfs) if (v.prefixes.length > 0) keys.add(vrfKey(v.id));
    }
    setExpanded(keys);
  }, [tree, expanded]);

  useEffect(() => {
    if (expanded === null) return;
    try {
      localStorage.setItem(EXPAND_KEY, JSON.stringify([...expanded]));
    } catch {}
  }, [expanded]);

  // Deep link: /tree?focus=<prefix_id> expands ancestors and flashes the row.
  useEffect(() => {
    if (!tree || expanded === null || focusDone.current) return;
    focusDone.current = true;
    const id = Number(new URLSearchParams(window.location.search).get("focus"));
    if (!id) return;
    const ancestors: string[] = [];
    let found = false;
    const walk = (n: PrefixNode, path: string[]) => {
      if (found) return;
      if (n.id === id) {
        ancestors.push(...path);
        found = true;
        return;
      }
      n.children.forEach((c) => walk(c, [...path, prefixKey(n.id)]));
    };
    for (const s of tree)
      for (const v of s.vrfs)
        v.prefixes.forEach((p) => walk(p, [siteKey(s.id), vrfKey(v.id)]));
    if (!found) return;
    setExpanded((prev) => new Set([...(prev ?? []), ...ancestors]));
    setFlashKey(prefixKey(id));
  }, [tree, expanded]);

  // "/" focuses search from anywhere on the page.
  useEffect(() => {
    const h = (e: KeyboardEvent) => {
      if (e.key !== "/") return;
      const t = e.target as HTMLElement;
      if (t.closest("input, textarea, select, [contenteditable]")) return;
      e.preventDefault();
      searchRef.current?.focus();
    };
    window.addEventListener("keydown", h);
    return () => window.removeEventListener("keydown", h);
  }, []);

  const toggle = useCallback((key: string) => {
    setExpanded((prev) => {
      const next = new Set(prev ?? []);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
  }, []);

  const statusAll = statuses.size === ALL_STATUSES.length;
  const query = q.trim();
  const filterActive = query !== "" || !statusAll || vrfFilter !== "all";

  // Restrict structure to the selected VRF before search/status visibility.
  const scoped = useMemo(() => {
    if (!tree) return [];
    if (vrfFilter === "all") return tree;
    return tree
      .map((s) => ({
        ...s,
        vrfs: s.vrfs.filter((v) => String(v.id) === vrfFilter),
      }))
      .filter((s) => s.vrfs.length > 0);
  }, [tree, vrfFilter]);

  // Row visibility: a row shows when it matches, an ancestor matched, or it is
  // on the path to a match. Status filtering only applies to prefix rows.
  const { visible, matched } = useMemo(() => {
    const vis = new Set<string>();
    const mat = new Set<string>();
    if (!filterActive) return { visible: null, matched: mat };
    const fold = (s: string) => foldHebrew(s.toLowerCase());
    const qq = fold(query);
    const hit = (s: string) => qq === "" || fold(s).includes(qq);

    for (const s of scoped) {
      const sSelf = hit(siteText(s));
      if (sSelf && qq) mat.add(siteKey(s.id));
      let siteVis = false;
      for (const v of s.vrfs) {
        const vSelf = hit(vrfText(v));
        if (vSelf && qq) mat.add(vrfKey(v.id));
        let vrfVis = false;
        const walk = (n: PrefixNode, ancMatch: boolean): boolean => {
          const self = hit(prefixText(n));
          const statusOk = statusAll || statuses.has(n.status);
          if (self && qq && statusOk) mat.add(prefixKey(n.id));
          const am = ancMatch || self;
          let kidsVis = false;
          for (const c of n.children) kidsVis = walk(c, am) || kidsVis;
          const show = statusOk && (am || kidsVis);
          if (show) vis.add(prefixKey(n.id));
          return show;
        };
        for (const p of v.prefixes) if (walk(p, sSelf || vSelf)) vrfVis = true;
        if (sSelf || vSelf || vrfVis) {
          vis.add(vrfKey(v.id));
          siteVis = true;
        }
      }
      if (sSelf || siteVis) vis.add(siteKey(s.id));
    }
    return { visible: vis, matched: mat };
  }, [scoped, query, statuses, statusAll, filterActive]);

  const totals = useMemo(() => {
    let vrfs = 0;
    let prefixes = 0;
    const count = (n: PrefixNode): number =>
      1 + n.children.reduce((a, c) => a + count(c), 0);
    for (const s of tree ?? [])
      for (const v of s.vrfs) {
        vrfs++;
        prefixes += v.prefixes.reduce((a, p) => a + count(p), 0);
      }
    return { sites: tree?.length ?? 0, vrfs, prefixes };
  }, [tree]);

  const allVrfs = useMemo(
    () =>
      (tree ?? []).flatMap((s) =>
        s.vrfs.map((v) => ({ id: v.id, label: `${v.name} (${s.name})` }))
      ),
    [tree]
  );

  const collapseToDepth = (value: string) => {
    if (!tree) return;
    const keys = collectExpandableKeys(tree);
    if (value === "all") {
      setExpanded(new Set(keys.keys()));
      return;
    }
    const d = Number(value);
    setExpanded(
      new Set([...keys].filter(([, dep]) => dep < d).map(([k]) => k))
    );
  };

  const matchCount = matched.size;

  return (
    <div className="flex h-[calc(100dvh-8rem)] flex-col gap-4">
      <div className="flex items-center justify-between">
        <h1 className="flex items-center gap-2 text-xl font-semibold">
          <Network className="h-5 w-5 text-emerald-400" /> Prefix hierarchy
          {tree && (
            <span className="ml-2 text-sm font-normal text-muted-foreground">
              {totals.sites} sites · {totals.vrfs} VRFs · {totals.prefixes}{" "}
              prefixes
            </span>
          )}
        </h1>
        <div className="flex items-center gap-2">
          <Select onValueChange={collapseToDepth}>
            <SelectTrigger className="w-44" aria-label="Expand to depth">
              <SelectValue placeholder="Expand to depth…" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="1">Sites only</SelectItem>
              <SelectItem value="2">+ VRFs</SelectItem>
              <SelectItem value="3">+ 1 prefix level</SelectItem>
              <SelectItem value="4">+ 2 prefix levels</SelectItem>
              <SelectItem value="5">+ 3 prefix levels</SelectItem>
              <SelectItem value="all">Everything</SelectItem>
            </SelectContent>
          </Select>
          <Button
            size="icon"
            variant="outline"
            aria-label="Expand all"
            title="Expand all"
            onClick={() =>
              tree && setExpanded(new Set(collectExpandableKeys(tree).keys()))
            }
          >
            <UnfoldVertical className="h-4 w-4" />
          </Button>
          <Button
            size="icon"
            variant="outline"
            aria-label="Collapse all"
            title="Collapse all"
            onClick={() => setExpanded(new Set())}
          >
            <FoldVertical className="h-4 w-4" />
          </Button>
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <div className="relative">
          <Search className="absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
          <Input
            ref={searchRef}
            placeholder="Search prefixes, VLANs, VRFs, sites…  ( / )"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            className="w-80 pl-8"
            aria-label="Search hierarchy"
          />
        </div>
        <div className="flex items-center gap-1.5" role="group" aria-label="Status filter">
          {ALL_STATUSES.map((s) => (
            <button
              key={s}
              type="button"
              aria-pressed={statuses.has(s)}
              onClick={() =>
                setStatuses((prev) => {
                  const next = new Set(prev);
                  if (next.has(s)) next.delete(s);
                  else next.add(s);
                  return next;
                })
              }
              className={cn(
                "rounded-full border px-2.5 py-0.5 text-xs capitalize transition-colors",
                statuses.has(s)
                  ? "border-emerald-500/40 bg-emerald-500/15 text-emerald-300"
                  : "border-border text-muted-foreground hover:text-foreground"
              )}
            >
              {s}
            </button>
          ))}
        </div>
        <Select value={vrfFilter} onValueChange={setVrfFilter}>
          <SelectTrigger className="w-52" aria-label="Filter by VRF">
            <SelectValue placeholder="All VRFs" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All VRFs</SelectItem>
            {allVrfs.map((v) => (
              <SelectItem key={v.id} value={String(v.id)}>
                {v.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        {filterActive && query !== "" && (
          <span className="text-xs text-muted-foreground">
            {matchCount} match{matchCount === 1 ? "" : "es"}
          </span>
        )}
      </div>

      {tree === null && !error && (
        <div className="space-y-1.5">
          {Array.from({ length: 10 }).map((_, i) => (
            <Skeleton key={i} className="h-9 w-full" />
          ))}
        </div>
      )}

      {error && (
        <Card>
          <CardContent className="flex items-center justify-between py-6">
            <p className="text-sm text-muted-foreground">
              Couldn&apos;t load the hierarchy — {error}
            </p>
            <Button size="sm" variant="outline" onClick={load}>
              Retry
            </Button>
          </CardContent>
        </Card>
      )}

      {tree && tree.length === 0 && (
        <p className="text-sm text-muted-foreground">
          Nothing here yet — create a site and prefixes.
        </p>
      )}

      {tree && tree.length > 0 && expanded !== null && (
        <>
          {visible !== null && visible.size === 0 ? (
            <p className="text-sm text-muted-foreground">
              No prefixes match the current filters.{" "}
              <button
                type="button"
                className="text-emerald-400 hover:underline"
                onClick={() => {
                  setQ("");
                  setStatuses(new Set(ALL_STATUSES));
                  setVrfFilter("all");
                }}
              >
                Clear filters
              </button>
            </p>
          ) : (
            <PrefixTree
              sites={scoped}
              expanded={expanded}
              onToggle={toggle}
              visible={visible}
              matchKeys={matched}
              query={query}
              flashKey={flashKey}
            />
          )}
        </>
      )}
    </div>
  );
}
