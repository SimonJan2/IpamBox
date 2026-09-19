"use client";

import {
  useCallback,
  useEffect,
  useRef,
  useState,
  type DependencyList,
  type Dispatch,
  type SetStateAction,
} from "react";

/**
 * Fetch-on-mount state: `{ data, loading, error, reload }`.
 *
 * - `loading` stays true only until the first attempt finishes — later
 *   refetches (polls, post-mutation refreshes) don't flip it back on, so
 *   <AsyncPanel> skeletons only show on the initial load.
 * - Failures are captured into `error` instead of being swallowed; render
 *   them through <AsyncPanel> (or a toast where a panel doesn't fit).
 * - `reload` refetches and resolves to the data (null on failure); it
 *   re-runs automatically when `deps` change and is safe to call from
 *   mutations, event handlers and usePolling callbacks.
 */
export function useAsyncData<T>(
  load: () => Promise<T>,
  deps: DependencyList = []
): {
  data: T | null;
  setData: Dispatch<SetStateAction<T | null>>;
  loading: boolean;
  error: string | null;
  reload: () => Promise<T | null>;
} {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const loadRef = useRef(load);
  loadRef.current = load;

  // eslint-disable-next-line react-hooks/exhaustive-deps -- deps are the
  // caller-declared dependency list, spread here by design.
  const reload = useCallback(async (): Promise<T | null> => {
    try {
      const v = await loadRef.current();
      setData(v);
      setError(null);
      return v;
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
      return null;
    } finally {
      setLoading(false);
    }
  }, deps);

  useEffect(() => {
    setLoading(true);
    void reload();
  }, [reload]);

  return { data, setData, loading, error, reload };
}
