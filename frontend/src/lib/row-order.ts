"use client";

import { useCallback, useRef, type Dispatch, type SetStateAction } from "react";
import { toast } from "sonner";
import { arrayMove } from "@dnd-kit/sortable";
import type { DragEndEvent } from "@dnd-kit/core";

import { api } from "@/lib/api";

/** Entities that carry the global manual-order columns. */
export interface OrderedEntity {
  id: number;
  pinned: boolean;
  sort_order: number | null;
}

/**
 * Reorder `items` so the rows named by `orderedIds` appear in that order;
 * rows not in the list keep their slots. Mirrors the slot-preserving
 * semantics of POST {path}/reorder, so reordering a scoped view (a circuits
 * tab, a VLAN group) can't disturb rows outside the scope.
 */
function permuteWithin<T extends OrderedEntity>(
  items: T[],
  orderedIds: number[]
): T[] {
  const inScope = new Set(orderedIds);
  const byId = new Map(items.map((it) => [it.id, it]));
  const queue = [...orderedIds];
  return items.map((it) =>
    inScope.has(it.id) ? byId.get(queue.shift()!)! : it
  );
}

/**
 * Resort after a pin flip: pinned first, then sort_order (NULLs last),
 * stable for equal keys — the same ORDER BY the server applies, so the
 * optimistic result matches what a reload returns.
 */
function pinnedFirst<T extends OrderedEntity>(items: T[]): T[] {
  return items
    .map((it, i) => ({ it, i }))
    .sort((a, b) => {
      if (a.it.pinned !== b.it.pinned) return a.it.pinned ? -1 : 1;
      const sa = a.it.sort_order ?? Number.MAX_SAFE_INTEGER;
      const sb = b.it.sort_order ?? Number.MAX_SAFE_INTEGER;
      return sa === sb ? a.i - b.i : sa - sb;
    })
    .map((x) => x.it);
}

/**
 * Shared row-order state for the entity list pages. Order is GLOBAL (stored
 * in Postgres, shared by every user) — never localStorage.
 *
 * - `getVisibleIds` returns the rows on screen in display order — a getter
 *   (not a value) so the hook can be declared before the table rows exist;
 *   it's only invoked inside gesture handlers. When the page is scoped
 *   (VLAN group, circuits active/retired tab) return just that scope's ids:
 *   the POST permutes only them, within their own positions.
 * - `enabled` should be false whenever the visible order isn't the stored
 *   manual order (column sort / text search / categorical filters) — the
 *   page shows a tooltip explaining why instead.
 * - Mutations are optimistic with rollback on failure; network calls are
 *   serialized so back-to-back gestures can't race.
 */
export function useRowOrder<T extends OrderedEntity>({
  path,
  items,
  setData,
  getVisibleIds,
  enabled,
}: {
  /** API prefix, e.g. "/api/v1/sites". */
  path: string;
  /** The full loaded list that `setData` owns. */
  items: T[];
  /** useAsyncData's setData. */
  setData: Dispatch<SetStateAction<T[] | null>>;
  /** Ids of the visible rows, in display order — called lazily inside
   *  gesture handlers, so it may reference values declared after this
   *  hook (e.g. the TanStack row model). */
  getVisibleIds: () => number[];
  enabled: boolean;
}) {
  const itemsRef = useRef(items);
  itemsRef.current = items;
  const visRef = useRef(getVisibleIds);
  visRef.current = getVisibleIds;
  const enabledRef = useRef(enabled);
  enabledRef.current = enabled;
  // Serializes reorder/pin requests so rapid gestures can't interleave.
  const queue = useRef<Promise<void>>(Promise.resolve());

  const enqueue = useCallback((job: () => Promise<void>) => {
    queue.current = queue.current.then(job).catch(() => {});
  }, []);

  /** Apply a reorder (+optional pin flip on the moved row) optimistically,
   *  then persist; roll everything back if either request fails. */
  const commit = useCallback(
    (orderedIds: number[], movedId: number, pinned: boolean | undefined) => {
      const before = itemsRef.current;
      setData((cur) => {
        const next = permuteWithin(cur ?? [], orderedIds);
        if (pinned === undefined) return next;
        return next.map((it) => (it.id === movedId ? { ...it, pinned } : it));
      });
      enqueue(async () => {
        try {
          if (pinned !== undefined) {
            await api.patch(`${path}/${movedId}`, { pinned });
          }
          await api.post(`${path}/reorder`, { ids: orderedIds });
        } catch (e) {
          setData(() => before);
          toast.error("Couldn't save row order", { description: String(e) });
        }
      });
    },
    [path, setData, enqueue]
  );

  const moveByIndex = useCallback(
    (from: number, to: number) => {
      if (!enabledRef.current) return;
      const ids = visRef.current();
      if (
        from === to ||
        from < 0 ||
        to < 0 ||
        from >= ids.length ||
        to >= ids.length
      ) {
        return;
      }
      const byId = new Map(itemsRef.current.map((it) => [it.id, it]));
      const moved = byId.get(ids[from]);
      if (!moved) return;
      // Crossing the pinned boundary pins/unpins the dragged row: landing
      // above the pinned block joins it, landing at/below it leaves it.
      const pinnedOthers = ids.filter(
        (id) => id !== moved.id && byId.get(id)?.pinned
      ).length;
      const newPinned = to < pinnedOthers;
      commit(
        arrayMove(ids, from, to),
        moved.id,
        newPinned === moved.pinned ? undefined : newPinned
      );
    },
    [commit]
  );

  /** dnd-kit onDragEnd handler — spread onto <RowOrderDnd>. */
  const onDragEnd = useCallback(
    (e: DragEndEvent) => {
      const { active, over } = e;
      if (!over || active.id === over.id) return;
      const ids = visRef.current();
      moveByIndex(ids.indexOf(Number(active.id)), ids.indexOf(Number(over.id)));
    },
    [moveByIndex]
  );

  /**
   * Alt+ArrowUp/Down on a focused row moves it. Returns the row's new index
   * (so the caller can refocus it), or null when the key wasn't handled —
   * compose ahead of row-nav's plain-arrow handler:
   *   onKeyDown={(e) => {
   *     const ni = order.keyDown(i, e);
   *     if (ni === null) rp.onKeyDown(e); else focusRow(ni);
   *   }}
   */
  const keyDown = useCallback(
    (i: number, e: React.KeyboardEvent): number | null => {
      if (!enabledRef.current || !e.altKey || e.target !== e.currentTarget) {
        return null;
      }
      const delta = e.key === "ArrowUp" ? -1 : e.key === "ArrowDown" ? 1 : 0;
      if (!delta) return null;
      e.preventDefault();
      const to = Math.min(
        Math.max(i + delta, 0),
        visRef.current().length - 1
      );
      moveByIndex(i, to);
      return to;
    },
    [moveByIndex]
  );

  /** Pin/unpin a row — optimistic, re-sorts so it lands in its section. */
  const setPinned = useCallback(
    (id: number, pinned: boolean) => {
      const before = itemsRef.current;
      setData((cur) =>
        pinnedFirst(
          (cur ?? []).map((it) => (it.id === id ? { ...it, pinned } : it))
        )
      );
      enqueue(async () => {
        try {
          await api.patch(`${path}/${id}`, { pinned });
        } catch (e) {
          setData(() => before);
          toast.error("Couldn't update pin", { description: String(e) });
        }
      });
    },
    [path, setData, enqueue]
  );

  return { enabled, onDragEnd, keyDown, moveByIndex, setPinned };
}
