"use client";

import { useCallback, type CSSProperties, type Dispatch, type SetStateAction } from "react";
import { toast } from "sonner";

import { api } from "@/lib/api";

/**
 * Shared row-color palette — the same ten hexes the tag dialog offers, so
 * a tag chip and a tinted row read as the same color language. The backend
 * stores raw #RRGGBB (validated server-side), not token names.
 */
export const ROW_COLOR_PALETTE: readonly string[] = [
  "#10b981",
  "#3b82f6",
  "#f59e0b",
  "#f43f5e",
  "#8b5cf6",
  "#06b6d4",
  "#f97316",
  "#84cc16",
  "#ec4899",
  "#64748b",
];

/** Entities whose list rows can carry a color. */
export interface RowColorEntity {
  id: number;
  row_color: string | null;
  display_color: string | null;
}

/**
 * Inline style for a tinted row: a 3px accent bar on the leading edge plus
 * a ~10% alpha wash painted as a background-image, so it layers over the
 * theme's row background (and the pinned-row `bg-muted/30`) instead of
 * replacing it — legible in both themes without hardcoded surface colors.
 */
export function rowTintStyle(color: string | null | undefined): CSSProperties | undefined {
  if (!color) return undefined;
  return {
    boxShadow: `inset 3px 0 0 ${color}`,
    backgroundImage: `linear-gradient(${color}1a, ${color}1a)`,
  };
}

/**
 * Optimistic manual-color PATCH. `display_color` is server-computed
 * (manual wins, else first matching rule), so the response value is applied
 * on success — that's how clearing a manual color instantly restores the
 * rule tint instead of going blank until reload.
 */
export function useRowColor<T extends RowColorEntity>({
  path,
  setData,
}: {
  /** API prefix, e.g. "/api/v1/sites". */
  path: string;
  /** useAsyncData's setData. */
  setData: Dispatch<SetStateAction<T[] | null>>;
}) {
  return useCallback(
    async (id: number, color: string | null) => {
      let prev: T | undefined;
      setData((cur) => {
        prev = (cur ?? []).find((r) => r.id === id);
        return (cur ?? []).map((r) =>
          r.id === id ? { ...r, row_color: color, display_color: color } : r
        );
      });
      try {
        const saved = await api.patch<T>(`${path}/${id}`, { row_color: color });
        setData((cur) =>
          (cur ?? []).map((r) =>
            r.id === id
              ? {
                  ...r,
                  row_color: saved.row_color,
                  display_color: saved.display_color,
                }
              : r
          )
        );
      } catch (e) {
        setData((cur) =>
          (cur ?? []).map((r) => (r.id === id && prev ? prev : r))
        );
        toast.error("Couldn't set row color", { description: String(e) });
      }
    },
    [path, setData]
  );
}
