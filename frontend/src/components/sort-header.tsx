import { ArrowDown, ArrowUp, ArrowUpDown } from "lucide-react";
import type { Column } from "@tanstack/react-table";

/** Maps a column's sort state to aria-sort for the wrapping <th>. */
export function columnAriaSort<TData>(
  column: Column<TData, unknown>
): "ascending" | "descending" | "none" | undefined {
  if (!column.getCanSort()) return undefined;
  const dir = column.getIsSorted();
  return dir === "asc" ? "ascending" : dir === "desc" ? "descending" : "none";
}

export function SortHeader<TData>({
  column,
  children,
}: {
  column: Column<TData, unknown>;
  children: React.ReactNode;
}) {
  const dir = column.getIsSorted();
  return (
    <button
      type="button"
      className="inline-flex items-center gap-1 hover:text-foreground"
      onClick={() => column.toggleSorting(dir === "asc")}
    >
      {children}
      {dir === "asc" ? (
        <ArrowUp className="h-3 w-3" />
      ) : dir === "desc" ? (
        <ArrowDown className="h-3 w-3" />
      ) : (
        <ArrowUpDown className="h-3 w-3 opacity-40" />
      )}
    </button>
  );
}
