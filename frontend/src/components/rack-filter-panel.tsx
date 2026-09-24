"use client";

import { useCallback, useId, useMemo } from "react";
import { Search, X } from "lucide-react";

import { foldHebrew } from "@/lib/utils";
import {
  useUrlFlag,
  useUrlSet,
  useUrlTexts,
} from "@/lib/url-state";
import type { Rack, RackGroup, Site } from "@/types";
import {
  FacetOption,
  FacetPill,
  FacetSection,
  toggleIn,
} from "@/components/filter-ui";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

// Every facet is a URL param — bookmarkable, shareable, and the vocabulary
// V5B export endpoints replay server-side.
export const RACK_TEXT_PARAMS = [
  "q",
  "room",
  "min_free_u",
  "max_free_u",
] as const;
export type RackTextParam = (typeof RACK_TEXT_PARAMS)[number];

export const RACK_FILTER_PARAMS = [
  ...RACK_TEXT_PARAMS,
  "site_id",
  "group_id",
  "ungrouped",
  "height_u",
  "occupancy",
] as const;

export const OCCUPANCY_CLASSES = ["empty", "partial", "full"] as const;
export type OccupancyClass = (typeof OCCUPANCY_CLASSES)[number];

/** Occupancy bucket — mirrors `_occupancy` in api/v1/racks.py. */
export function occupancyClass(
  r: Pick<Rack, "used_u" | "height_u">
): OccupancyClass {
  if (r.used_u === 0) return "empty";
  if (r.used_u >= r.height_u) return "full";
  return "partial";
}

export interface RackFilterState {
  texts: Record<RackTextParam, string>;
  setText: (k: RackTextParam, v: string) => void;
  setTextsNow: (patch: Record<string, string | null>) => void;
  siteIds: Set<string>;
  toggleSiteId: (v: string) => void;
  groupIds: Set<string>;
  setGroupIds: (s: Set<string>) => void;
  toggleGroupId: (v: string) => void;
  ungrouped: boolean;
  setUngrouped: (v: boolean) => void;
  heights: Set<string>;
  toggleHeight: (v: string) => void;
  occupancy: Set<string>;
  toggleOccupancy: (v: string) => void;
  activeCount: number;
  clearAll: () => void;
}

/** All racks-page filter state, URL-backed. Lives in the page so the table
 *  filters even with the panel closed; the panel and chips consume it. */
export function useRackFilterState(): RackFilterState {
  const [texts, setText, setTextsNow] =
    useUrlTexts<RackTextParam>(RACK_TEXT_PARAMS);
  const [siteIds, setSiteIds] = useUrlSet("site_id");
  const [groupIds, setGroupIds] = useUrlSet("group_id");
  const [ungrouped, setUngrouped] = useUrlFlag("ungrouped");
  const [heights, setHeights] = useUrlSet("height_u");
  const [occupancy, setOccupancy] = useUrlSet("occupancy");

  const activeCount =
    RACK_TEXT_PARAMS.filter((k) => texts[k] !== "").length +
    (siteIds.size ? 1 : 0) +
    (groupIds.size ? 1 : 0) +
    (ungrouped ? 1 : 0) +
    (heights.size ? 1 : 0) +
    (occupancy.size ? 1 : 0);

  const clearAll = useCallback(
    () =>
      setTextsNow({
        q: null,
        room: null,
        min_free_u: null,
        max_free_u: null,
        site_id: null,
        group_id: null,
        ungrouped: null,
        height_u: null,
        occupancy: null,
      }),
    [setTextsNow]
  );

  // Stable identity so `useMemo(() => filterRacks(rows, f))` only re-runs
  // when a real input changes.
  return useMemo<RackFilterState>(
    () => ({
      texts,
      setText,
      setTextsNow,
      siteIds,
      toggleSiteId: (v) => setSiteIds(toggleIn(siteIds, v)),
      groupIds,
      setGroupIds,
      toggleGroupId: (v) => setGroupIds(toggleIn(groupIds, v)),
      ungrouped,
      setUngrouped,
      heights,
      toggleHeight: (v) => setHeights(toggleIn(heights, v)),
      occupancy,
      toggleOccupancy: (v) => setOccupancy(toggleIn(occupancy, v)),
      activeCount,
      clearAll,
    }),
    [
      texts, setText, setTextsNow, siteIds, groupIds, setGroupIds, ungrouped,
      setUngrouped, heights, occupancy, activeCount, clearAll,
    ]
  );
}

function containsFold(hay: string | null | undefined, needle: string): boolean {
  return hay != null && foldHebrew(hay.toLowerCase()).includes(needle);
}

function numParam(v: string): number | null {
  if (v.trim() === "") return null;
  const n = Number(v);
  return Number.isFinite(n) ? n : null;
}

/** Client-side predicate — mirrors the /racks query params exactly. */
export function filterRacks<T extends Rack>(rows: T[], f: RackFilterState): T[] {
  const t = f.texts;
  const qNeedle = t.q ? foldHebrew(t.q.toLowerCase()) : "";
  const roomNeedle = t.room ? foldHebrew(t.room.toLowerCase()) : "";
  const minFree = numParam(t.min_free_u);
  const maxFree = numParam(t.max_free_u);
  return rows.filter((r) => {
    if (f.siteIds.size && (r.site_id == null || !f.siteIds.has(String(r.site_id))))
      return false;
    if (f.groupIds.size && (r.group_id == null || !f.groupIds.has(String(r.group_id))))
      return false;
    if (f.ungrouped && r.group_id != null) return false;
    if (f.heights.size && !f.heights.has(String(r.height_u))) return false;
    if (f.occupancy.size && !f.occupancy.has(occupancyClass(r))) return false;
    const free = r.height_u - r.used_u;
    if (minFree !== null && free < minFree) return false;
    if (maxFree !== null && free > maxFree) return false;
    if (roomNeedle && !containsFold(r.room, roomNeedle)) return false;
    if (qNeedle) {
      const rr = r as T & { site_name?: string; group_name?: string };
      const hay = [r.name, r.room, r.description, rr.site_name, rr.group_name];
      if (!hay.some((v) => containsFold(v, qNeedle))) return false;
    }
    return true;
  });
}

