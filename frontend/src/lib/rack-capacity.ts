/** Rack capacity rollups — the client-side mirror of the API's per-rack
 *  aggregates (services/racks.py:stamp_rack_stats). Used anywhere device
 *  rows need summing: the group row view recomputes optimistically after
 *  cross-rack drags, the detail header shows the "Σ kW · kg" line. */
import type { RackDevice } from "@/types";

/** Σ watts / Σ kg over `devices` — null when nothing supplies a value, so
 *  callers can hide the readout instead of showing a misleading zero. */
export function deviceSums(devices: RackDevice[]): {
  watts: number | null;
  kg: number | null;
} {
  const watts = devices.filter((d) => d.watts != null);
  const kg = devices.filter((d) => d.weight_kg != null);
  return {
    watts: watts.length ? watts.reduce((s, d) => s + (d.watts ?? 0), 0) : null,
    kg: kg.length
      ? Math.round(kg.reduce((s, d) => s + (d.weight_kg ?? 0), 0) * 100) / 100
      : null,
  };
}

/** "1.2 kW" above 1000W, "450 W" below. */
export function formatWatts(w: number): string {
  return w >= 1000 ? `${(w / 1000).toFixed(1).replace(/\.0$/, "")} kW` : `${w} W`;
}

/** "34 kg" / "12.5 kg" — trims a trailing .0. */
export function formatKg(kg: number): string {
  return `${Number.isInteger(kg) ? kg : kg.toFixed(1)} kg`;
}
