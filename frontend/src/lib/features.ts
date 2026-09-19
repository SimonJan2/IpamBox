"use client";

import { useEffect, useState } from "react";

import { api } from "@/lib/api";
import type { SettingsOut, SettingsValues } from "@/types";

/**
 * Read a runtime feature flag (Settings > Features). Defaults to false while
 * loading or when the settings endpoint is unreachable — the safe choice for
 * "opt-in" toggles.
 */
export function useFeatureFlag(key: keyof SettingsValues): boolean {
  const [on, setOn] = useState(false);
  useEffect(() => {
    const load = () =>
      api
        .get<SettingsOut>("/api/v1/settings")
        .then((o) => setOn(Boolean(o.values[key])))
        .catch(() => {});
    void load();
    // Backup restore / factory reset can replace feature flags in place.
    window.addEventListener("ipam:refresh", load);
    return () => window.removeEventListener("ipam:refresh", load);
  }, [key]);
  return on;
}
