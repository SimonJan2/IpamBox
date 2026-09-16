import { ArrowDown, ArrowUp, ArrowUpDown } from "lucide-react";
import type { Column } from "@tanstack/react-table";

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
