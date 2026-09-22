"use client";

import { useEffect, useState } from "react";

import { api } from "@/lib/api";
import type { SettingsOut, SettingsValues } from "@/types";

// Shared settings fetch: concurrent consumers (e.g. one ExpiryBadge per table
// row) ride a single in-flight request instead of each firing their own.
let cache: SettingsValues | undefined;
let inflight: Promise<void> | undefined;
const listeners = new Set<() => void>();

function load() {
  inflight ??= api
    .get<SettingsOut>("/api/v1/settings")
    .then((o) => {
      cache = o.values;
      listeners.forEach((f) => f());
    })
    .catch(() => {})
    .finally(() => {
      inflight = undefined;
    });
}

/**
 * Read a runtime setting (Settings pages). Undefined while loading or when
 * the settings endpoint is unreachable — callers should fall back to the
 * documented default.
 */
export function useSetting<K extends keyof SettingsValues>(
  key: K
): SettingsValues[K] | undefined {
  const [val, setVal] = useState<SettingsValues[K] | undefined>(cache?.[key]);
  useEffect(() => {
    const apply = () => setVal(cache?.[key]);
    listeners.add(apply);
    load();
    // Backup restore / factory reset can replace feature flags in place.
    window.addEventListener("ipam:refresh", load);
    return () => {
      listeners.delete(apply);
      window.removeEventListener("ipam:refresh", load);
    };
  }, [key]);
  return val;
}

/**
 * Read a runtime feature flag (Settings > Features). Defaults to false while
 * loading or when the settings endpoint is unreachable — the safe choice for
 * "opt-in" toggles.
 */
export function useFeatureFlag(key: keyof SettingsValues): boolean {
  return Boolean(useSetting(key));
}
