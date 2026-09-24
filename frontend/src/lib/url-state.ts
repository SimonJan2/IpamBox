"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { SortingState } from "@tanstack/react-table";

// Filter/sort/view state lives in the query string so views are shareable and
// survive reload + Back/Forward. Discrete changes push a history entry (Back
// undoes them); scroll is never reset.

export function useUrlParams() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const pathname = usePathname();

  const setParams = useCallback(
    (
      patch: Record<string, string | null | undefined>,
      mode: "push" | "replace" = "push"
    ) => {
      const next = new URLSearchParams(searchParams.toString());
      for (const [k, v] of Object.entries(patch)) {
        if (v === null || v === undefined || v === "") next.delete(k);
        else next.set(k, v);
      }
      const qs = next.toString();
      const url = qs ? `${pathname}?${qs}` : pathname;
      (mode === "push" ? router.push : router.replace)(url, {
        scroll: false,
      });
    },
    [searchParams, router, pathname]
  );

  return { searchParams, setParams };
}

/** Plain string param, e.g. a Select filter. `fallback` values are omitted
 * from the URL so clean views stay clean. */
export function useUrlParam(
  key: string,
  fallback = ""
): [string, (v: string) => void] {
  const { searchParams, setParams } = useUrlParams();
  const value = searchParams.get(key) ?? fallback;
  const set = useCallback(
    (v: string) => setParams({ [key]: v === fallback || v === "" ? null : v }),
    [key, fallback, setParams]
  );
  return [value, set];
}

/** Free-text param with a debounce so typing doesn't spam history. The input
 * stays responsive (local state) while the URL catches up, and external URL
 * changes (Back/Forward, shared links) still sync in. `setNow` writes the
 * param immediately — optionally alongside other params in one navigation. */
export function useUrlText(
  key: string,
  debounceMs = 250
): [
  string,
  (v: string) => void,
  (v: string, extra?: Record<string, string | null>) => void,
] {
  const { searchParams, setParams } = useUrlParams();
  const urlVal = searchParams.get(key) ?? "";
  const [value, setValue] = useState(urlVal);
  const pending = useRef<string | null>(null);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (pending.current !== null && urlVal === pending.current) {
      // Our own debounced write landing — local state is already correct.
      pending.current = null;
      return;
    }
    // External navigation (Back/Forward, shared link, combined clear) — sync in.
    setValue(urlVal);
  }, [urlVal]);

  useEffect(
    () => () => {
      if (timer.current) clearTimeout(timer.current);
    },
    []
  );

  const set = useCallback(
    (v: string) => {
      setValue(v);
      pending.current = v;
      if (timer.current) clearTimeout(timer.current);
      timer.current = setTimeout(
        () => setParams({ [key]: v || null }),
        debounceMs
      );
    },
    [key, debounceMs, setParams]
  );

  const setNow = useCallback(
    (v: string, extra?: Record<string, string | null>) => {
      if (timer.current) clearTimeout(timer.current);
      pending.current = null;
      setValue(v);
      setParams({ [key]: v || null, ...extra });
    },
    [key, setParams]
  );

  return [value, set, setNow];
}

/** Multi-key variant of useUrlText: several debounced text params share one
 *  hook, so a combined clear (or a chip X) can't be resurrected by a pending
 *  per-key timer. `keys` must be a stable module-level list — identity is
 *  taken by content, not reference. `setNow` writes an arbitrary patch in a
 *  single navigation and cancels every pending debounce. */
