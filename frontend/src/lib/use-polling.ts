"use client";

import { useEffect, useRef } from "react";

export type PollSignature = string | number | void;

interface PollingOptions {
  /** Base interval between polls, in ms. */
  interval: number;
  /** Backoff ceiling while data is unchanged, in ms. Defaults to 60s. */
  maxInterval?: number;
  /** Set false to suspend polling entirely (e.g. while SSE drives updates). */
  enabled?: boolean;
}

/**
 * Poll `fn` on an interval that:
 * - issues zero requests while the tab is hidden, and refetches immediately
 *   when the tab regains visibility,
 * - doubles the interval (up to `maxInterval`) while `fn` reports unchanged
 *   data, resetting to `interval` on the first change.
 *
 * `fn` may return a primitive signature of the data it fetched — two identical
 * signatures in a row count as "unchanged". Returning nothing disables
 * backoff (fixed interval). The first tick fires after `interval`, not on
 * mount — do the initial fetch separately (useAsyncData already does).
 */
export function usePolling(
  fn: () => PollSignature | Promise<PollSignature>,
  { interval, maxInterval = 60_000, enabled = true }: PollingOptions
) {
  const fnRef = useRef(fn);
  fnRef.current = fn;

  useEffect(() => {
    if (!enabled) return;
    let delay = interval;
    let lastSig: PollSignature;
    let hasSig = false;
    let inflight = false;
    let disposed = false;
    let timer: ReturnType<typeof setTimeout> | null = null;

    const run = async () => {
      if (inflight || disposed) return;
      inflight = true;
      try {
        const sig = await fnRef.current();
        if (sig !== undefined) {
          delay =
            hasSig && sig === lastSig
              ? Math.min(delay * 2, maxInterval)
              : interval;
          lastSig = sig;
          hasSig = true;
        }
      } finally {
        inflight = false;
      }
    };

    const schedule = () => {
      if (disposed) return;
      timer = setTimeout(async () => {
        if (document.visibilityState === "visible") await run();
        schedule();
      }, delay);
    };

    const onVisibility = () => {
      if (document.visibilityState !== "visible") return;
      if (timer) clearTimeout(timer);
      void run().finally(schedule);
    };

    schedule();
    document.addEventListener("visibilitychange", onVisibility);
    return () => {
      disposed = true;
      if (timer) clearTimeout(timer);
      document.removeEventListener("visibilitychange", onVisibility);
    };
  }, [interval, maxInterval, enabled]);
}
