"use client";

import { useEffect, useState } from "react";

// Client-side preferences — stored in localStorage, never sent to the API.

export type ThemeChoice =
  | "dark"
  | "light"
  | "localsend"
  | "localsend-dark"
  | "netbox"
  | "netbox-dark"
  | "tokyonight"
  | "tokyonight-storm"
  | "cyberpunk"
  | "system";
/** A concrete theme after "system" resolves. */
export type ResolvedTheme = Exclude<ThemeChoice, "system">;

/** Display metadata for each concrete theme — the appearance dropdown renders
 *  from this (plus a separate "System" entry), and prefs-init maps the active
 *  theme to a sonner light/dark mode via `mode`. */
export const THEMES: readonly {
  value: ResolvedTheme;
  label: string;
  mode: "dark" | "light";
}[] = [
  { value: "cyberpunk", label: "IpamBox Nightwire", mode: "dark" },
  { value: "tokyonight", label: "IpamBox Tokyo Night", mode: "dark" },
  { value: "tokyonight-storm", label: "IpamBox Tokyo Night Storm", mode: "dark" },
  { value: "dark", label: "IpamBox Dark", mode: "dark" },
  { value: "light", label: "IpamBox Light", mode: "light" },
  { value: "localsend", label: "LocalSend Mint", mode: "light" },
  { value: "localsend-dark", label: "LocalSend Dark", mode: "dark" },
  { value: "netbox", label: "NetBox Light", mode: "light" },
  { value: "netbox-dark", label: "NetBox Dark", mode: "dark" },
];
export type DensityChoice = "comfortable" | "compact";
export type TsFormat = "local" | "iso";
export type AddrMapView = "grid" | "list";

/** A named, stored filter state for one page — `query` is the literal
 *  URLSearchParams string that reproduces the view. */
export interface SavedView {
  name: string;
  query: string;
}

/** Ambient-effects master level — "full" everything on, "calm" keeps the
 *  static ambience but kills motion, "off" strips ambient layers too. */
export type FxLevel = "full" | "calm" | "off";

export interface Prefs {
  theme: ThemeChoice;
  density: DensityChoice;
  fx: FxLevel;
  fxStars: boolean;
  fxGrain: boolean;
  fxSpin: boolean;
  /** Cyberpunk-specific effect switches. */
  fxScanlines: boolean;
  fxGlitch: boolean;
  fxHud: boolean;
  pageSize: number;
  landing: string;
  tsFormat: TsFormat;
  addrMapView: AddrMapView;
  showSlugs: boolean;
  sidebarCollapsed: boolean;
  /** Sidebar group label -> expanded; missing key means expanded. */
  sidebarGroups: Record<string, boolean>;
  /** Recent command-palette picks, newest first (max 5). */
  searchRecent: { label: string; href: string }[];
  /** Per-page named saved views (page key -> presets). */
  savedViews: Record<string, SavedView[]>;
}

export const DEFAULT_PREFS: Prefs = {
  theme: "cyberpunk",
  density: "comfortable",
  fx: "full",
  fxStars: true,
  fxGrain: true,
  fxSpin: true,
  fxScanlines: true,
  fxGlitch: true,
  fxHud: true,
  pageSize: 50,
  landing: "/",
  tsFormat: "local",
  addrMapView: "grid",
  showSlugs: false,
  sidebarCollapsed: false,
  sidebarGroups: {},
  searchRecent: [],
  savedViews: {},
};

const KEY = "ipambox:prefs";
const EVENT = "ipam:prefs-changed";

export function getPrefs(): Prefs {
  if (typeof window === "undefined") return DEFAULT_PREFS;
  try {
    const raw = window.localStorage.getItem(KEY);
    return { ...DEFAULT_PREFS, ...(raw ? JSON.parse(raw) : {}) };
  } catch {
    return DEFAULT_PREFS;
  }
}

export function savePrefs(patch: Partial<Prefs>): Prefs {
  const next = { ...getPrefs(), ...patch };
  window.localStorage.setItem(KEY, JSON.stringify(next));
  window.dispatchEvent(new Event(EVENT));
  return next;
}

export function resolveTheme(theme: ThemeChoice): ResolvedTheme {
  if (theme !== "system") return theme;
  if (typeof window === "undefined") return "dark";
  return window.matchMedia("(prefers-color-scheme: light)").matches
    ? "light"
    : "cyberpunk";
}

export function applyPrefs(p: Prefs) {
  const root = document.documentElement;
  root.dataset.theme = resolveTheme(p.theme);
  root.dataset.density = p.density;
  root.dataset.fx = p.fx;
  root.dataset.fxStars = p.fxStars ? "1" : "0";
  root.dataset.fxGrain = p.fxGrain ? "1" : "0";
  root.dataset.fxSpin = p.fxSpin ? "1" : "0";
  root.dataset.fxScanlines = p.fxScanlines ? "1" : "0";
  root.dataset.fxGlitch = p.fxGlitch ? "1" : "0";
  root.dataset.fxHud = p.fxHud ? "1" : "0";
}

/** Applies prefs to <html> and keeps them live (system theme + cross-page). */
export function useApplyPrefs() {
  useEffect(() => {
    const apply = () => applyPrefs(getPrefs());
    apply();
    const mq = window.matchMedia("(prefers-color-scheme: light)");
    mq.addEventListener("change", apply);
    window.addEventListener(EVENT, apply);
    return () => {
      mq.removeEventListener("change", apply);
      window.removeEventListener(EVENT, apply);
    };
  }, []);
}

export function usePrefs(): [Prefs, (patch: Partial<Prefs>) => void] {
  const [prefs, setPrefs] = useState<Prefs>(DEFAULT_PREFS);
  useEffect(() => {
    setPrefs(getPrefs());
    const onChange = () => setPrefs(getPrefs());
    window.addEventListener(EVENT, onChange);
    return () => window.removeEventListener(EVENT, onChange);
  }, []);
  return [prefs, savePrefs];
}

/** Format a timestamp honoring the tsFormat pref. */
export function fmtTs(iso: string | null | undefined, p?: Prefs): string {
  if (!iso) return "—";
  const d = new Date(iso);
  if (isNaN(d.getTime())) return iso;
  const prefs = p ?? getPrefs();
  return prefs.tsFormat === "iso"
    ? d.toISOString().replace("T", " ").replace(/\.\d+Z$/, " UTC")
    : d.toLocaleString();
}
