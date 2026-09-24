"use client";

import { useCallback, useId, useMemo } from "react";
import { Search, X } from "lucide-react";

import { STATUS_TOKENS } from "@/lib/status-tokens";
import { foldHebrew } from "@/lib/utils";
import {
  useUrlFlag,
  useUrlParam,
  useUrlSet,
  useUrlTexts,
} from "@/lib/url-state";
import type { Device, IpStatus, Rack, RackGroup, Site } from "@/types";
import {
  FacetOption,
  FacetPill,
  FacetSection,
  toggleIn,
} from "@/components/filter-ui";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

// Every facet is a URL param — a filtered view is bookmarkable/shareable and
// V5B export endpoints replay this exact vocabulary server-side.
export const DEVICE_TEXT_PARAMS = [
  "q",
  "manufacturer",
  "model",
  "category",
  "device_type",
] as const;
export type DeviceTextParam = (typeof DEVICE_TEXT_PARAMS)[number];

export const DEVICE_FILTER_PARAMS = [
  ...DEVICE_TEXT_PARAMS,
  "health",
  "unracked",
  "mounted",
  "site_id",
  "rack_id",
  "group_id",
  "source",
  "face",
  "has_ip",
  "wiring",
] as const;

export type HealthFacet = IpStatus | "unmonitored";
const HEALTHS: HealthFacet[] = [
  "active",
  "reserved",
  "dhcp",
  "discovered",
  "offline",
  "unmonitored",
];
const FACES = ["front", "rear", "both"] as const;
export const WIRING_CLASSES = ["cabled", "partial", "uncabled"] as const;
export type WiringClass = (typeof WIRING_CLASSES)[number];

const TEXT_FACETS: { key: DeviceTextParam; label: string }[] = [
  { key: "manufacturer", label: "Manufacturer" },
  { key: "model", label: "Model" },
  { key: "category", label: "Category" },
  { key: "device_type", label: "Device type" },
];

/** L1 wiring class — mirrors `_wiring_class` in api/v1/devices.py. A device
 *  with no interfaces is "uncabled" (zero cabled ports is zero cabled). */
export function wiringClass(
  d: Pick<Device, "interface_count" | "cabled_count">
): WiringClass {
  if (d.cabled_count === 0) return "uncabled";
  if (d.cabled_count >= d.interface_count) return "cabled";
  return "partial";
}

export interface DeviceFilterState {
  texts: Record<DeviceTextParam, string>;
  setText: (k: DeviceTextParam, v: string) => void;
  setTextsNow: (patch: Record<string, string | null>) => void;
  health: Set<string>;
  toggleHealth: (v: string) => void;
  unracked: string; // "" | "1" | "0" — tri-state (racked when "0")
  setUnracked: (v: string) => void;
  mounted: boolean;
  setMounted: (v: boolean) => void;
  siteIds: Set<string>;
  toggleSiteId: (v: string) => void;
  rackIds: Set<string>;
  toggleRackId: (v: string) => void;
  groupIds: Set<string>;
  toggleGroupId: (v: string) => void;
  sources: Set<string>;
  toggleSource: (v: string) => void;
  faces: Set<string>;
  toggleFace: (v: string) => void;
  hasIp: string; // "" | "1" | "0"
  setHasIp: (v: string) => void;
  wiring: Set<string>;
  toggleWiring: (v: string) => void;
  activeCount: number;
  clearAll: () => void;
}

/** All device-page filter state, URL-backed. Lives in the page so the table
 *  filters even with the panel closed; the panel and chips consume it. */