export function RackFilterPanel({
  f,
  items,
  filtered,
  sites,
  groups,
}: {
  f: RackFilterState;
  items: Rack[];
  filtered: Rack[];
  sites: Site[];
  groups: RackGroup[];
}) {
  const uid = useId();
  const t = f.texts;

  const counts = useMemo(() => {
    const site = new Map<number, number>();
    const group = new Map<number, number>();
    const height = new Map<number, number>();
    const occ = new Map<string, number>();
    const rooms = new Set<string>();
    let ungrouped = 0;
    for (const r of items) {
      if (r.site_id != null)
        site.set(r.site_id, (site.get(r.site_id) ?? 0) + 1);
      if (r.group_id != null)
        group.set(r.group_id, (group.get(r.group_id) ?? 0) + 1);
      else ungrouped++;
      height.set(r.height_u, (height.get(r.height_u) ?? 0) + 1);
      const o = occupancyClass(r);
      occ.set(o, (occ.get(o) ?? 0) + 1);
      if (r.room) rooms.add(r.room);
    }
    return {
      site,
      group,
      height,
      occ,
      ungrouped,
      rooms: [...rooms].sort(),
      heights: [...height.keys()].sort((a, b) => a - b),
    };
  }, [items]);

  const active = f.activeCount > 0;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium">Filters</span>
        {active && (
          <Button
            variant="ghost"
            size="sm"
            className="h-7 px-2"
            onClick={f.clearAll}
          >
            <X className="h-3.5 w-3.5" /> Clear
          </Button>
        )}
      </div>

      <div className="relative">
        <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
        <Input
          value={t.q}
          onChange={(e) => f.setText("q", e.target.value)}
          placeholder="Name, room, site, group…"
          className="pl-8"
          aria-label="Search racks"
        />
      </div>

      {sites.length > 0 && (
        <FacetSection label="Site">
          <div className="max-h-40 space-y-0.5 overflow-auto pr-1">
            {sites.map((s) => (
              <FacetOption
                key={s.id}
                on={f.siteIds.has(String(s.id))}
                dim={(counts.site.get(s.id) ?? 0) === 0}
                onClick={() => f.toggleSiteId(String(s.id))}
                count={counts.site.get(s.id) ?? 0}
              >
                {s.name}
              </FacetOption>
            ))}
          </div>
        </FacetSection>
      )}

      <FacetSection label="Group">
        <div className="max-h-40 space-y-0.5 overflow-auto pr-1">
          <FacetOption
            on={f.ungrouped}
            dim={counts.ungrouped === 0}
            onClick={() => f.setUngrouped(!f.ungrouped)}
            count={counts.ungrouped}
            italic
          >
            ungrouped
          </FacetOption>
          {groups.map((g) => (
            <FacetOption
              key={g.id}
              on={f.groupIds.has(String(g.id))}
              dim={(counts.group.get(g.id) ?? 0) === 0}
              onClick={() => f.toggleGroupId(String(g.id))}
              count={counts.group.get(g.id) ?? 0}
            >
              {g.name}
            </FacetOption>
          ))}
        </div>
      </FacetSection>

      <FacetSection label="Room">
        <Input
          value={t.room}
          onChange={(e) => f.setText("room", e.target.value)}
          placeholder="Room…"
          list={`${uid}-room`}
          aria-label="Room"
          dir="auto"
        />
        <datalist id={`${uid}-room`}>
          {counts.rooms.map((v) => (
            <option key={v} value={v} />
          ))}
        </datalist>
      </FacetSection>

      <FacetSection label="Height">
        <div className="flex flex-wrap gap-1.5">
          {counts.heights.map((h) => (
            <FacetPill
              key={h}
              on={f.heights.has(String(h))}
              onClick={() => f.toggleHeight(String(h))}
              count={counts.height.get(h) ?? 0}
            >
              {h}U
            </FacetPill>
          ))}
        </div>
      </FacetSection>

      <FacetSection label="Occupancy">
        <div className="flex flex-wrap gap-1.5">
          {OCCUPANCY_CLASSES.map((o) => (
            <FacetPill
              key={o}
              on={f.occupancy.has(o)}
              onClick={() => f.toggleOccupancy(o)}
              count={counts.occ.get(o) ?? 0}
            >
              {o}
            </FacetPill>
          ))}
        </div>
      </FacetSection>

      <FacetSection label="Free U">
        <div className="flex items-center gap-2">
          <Input
            type="number"
            min={0}
            value={t.min_free_u}
            onChange={(e) => f.setText("min_free_u", e.target.value)}
            placeholder="min"
            aria-label="Minimum free U"
            className="w-24"
          />
          <span className="text-xs text-muted-foreground">to</span>
          <Input
            type="number"
            min={0}
            value={t.max_free_u}
            onChange={(e) => f.setText("max_free_u", e.target.value)}
            placeholder="max"
            aria-label="Maximum free U"
            className="w-24"
          />
        </div>
      </FacetSection>

      {active && (
        <div className="border-t pt-3 text-xs font-medium text-muted-foreground">
          {filtered.length} matching
        </div>
      )}
    </div>
  );
}
