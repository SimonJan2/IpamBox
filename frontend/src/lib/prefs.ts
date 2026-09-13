"use client";

import { useEffect, useState } from "react";

// Client-side preferences — stored in localStorage, never sent to the API.

export type ThemeChoice = "dark" | "light" | "system";
export type DensityChoice = "comfortable" | "compact";
export type TsFormat = "local" | "iso";

export interface Prefs {
  theme: ThemeChoice;
  density: DensityChoice;
  pageSize: number;
  landing: string;
  tsFormat: TsFormat;
}

export const DEFAULT_PREFS: Prefs = {
  theme: "dark",
  density: "comfortable",
  pageSize: 50,
  landing: "/",
  tsFormat: "local",
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

function resolveTheme(theme: ThemeChoice): "dark" | "light" {
  if (theme !== "system") return theme;
  if (typeof window === "undefined") return "dark";
  return window.matchMedia("(prefers-color-scheme: light)").matches
    ? "light"
    : "dark";
}

export function applyPrefs(p: Prefs) {
  const root = document.documentElement;
  root.dataset.theme = resolveTheme(p.theme);
  root.dataset.density = p.density;
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