export function useDeviceFilterState(): DeviceFilterState {
  const [texts, setText, setTextsNow] =
    useUrlTexts<DeviceTextParam>(DEVICE_TEXT_PARAMS);
  const [health, setHealth] = useUrlSet("health");
  const [unracked, setUnracked] = useUrlParam("unracked");
  const [mounted, setMounted] = useUrlFlag("mounted");
  const [siteIds, setSiteIds] = useUrlSet("site_id");
  const [rackIds, setRackIds] = useUrlSet("rack_id");
  const [groupIds, setGroupIds] = useUrlSet("group_id");
  const [sources, setSources] = useUrlSet("source");
  const [faces, setFaces] = useUrlSet("face");
  const [hasIp, setHasIp] = useUrlParam("has_ip");
  const [wiring, setWiring] = useUrlSet("wiring");

  const activeCount =
    DEVICE_TEXT_PARAMS.filter((k) => texts[k] !== "").length +
    (health.size ? 1 : 0) +
    (unracked !== "" ? 1 : 0) +
    (mounted ? 1 : 0) +
    (siteIds.size ? 1 : 0) +
    (rackIds.size ? 1 : 0) +
    (groupIds.size ? 1 : 0) +
    (sources.size ? 1 : 0) +
    (faces.size ? 1 : 0) +
    (hasIp !== "" ? 1 : 0) +
    (wiring.size ? 1 : 0);

  const clearAll = useCallback(
    () =>
      setTextsNow({
        q: null,
        manufacturer: null,
        model: null,
        category: null,
        device_type: null,
        health: null,
        unracked: null,
        mounted: null,
        site_id: null,
        rack_id: null,
        group_id: null,
        source: null,
        face: null,
        has_ip: null,
        wiring: null,
      }),
    [setTextsNow]
  );

  // Stable identity so `useMemo(() => filterDevices(rows, f, …))` only
  // re-runs when a real input changes.
  return useMemo<DeviceFilterState>(
    () => ({
      texts,
      setText,
      setTextsNow,
      health,
      toggleHealth: (v) => setHealth(toggleIn(health, v)),
      unracked,
      setUnracked,
      mounted,
      setMounted,
      siteIds,
      toggleSiteId: (v) => setSiteIds(toggleIn(siteIds, v)),
      rackIds,
      toggleRackId: (v) => setRackIds(toggleIn(rackIds, v)),
      groupIds,
      toggleGroupId: (v) => setGroupIds(toggleIn(groupIds, v)),
      sources,
      toggleSource: (v) => setSources(toggleIn(sources, v)),
      faces,
      toggleFace: (v) => setFaces(toggleIn(faces, v)),
      hasIp,
      setHasIp,
      wiring,
      toggleWiring: (v) => setWiring(toggleIn(wiring, v)),
      activeCount,
      clearAll,
    }),
    [
      texts, setText, setTextsNow, health, unracked, setUnracked, mounted,
      setMounted, siteIds, rackIds, groupIds, sources, faces, hasIp, setHasIp,
      wiring, activeCount, clearAll,
    ]
  );
}

function containsFold(hay: string | null | undefined, needle: string): boolean {
  return hay != null && foldHebrew(hay.toLowerCase()).includes(needle);
}

/** Client-side predicate — mirrors the /devices query params exactly, so a
 *  filtered URL means the same set here and (for V5B) on the export side. */
export function filterDevices<T extends Device>(
  rows: T[],
  f: DeviceFilterState,
  rackGroup: Map<number, number | null>
): T[] {
  const t = f.texts;
  const qNeedle = t.q ? foldHebrew(t.q.toLowerCase()) : "";
  const subs: [DeviceTextParam, (d: T) => string | null][] = [
    ["manufacturer", (d) => d.manufacturer],
    ["model", (d) => d.model],
    ["category", (d) => d.category],
    ["device_type", (d) => d.device_type],
  ];
  return rows.filter((d) => {
    if (f.unracked === "1" && d.rack_id != null) return false;
    if (f.unracked === "0" && d.rack_id == null) return false;
    if (f.mounted && d.carrier_id == null) return false;
    if (f.health.size && !f.health.has(d.health ?? "unmonitored"))
      return false;
    if (f.siteIds.size && (d.site_id == null || !f.siteIds.has(String(d.site_id))))
      return false;
    if (f.rackIds.size && (d.rack_id == null || !f.rackIds.has(String(d.rack_id))))
      return false;
    if (f.groupIds.size) {
      const g = d.rack_id != null ? rackGroup.get(d.rack_id) : null;
      if (g == null || !f.groupIds.has(String(g))) return false;
    }
    if (f.sources.size && !f.sources.has(d.source)) return false;
    // face defaults to "front" even when unracked — the facet means
    // "placement face", so it only applies to placed devices.
    if (
      f.faces.size &&
      (d.rack_id == null || d.face == null || !f.faces.has(d.face))
    )
      return false;
    if (f.hasIp === "1" && d.ip_count === 0) return false;
    if (f.hasIp === "0" && d.ip_count > 0) return false;
    if (f.wiring.size && !f.wiring.has(wiringClass(d))) return false;
    for (const [k, field] of subs) {
      if (t[k] && !containsFold(field(d), foldHebrew(t[k].toLowerCase())))
        return false;
    }
    if (qNeedle) {
      const r = d as T & { rack_name?: string; site_name?: string };
      const hay = [
        d.name,
        d.device_type,
        d.serial_number,
        d.manufacturer,
        d.model,
        d.mac_address,
        d.category,
        r.rack_name,
        r.site_name,
        d.notes,
      ];
      if (!hay.some((v) => containsFold(v, qNeedle))) return false;
    }
    return true;
  });
}