export function useUrlTexts<K extends string>(
  keys: readonly K[],
  debounceMs = 250
): [
  Record<K, string>,
  (key: K, v: string) => void,
  (patch: Record<string, string | null>) => void,
] {
  const { searchParams, setParams } = useUrlParams();
  const keysKey = keys.join("");
  const urlVals = useMemo(() => {
    const out = {} as Record<K, string>;
    for (const k of keys) out[k] = searchParams.get(k) ?? "";
    return out;
    // eslint-disable-next-line react-hooks/exhaustive-deps -- keysKey proxies keys
  }, [searchParams, keysKey]);
  const [values, setValues] = useState(urlVals);
  const pending = useRef<Partial<Record<K, string>>>({});
  const timers = useRef<Partial<Record<K, ReturnType<typeof setTimeout>>>>({});

  useEffect(() => {
    // External navigation (Back/Forward, shared link, clear-all) — adopt the
    // URL value per key, except keys with an own write still in flight.
    setValues((cur) => {
      const next = { ...cur };
      let changed = false;
      for (const k of keys) {
        if (k in pending.current) {
          if (urlVals[k] === pending.current[k]) delete pending.current[k];
          else continue;
        }
        if (next[k] !== urlVals[k]) {
          next[k] = urlVals[k];
          changed = true;
        }
      }
      return changed ? next : cur;
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps -- keysKey proxies keys
  }, [urlVals, keysKey]);

  useEffect(
    () => () => {
      for (const k of keys) {
        const t = timers.current[k];
        if (t) clearTimeout(t);
      }
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps -- keysKey proxies keys
    [keysKey]
  );

  const set = useCallback(
    (key: K, v: string) => {
      setValues((cur) => ({ ...cur, [key]: v }));
      pending.current[key] = v;
      if (timers.current[key]) clearTimeout(timers.current[key]);
      timers.current[key] = setTimeout(
        () => setParams({ [key]: v || null }),
        debounceMs
      );
    },
    [debounceMs, setParams]
  );

  const setNow = useCallback(
    (patch: Record<string, string | null>) => {
      for (const k of keys) {
        const t = timers.current[k];
        if (t) clearTimeout(t);
      }
      timers.current = {};
      pending.current = {};
      const keySet = new Set<string>(keys);
      setValues((cur) => {
        const next = { ...cur };
        for (const [k, v] of Object.entries(patch)) {
          if (keySet.has(k)) next[k as K] = v ?? "";
        }
        return next;
      });
      setParams(patch);
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps -- keysKey proxies keys
    [setParams, keysKey]
  );

  return [values, set, setNow];
}

export function parseCsvSet<T extends string>(raw: string | null): Set<T> {
  return new Set((raw ?? "").split(",").filter(Boolean) as T[]);
}

/** Set<T> param encoded comma-separated. */
export function useUrlSet<T extends string>(
  key: string
): [Set<T>, (s: Set<T>) => void] {
  const { searchParams, setParams } = useUrlParams();
  const value = useMemo(
    () => parseCsvSet<T>(searchParams.get(key)),
    [searchParams, key]
  );
  const set = useCallback(
    (s: Set<T>) => setParams({ [key]: s.size ? [...s].join(",") : null }),
    [key, setParams]
  );
  return [value, set];
}

/** Boolean flag param ("1" when on, absent when off). */
export function useUrlFlag(key: string): [boolean, (v: boolean) => void] {
  const { searchParams, setParams } = useUrlParams();
  const value = searchParams.get(key) === "1";
  const set = useCallback(
    (v: boolean) => setParams({ [key]: v ? "1" : null }),
    [key, setParams]
  );
  return [value, set];
}

export function encodeSorting(s: SortingState): string | null {
  return s.length
    ? s.map((x) => `${x.id}.${x.desc ? "desc" : "asc"}`).join(",")
    : null;
}

export function decodeSorting(
  raw: string | null,
  fallback: SortingState
): SortingState {
  if (!raw) return fallback;
  const parsed = raw
    .split(",")
    .map((part) => {
      const [id, dir] = part.split(".");
      return { id, desc: dir === "desc" };
    })
    .filter((x) => x.id);
  return parsed.length ? parsed : fallback;
}

const NO_SORT: SortingState = [];

/** TanStack SortingState param, e.g. ?sort=name.asc,name2.desc . Accepts
 * updater functions so it can be passed straight to onSortingChange. The
 * returned value keeps a stable identity across renders — feeding a fresh
 * array into controlled TanStack state every render deadlocks transitions. */
export function useUrlSorting(
  fallback: SortingState = NO_SORT,
  key = "sort"
): [SortingState, (s: SortingState | ((p: SortingState) => SortingState)) => void] {
  const { searchParams, setParams } = useUrlParams();
  const raw = searchParams.get(key);
  // Deps on `raw` only: `fallback` may be an inline literal, and re-decoding
  // per render would give callers a new array identity every render.
  const value = useMemo(() => decodeSorting(raw, fallback), [raw]);
  const fallbackEnc = encodeSorting(fallback);
  const set = useCallback(
    (s: SortingState | ((p: SortingState) => SortingState)) => {
      const next = typeof s === "function" ? s(value) : s;
      const enc = encodeSorting(next);
      setParams({ [key]: enc === fallbackEnc ? null : enc });
    },
    [key, fallbackEnc, setParams, value]
  );
  return [value, set];
}
