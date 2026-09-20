"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";

// Row navigation for the "main data table" on a page: j/k (handled by the
// global shortcuts in lib/shortcuts.ts) move a roving focus between rows and
// Enter opens the focused row. Tables register themselves here; the most
// recently mounted table owns the global j/k keys. Non-virtualized tables
// need nothing else; virtualized ones pass `scrollToIndex` so a focus target
// that isn't mounted yet gets scrolled in first (same pending-focus pattern
// as subnet-grid).

interface RowNavApi {
  move: (delta: number) => void;
}

let active: RowNavApi | null = null;

/** Called by the global key handler. Returns true when a table consumed it. */
export function moveRowNav(delta: number): boolean {
  if (!active) return false;
  active.move(delta);
  return true;
}

export function useRowNav({
  count,
  onOpen,
  scrollToIndex,
}: {
  /** Number of navigable rows in display order. */
  count: number;
  /** Enter on a focused row — usually the same as its click action. */
  onOpen?: (index: number) => void;
  /** Bring row `index` into view (virtualized tables only). */
  scrollToIndex?: (index: number) => void;
}) {
  const [cursor, setCursor] = useState(-1);
  const cursorRef = useRef(-1);
  const rowRefs = useRef(new Map<number, HTMLElement>());
  const pendingFocus = useRef<number | null>(null);
  const scrollRef = useRef(scrollToIndex);
  scrollRef.current = scrollToIndex;

  const focusRow = useCallback(
    (i: number) => {
      if (i < 0 || i >= count) return;
      cursorRef.current = i;
      setCursor(i);
      const el = rowRefs.current.get(i);
      if (el) {
        el.focus();
        return;
      }
      pendingFocus.current = i;
      scrollRef.current?.(i);
    },
    [count]
  );

  // Flush a pending focus once the (virtualized) row mounts.
  useEffect(() => {
    const i = pendingFocus.current;
    if (i == null) return;
    const el = rowRefs.current.get(i);
    if (el) {
      pendingFocus.current = null;
      el.focus();
    }
  });

  const move = useCallback(
    (delta: number) => {
      if (count === 0) return;
      const cur = cursorRef.current;
      const next =
        cur < 0
          ? delta > 0
            ? 0
            : count - 1
          : Math.min(Math.max(cur + delta, 0), count - 1);
      focusRow(next);
    },
    [count, focusRow]
  );

  // Own the global j/k keys while mounted.
  const api = useMemo<RowNavApi>(() => ({ move }), [move]);
  useEffect(() => {
    active = api;
    return () => {
      if (active === api) active = null;
    };
  }, [api]);

  // When the list shrinks (filtering, deletes) clamp the cursor.
  const effective = Math.min(cursor, count - 1);

  /** Spread onto each navigable <tr>: roving tabindex, focus tracking,
   *  arrow/Home/End keys, Enter -> onOpen. j/k stay global so they work
   *  before any row is focused. */
  const rowProps = useCallback(
    (i: number) => ({
      ref: (el: HTMLElement | null) => {
        if (el) rowRefs.current.set(i, el);
        else rowRefs.current.delete(i);
      },
      tabIndex: (effective < 0 ? i === 0 : i === effective) ? 0 : -1,
      onFocus: () => {
        cursorRef.current = i;
        setCursor(i);
      },
      onKeyDown: (e: React.KeyboardEvent) => {
        if (e.target !== e.currentTarget) return;
        switch (e.key) {
          case "Enter":
            if (onOpen) {
              e.preventDefault();
              onOpen(i);
            }
            break;
          case "ArrowDown":
            e.preventDefault();
            focusRow(Math.min(i + 1, count - 1));
            break;
          case "ArrowUp":
            e.preventDefault();
            focusRow(Math.max(i - 1, 0));
            break;
          case "Home":
            e.preventDefault();
            focusRow(0);
            break;
          case "End":
            e.preventDefault();
            focusRow(count - 1);
            break;
        }
      },
    }),
    [count, effective, focusRow, onOpen]
  );

  return { rowProps, cursor: effective };
}

/** Register a custom j/k move handler instead of the default row cursor —
 *  e.g. the subnet grid maps j/k to moving one grid row (±COLS cells). */
export function useRowNavMove(move: ((delta: number) => void) | null) {
  const api = useMemo<RowNavApi | null>(
    () => (move ? { move } : null),
    [move]
  );
  useEffect(() => {
    if (!api) return;
    active = api;
    return () => {
      if (active === api) active = null;
    };
  }, [api]);
}