export function DeviceFilterPanel({
  f,
  items,
  filtered,
  sites,
  racks,
  groups,
  rackGroup,
}: {
  f: DeviceFilterState;
  items: Device[];
  filtered: Device[];
  sites: Site[];
  racks: Rack[];
  groups: RackGroup[];
  /** rack_id -> group_id, for counting devices per rack group. */
  rackGroup: Map<number, number | null>;
}) {
  const uid = useId();
  const t = f.texts;

  const counts = useMemo(() => {
    const health = new Map<string, number>();
    const site = new Map<number, number>();
    const rack = new Map<number, number>();
    const group = new Map<number, number>();
    const source = new Map<string, number>();
    const face = new Map<string, number>();
    const wiring = new Map<string, number>();
    let racked = 0,
      unracked = 0,
      mounted = 0,
      hasIp = 0;
    for (const d of items) {
      const h = d.health ?? "unmonitored";
      health.set(h, (health.get(h) ?? 0) + 1);
      if (d.rack_id != null) racked++;
      else unracked++;
      if (d.carrier_id != null) mounted++;
      if (d.site_id != null)
        site.set(d.site_id, (site.get(d.site_id) ?? 0) + 1);
      if (d.rack_id != null) {
        rack.set(d.rack_id, (rack.get(d.rack_id) ?? 0) + 1);
        const g = rackGroup.get(d.rack_id);
        if (g != null) group.set(g, (group.get(g) ?? 0) + 1);
      }
      source.set(d.source, (source.get(d.source) ?? 0) + 1);
      // face is a placement facet — unracked rows carry a stale/default
      // face that the predicate ignores, so don't count them either.
      if (d.rack_id != null && d.face != null)
        face.set(d.face, (face.get(d.face) ?? 0) + 1);
      if (d.ip_count > 0) hasIp++;
      const w = wiringClass(d);
      wiring.set(w, (wiring.get(w) ?? 0) + 1);
    }
    return {
      health,
      site,
      rack,
      group,
      source,
      face,
      wiring,
      racked,
      unracked,
      mounted,
      hasIp,
      noIp: items.length - hasIp,
    };
  }, [items, rackGroup]);

  const datalists = useMemo(() => {
    const out = {} as Record<DeviceTextParam, string[]>;
    for (const { key } of TEXT_FACETS) {
      const vals = new Set<string>();
      for (const d of items) {
        const v = d[key as keyof Device];
        if (typeof v === "string" && v) vals.add(v);
      }
      out[key] = [...vals].sort();
    }
    return out;
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
          placeholder="Name, model, serial, MAC, site…"
          className="pl-8"
          aria-label="Search devices"
        />
      </div>

      <FacetSection label="Health">
        <div className="flex flex-wrap gap-1.5">
          {HEALTHS.map((h) => (
            <FacetPill
              key={h}
              on={f.health.has(h)}
              onClick={() => f.toggleHealth(h)}
              dot={
                h === "unmonitored"
                  ? "border border-dashed border-muted-foreground"
                  : STATUS_TOKENS[h].dot
              }
              count={counts.health.get(h) ?? 0}
            >
              {h}
            </FacetPill>
          ))}
        </div>
      </FacetSection>

      <FacetSection label="Placement">
        <div className="flex flex-wrap gap-1.5">
          <FacetPill
            on={f.unracked === "0"}
            onClick={() => f.setUnracked(f.unracked === "0" ? "" : "0")}
            count={counts.racked}
          >
            racked
          </FacetPill>
          <FacetPill
            on={f.unracked === "1"}
            onClick={() => f.setUnracked(f.unracked === "1" ? "" : "1")}
            count={counts.unracked}
          >
            unracked
          </FacetPill>
          <FacetPill
            on={f.mounted}
            onClick={() => f.setMounted(!f.mounted)}
            count={counts.mounted}
          >
            in carrier
          </FacetPill>
        </div>
      </FacetSection>

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

      {racks.length > 0 && (
        <FacetSection label="Rack">
          <div className="max-h-40 space-y-0.5 overflow-auto pr-1">
            {racks.map((r) => (
              <FacetOption
                key={r.id}
                on={f.rackIds.has(String(r.id))}
                dim={(counts.rack.get(r.id) ?? 0) === 0}
                onClick={() => f.toggleRackId(String(r.id))}
                count={counts.rack.get(r.id) ?? 0}
              >
                {r.name}
              </FacetOption>
            ))}
          </div>
        </FacetSection>
      )}

      {groups.length > 0 && (
        <FacetSection label="Rack group">
          <div className="max-h-40 space-y-0.5 overflow-auto pr-1">
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
      )}

      <FacetSection label="Attributes">
        <div className="space-y-2">
          {TEXT_FACETS.map(({ key, label }) => (
            <div key={key}>
              <Input
                value={t[key]}
                onChange={(e) => f.setText(key, e.target.value)}
                placeholder={`${label}…`}
                list={`${uid}-${key}`}
                aria-label={label}
                dir="auto"
              />
              <datalist id={`${uid}-${key}`}>
                {datalists[key].map((v) => (
                  <option key={v} value={v} />
                ))}
              </datalist>
            </div>
          ))}
        </div>
      </FacetSection>

      {counts.source.size > 0 && (
        <FacetSection label="Source">
          <div className="space-y-0.5">
            {[...counts.source.keys()].sort().map((s) => (
              <FacetOption
                key={s}
                on={f.sources.has(s)}
                onClick={() => f.toggleSource(s)}
                count={counts.source.get(s) ?? 0}
              >
                {s}
              </FacetOption>
            ))}
          </div>
        </FacetSection>
      )}

      <FacetSection label="Face">
        <div className="flex flex-wrap gap-1.5">
          {FACES.map((face) => (
            <FacetPill
              key={face}
              on={f.faces.has(face)}
              onClick={() => f.toggleFace(face)}
              count={counts.face.get(face) ?? 0}
            >
              {face}
            </FacetPill>
          ))}
        </div>
      </FacetSection>

      <FacetSection label="IP addresses">
        <div className="flex flex-wrap gap-1.5">
          <FacetPill
            on={f.hasIp === "1"}
            onClick={() => f.setHasIp(f.hasIp === "1" ? "" : "1")}
            count={counts.hasIp}
          >
            has IPs
          </FacetPill>
          <FacetPill
            on={f.hasIp === "0"}
            onClick={() => f.setHasIp(f.hasIp === "0" ? "" : "0")}
            count={counts.noIp}
          >
            no IPs
          </FacetPill>
        </div>
      </FacetSection>

      <FacetSection label="Wiring">
        <div className="flex flex-wrap gap-1.5">
          {WIRING_CLASSES.map((w) => (
            <FacetPill
              key={w}
              on={f.wiring.has(w)}
              onClick={() => f.toggleWiring(w)}
              count={counts.wiring.get(w) ?? 0}
            >
              {w}
            </FacetPill>
          ))}
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
