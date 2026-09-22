"use client";

import { useCallback, useEffect, useId, useMemo, useState } from "react";
import {
  Columns3,
  History,
  Layers,
  Pencil,
  Plus,
  Trash2,
} from "lucide-react";
import { toast } from "sonner";
import {
  flexRender,
  getCoreRowModel,
  getExpandedRowModel,
  getGroupedRowModel,
  getSortedRowModel,
  useReactTable,
  type ColumnDef,
  type ExpandedState,
  type VisibilityState,
} from "@tanstack/react-table";

import { api } from "@/lib/api";
import { useAsyncData } from "@/lib/use-async-data";
import { useAuth } from "@/lib/auth";
import { PERM } from "@/lib/permissions";
import { cn, foldHebrew } from "@/lib/utils";
import { useUrlParam, useUrlSorting, useUrlText } from "@/lib/url-state";
import { useRowNav } from "@/lib/row-nav";
import { useRowColor, rowTintStyle } from "@/lib/row-color";
import { useRowOrder } from "@/lib/row-order";
import {
  DragHandle,
  PinToggle,
  PinnedDivider,
  RowOrderDnd,
  SortableRow,
} from "@/components/row-order";
import { SortHeader, columnAriaSort } from "@/components/sort-header";
import { AsyncPanel } from "@/components/async-panel";
import { DocsLink } from "@/components/docs/docs-link";
import { HistoryDialog } from "@/components/history-panel";
import { InlineText } from "@/components/inline-edit";
import { RowColorLegend, RowColorPicker } from "@/components/row-color";
import { SavedViews } from "@/components/saved-views";
import type { Asset, AssetKind, Page, Site } from "@/types";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

const EMPTY = {
  kind: "hardware" as AssetKind,
  category: "",
  vendor: "",
  model: "",
  purpose: "",
  version: "",
  eol_on: "",
  support_status: "",
  serial_number: "",
  site_id: "none",
  notes: "",
};

// Lookup names are baked into the row objects: TanStack caches accessorFn
// results per row for the lifetime of `data`, so reading siteName inside
// accessorFn leaves "" cached when the sites fetch resolves after the
// assets fetch.
type AssetRow = Asset & { site_name: string };

export default function InventoryPage() {
  const { can } = useAuth();
  const canWrite = can(PERM.DATA_WRITE);
  const canDelete = can(PERM.DATA_DELETE);
  const itemsQ = useAsyncData(() => api.get<Page<Asset>>("/api/v1/assets").then((p) => p.items));
  const sitesQ = useAsyncData(async () => {
    try {
      return await api.get<Page<Site>>("/api/v1/sites").then((p) => p.items);
    } catch (e) {
      toast.error("Could not load sites", { description: String(e) });
      return [];
    }
  });
  const [q, setQ] = useUrlText("q");
  const [kindFilter, setKindFilter] = useUrlParam("kind", "all");
  // operational quick-filters set by the stats cards
  const [flag, setFlag] = useUrlParam("flag", "");
  const [groupBy, setGroupBy] = useUrlParam("group", "");
  const [hide, setHide] = useUrlParam("hide", "");
  const [expanded, setExpanded] = useState<ExpandedState>(true);
  const [sorting, setSorting] = useUrlSorting();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState<Asset | null>(null);
  const [deleting, setDeleting] = useState<Asset | null>(null);
  const [historyFor, setHistoryFor] = useState<Asset | null>(null);
  const [form, setForm] = useState(EMPTY);
  const [busy, setBusy] = useState(false);

  const items = itemsQ.data ?? [];
  const sites = sitesQ.data ?? [];
  const refresh = () => void itemsQ.reload();

  // Optimistic single-field patch for inline-editable cells.
  const saveField = useCallback(
    async (id: number, field: "purpose", value: string | null) => {
      let prev: Asset | undefined;
      itemsQ.setData((cur) => {
        prev = (cur ?? []).find((a) => a.id === id);
        return (cur ?? []).map((a) =>
          a.id === id ? { ...a, [field]: value } : a
        );
      });
      try {
        await api.patch(`/api/v1/assets/${id}`, { [field]: value });
      } catch (e) {
        itemsQ.setData((cur) =>
          (cur ?? []).map((a) => (a.id === id && prev ? prev : a))
        );
        toast.error("Save failed", { description: String(e) });
        throw e;
      }
    },
    [itemsQ.setData]
  );

  useEffect(() => {
    if (dialogOpen) {
      setForm(
        editing
          ? {
              kind: editing.kind,
              category: editing.category ?? "",
              vendor: editing.vendor ?? "",
              model: editing.model ?? "",
              purpose: editing.purpose ?? "",
              version: editing.version ?? "",
              eol_on: editing.eol_on ?? "",
              support_status: editing.support_status ?? "",
              serial_number: editing.serial_number ?? "",
              site_id: editing.site_id ? String(editing.site_id) : "none",
              notes: editing.notes ?? "",
            }
          : EMPTY
      );
    }
  }, [dialogOpen, editing]);

  const submit = async () => {
    setBusy(true);
    try {
      const body = {
        ...Object.fromEntries(
          Object.entries(form)
            .filter(([k]) => k !== "site_id")
            .map(([k, v]) => [k, v || null])
        ),
        kind: form.kind,
        eol_on: form.eol_on || null,
        site_id: form.site_id === "none" ? null : Number(form.site_id),
      };
      if (editing) {
        await api.patch(`/api/v1/assets/${editing.id}`, body);
        toast.success("Asset updated");
      } else {
        await api.post("/api/v1/assets", body);
        toast.success("Asset added");
      }
      setDialogOpen(false);
      refresh();
    } catch (e) {
      toast.error("Save failed", { description: String(e) });
    } finally {
      setBusy(false);
    }
  };

  const doDelete = async () => {
    if (!deleting) return;
    try {
      await api.del(`/api/v1/assets/${deleting.id}`);
      toast.success("Asset deleted");
      setDeleting(null);
      refresh();
    } catch (e) {
      toast.error("Delete failed", { description: String(e) });
    }
  };

  const siteName = useMemo(
    () => Object.fromEntries(sites.map((s) => [s.id, s.name])),
    [sites]
  );

  const rows = useMemo<AssetRow[]>(
    () =>
      items.map((a) => ({
        ...a,
        site_name: a.site_id ? (siteName[a.site_id] ?? "") : "",
      })),
    [items, siteName]
  );

  const stats = useMemo(() => {
    const now = Date.now();
    const in90 = now + 90 * 86_400_000;
    const s = { hardware: 0, software: 0, eol_past: 0, eol_90: 0, no_serial: 0, no_site: 0 };
    for (const a of rows) {
      if (a.kind === "hardware") s.hardware++;
      else s.software++;
      const eol = a.eol_on ? new Date(a.eol_on).getTime() : null;
      if (eol !== null && eol < now) s.eol_past++;
      else if (eol !== null && eol < in90) s.eol_90++;
      if (!a.serial_number) s.no_serial++;
      if (!a.site_id) s.no_site++;
    }
    return s;
  }, [rows]);

  const filtered = useMemo(() => {
    const needle = foldHebrew(q.toLowerCase());
    const now = Date.now();
    const in90 = now + 90 * 86_400_000;
    return rows.filter((a) => {
      if (kindFilter !== "all" && a.kind !== kindFilter) return false;
      const eol = a.eol_on ? new Date(a.eol_on).getTime() : null;
      if (flag === "eol_past" && !(eol !== null && eol < now)) return false;
      if (flag === "eol_90" && !(eol !== null && eol >= now && eol < in90))
        return false;
      if (flag === "no_serial" && a.serial_number) return false;
      if (flag === "no_site" && a.site_id) return false;
      if (!q) return true;
      return [
        a.vendor,
        a.model,
        a.serial_number,
        a.purpose,
        a.category,
        a.version,
        a.support_status,
        a.notes,
        a.site_name,
      ].some((f) => f != null && foldHebrew(f.toLowerCase()).includes(needle));
    });
  }, [rows, q, kindFilter, flag]);

  const eolBadge = (eol: string | null) => {
    if (!eol) return <span className="text-muted-foreground">—</span>;
    const past = new Date(eol).getTime() < Date.now();
    return (
      <Badge
        variant="outline"
        className={
          past
            ? "border-rose-500/40 text-rose-400"
            : "border-amber-500/40 text-amber-400"
        }
      >
        {past ? "EOL" : `EOL ${eol}`}
      </Badge>
    );
  };

  const orderBlock = sorting.length
    ? "Row order is fixed while a column sort is on — clear the sort to drag."
    : q
      ? "Row order is fixed while searching — clear the search to drag."
      : groupBy
        ? "Row order is fixed while grouped — clear the grouping to drag."
        : flag
          ? "Row order is fixed while a quick filter is on — clear it to drag."
          : kindFilter !== "all"
            ? "Row order is fixed while the kind filter is on — clear it to drag."
            : null;
  const order = useRowOrder<Asset>({
    path: "/api/v1/assets",
    items,
    setData: itemsQ.setData,
    getVisibleIds: (): number[] =>
      tableRows.filter((r) => !r.getIsGrouped()).map((r) => r.original.id),
    enabled: canWrite && !orderBlock,
  });
  const setRowColor = useRowColor<Asset>({
    path: "/api/v1/assets",
    setData: itemsQ.setData,
  });

  const columns = useMemo<ColumnDef<AssetRow>[]>(
    () => [
      ...(canWrite
        ? [
            {
              id: "order",
              enableSorting: false,
              enableHiding: false,
              header: () => <span className="sr-only">Reorder</span>,
              cell: (c) => (
                <DragHandle
                  reason={orderBlock}
                  label={`Reorder asset ${c.row.original.model ?? c.row.original.serial_number ?? c.row.original.id}`}
                />
              ),
            } satisfies ColumnDef<AssetRow>,
          ]
        : []),
      {
        id: "model",
        accessorFn: (a) => a.model ?? a.category ?? "",
        header: ({ column }) => (
          <SortHeader column={column}>Model</SortHeader>
        ),
        cell: (c) => (
          <span dir="auto" className="font-medium">
            {c.getValue<string>() || "—"}
          </span>
        ),
      },
      {
        accessorKey: "kind",
        header: ({ column }) => <SortHeader column={column}>Kind</SortHeader>,
        cell: (c) => <Badge variant="outline">{c.getValue<string>()}</Badge>,
      },
      {
        id: "category",
        accessorFn: (a) => a.category ?? "",
        header: ({ column }) => (
          <SortHeader column={column}>Category</SortHeader>
        ),
        cell: (c) => (
          <span dir="auto" className="text-muted-foreground">
            {c.getValue<string>() || "—"}
          </span>
        ),
      },
      {
        accessorKey: "vendor",
        header: ({ column }) => (
          <SortHeader column={column}>Vendor</SortHeader>
        ),
        cell: (c) => (
          <span dir="auto" className="text-muted-foreground">
            {c.getValue<string | null>() ?? "—"}
          </span>
        ),
      },
      {
        accessorKey: "serial_number",
        header: ({ column }) => (
          <SortHeader column={column}>Serial</SortHeader>
        ),
        cell: (c) => (
          <span dir="ltr" className="font-mono text-muted-foreground">
            {c.getValue<string | null>() ?? "—"}
          </span>
        ),
      },
      {
        id: "site",
        accessorKey: "site_name",
        header: ({ column }) => <SortHeader column={column}>Site</SortHeader>,
        cell: (c) => (
          <span dir="auto" className="text-muted-foreground">
            {c.getValue<string>() || "—"}
          </span>
        ),
      },
      {
        accessorKey: "purpose",
        header: ({ column }) => (
          <SortHeader column={column}>Purpose</SortHeader>
        ),
        cell: (c) => (
          <InlineText
            value={c.getValue<string | null>()}
            onSave={(v) => saveField(c.row.original.id, "purpose", v || null)}
            disabled={!canWrite}
            dir="auto"
            label={`Edit purpose for ${c.row.original.model ?? c.row.original.id}`}
            className="max-w-[200px]"
          />
        ),
      },
      {
        accessorKey: "version",
        header: ({ column }) => (
          <SortHeader column={column}>Version</SortHeader>
        ),
        cell: (c) => (
          <span dir="ltr" className="font-mono text-muted-foreground">
            {c.getValue<string | null>() ?? "—"}
          </span>
        ),
      },
      {
        accessorKey: "support_status",
        header: ({ column }) => (
          <SortHeader column={column}>Support</SortHeader>
        ),
        cell: (c) => (
          <span dir="auto" className="text-muted-foreground">
            {c.getValue<string | null>() ?? "—"}
          </span>
        ),
      },
      {
        accessorKey: "eol_on",
        header: ({ column }) => <SortHeader column={column}>EOL</SortHeader>,
        cell: (c) => eolBadge(c.getValue<string | null>()),
      },
      {
        id: "actions",
        header: () => <div className="text-right">Actions</div>,
        enableSorting: false,
        enableHiding: false,
        cell: (c) => (
          <div className="flex justify-end gap-1">
            {canWrite && (
              <PinToggle
                pinned={c.row.original.pinned}
                name={`asset ${c.row.original.model ?? c.row.original.serial_number ?? c.row.original.id}`}
                onToggle={() =>
                  order.setPinned(c.row.original.id, !c.row.original.pinned)
                }
              />
            )}
            {canWrite && (
              <RowColorPicker
                value={c.row.original.row_color}
                displayColor={c.row.original.display_color}
                name={`asset ${c.row.original.model ?? c.row.original.serial_number ?? c.row.original.id}`}
                onPick={(color) => setRowColor(c.row.original.id, color)}
              />
            )}
            <Button
              variant="ghost"
              size="icon"
              aria-label={`History of asset ${c.row.original.model ?? c.row.original.serial_number ?? c.row.original.id}`}
              onClick={() => setHistoryFor(c.row.original)}
            >
              <History className="h-4 w-4" />
            </Button>
            {canWrite && (
              <Button
                variant="ghost"
                size="icon"
                aria-label={`Edit asset ${c.row.original.model ?? c.row.original.serial_number ?? c.row.original.id}`}
                onClick={() => {
                  setEditing(c.row.original);
                  setDialogOpen(true);
                }}
              >
                <Pencil className="h-4 w-4" />
              </Button>
            )}
            {canDelete && (
              <Button
                variant="ghost"
                size="icon"
                aria-label={`Delete asset ${c.row.original.model ?? c.row.original.serial_number ?? c.row.original.id}`}
                onClick={() => setDeleting(c.row.original)}
              >
                <Trash2 className="h-4 w-4 text-rose-400" />
              </Button>
            )}
          </div>
        ),
      },
    ],
    [canWrite, canDelete, saveField, order.setPinned, orderBlock, setRowColor]
  );

  // URL-backed column visibility (?hide=col1,col2) + grouping (?group=…)
  const columnVisibility = useMemo<VisibilityState>(() => {
    const hidden = new Set(hide ? hide.split(",") : []);
    const v: VisibilityState = {};
    for (const id of [
      "model", "kind", "category", "vendor", "serial_number",
      "site", "purpose", "version", "support_status", "eol_on",
    ]) {
      v[id] = !hidden.has(id);
    }
    return v;
  }, [hide]);
  const grouping = useMemo(() => (groupBy ? [groupBy] : []), [groupBy]);

  const table = useReactTable({
    data: filtered,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getGroupedRowModel: getGroupedRowModel(),
    getExpandedRowModel: getExpandedRowModel(),
    state: { sorting, grouping, columnVisibility, expanded },
    onSortingChange: setSorting,
    onExpandedChange: setExpanded,
  });

  const tableRows = table.getRowModel().rows;
  const visibleIds = tableRows
    .filter((r) => !r.getIsGrouped())
    .map((r) => r.original.id);
  const { rowProps, focusRow } = useRowNav({
    count: tableRows.length,
    onOpen: (i) => {
      const tr = tableRows[i];
      if (!tr || tr.getIsGrouped()) {
        tr?.toggleExpanded();
        return;
      }
      const a = tr.original;
      if (canWrite) {
        setEditing(a);
        setDialogOpen(true);
      } else {
        setHistoryFor(a);
      }
    },
  });

  const set = (k: keyof typeof EMPTY) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm({ ...form, [k]: e.target.value });
  const uid = useId();

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="flex items-center gap-1.5 text-xl font-semibold">Inventory <DocsLink slug="inventory" /></h1>
        {canWrite && (
          <Button
            size="sm"
            onClick={() => {
              setEditing(null);
              setDialogOpen(true);
            }}
          >
            <Plus /> New asset
          </Button>
        )}
      </div>

      {/* stats strip — each card is a click-to-filter shortcut */}
      <div className="grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-6">
        {(
          [
            ["Hardware", stats.hardware, "", "hardware"] as const,
            ["Software", stats.software, "", "software"] as const,
            ["EOL passed", stats.eol_past, "eol_past", ""] as const,
            ["EOL < 90d", stats.eol_90, "eol_90", ""] as const,
            ["No serial", stats.no_serial, "no_serial", ""] as const,
            ["No site", stats.no_site, "no_site", ""] as const,
          ]
        ).map(([label, n, flagKey, kindKey]) => {
          const activeFlag = flagKey !== "" && flag === flagKey;
          const activeKind = kindKey !== "" && kindFilter === kindKey;
          return (
            <button
              key={label}
              type="button"
              onClick={() => {
                if (flagKey) setFlag(activeFlag ? "" : flagKey);
                if (kindKey) setKindFilter(activeKind ? "all" : kindKey);
              }}
              className={cn(
                "rounded-lg border bg-card px-3 py-2 text-left transition-colors hover:bg-accent/50",
                (activeFlag || activeKind) && "border-emerald-500/50 bg-emerald-500/10"
              )}
            >
              <div className="text-xl font-semibold">{n}</div>
              <div className="text-xs text-muted-foreground">{label}</div>
            </button>
          );
        })}
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <Input
          placeholder="Search inventory…"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          className="max-w-xs"
        />
        <div
          role="group"
          aria-label="Kind filter"
          className="flex rounded-lg border p-0.5"
        >
          {(
            [
              ["all", "All"],
              ["hardware", "Hardware"],
              ["software", "Software"],
            ] as const
          ).map(([v, label]) => (
            <button
              key={v}
              type="button"
              onClick={() => setKindFilter(v)}
              className={cn(
                "rounded-md px-3 py-1 text-sm transition-colors",
                kindFilter === v
                  ? "bg-emerald-500/15 text-emerald-400"
                  : "text-muted-foreground hover:text-foreground"
              )}
            >
              {label}
            </button>
          ))}
        </div>
        <Select
          value={groupBy || "__none__"}
          onValueChange={(v) => setGroupBy(v === "__none__" ? "" : v)}
        >
          <SelectTrigger className="w-40" aria-label="Group by">
            <Layers className="h-3.5 w-3.5 text-muted-foreground" />
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="__none__">No grouping</SelectItem>
            <SelectItem value="category">Group by category</SelectItem>
            <SelectItem value="site">Group by site</SelectItem>
            <SelectItem value="vendor">Group by vendor</SelectItem>
          </SelectContent>
        </Select>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="sm" aria-label="Choose columns">
              <Columns3 className="h-4 w-4" /> Columns
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            {table
              .getAllColumns()
              .filter((c) => c.getCanHide())
              .map((c) => (
                <DropdownMenuCheckboxItem
                  key={c.id}
                  checked={c.getIsVisible()}
                  onCheckedChange={(v) => {
                    const hidden = new Set(hide ? hide.split(",") : []);
                    if (v) hidden.delete(c.id);
                    else hidden.add(c.id);
                    setHide([...hidden].join(","));
                  }}
                >
                  {c.id.replace(/_/g, " ")}
                </DropdownMenuCheckboxItem>
              ))}
          </DropdownMenuContent>
        </DropdownMenu>
        {flag && (
          <Button variant="ghost" size="sm" onClick={() => setFlag("")}>
            Clear filter ×
          </Button>
        )}
        <span className="ml-auto text-sm text-muted-foreground">
          {tableRows.length} of {items.length}
        </span>
        <RowColorLegend />
        <SavedViews
          pageKey="inventory"
          builtins={[
            { name: "EOL < 90 days", query: "flag=eol_90" },
            { name: "EOL passed", query: "flag=eol_past" },
            { name: "Missing serial", query: "flag=no_serial" },
            { name: "Routers w/o site", query: "q=router&flag=no_site" },
            { name: "Servers", query: "q=server&group=category" },
          ]}
        />
      </div>

      <div className="rounded-lg border">
        <AsyncPanel
          loading={itemsQ.loading}
          error={itemsQ.error}
          onRetry={itemsQ.reload}
          empty={items.length === 0}
          emptyMessage="No assets yet — add the first one."
        >
        <RowOrderDnd ids={visibleIds} onDragEnd={order.onDragEnd}>
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((hg) => (
              <TableRow key={hg.id}>
                {hg.headers.map((h) => (
                  <TableHead key={h.id} aria-sort={columnAriaSort(h.column)}>
                    {flexRender(h.column.columnDef.header, h.getContext())}
                  </TableHead>
                ))}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {sorting.length === 0 && !groupBy && tableRows[0]?.original.pinned && (
              <PinnedDivider colSpan={columns.length} />
            )}
            {tableRows.map((row, i) => {
              const rp = rowProps(i);
              if (row.getIsGrouped()) {
                // collapsible group header — leafRows holds the members
                return (
                  <TableRow key={row.id} className="bg-muted/40">
                    <TableCell colSpan={columns.length} className="py-1.5">
                      <button
                        type="button"
                        onClick={() => row.toggleExpanded()}
                        className="flex items-center gap-2 font-medium"
                      >
                        <span className="text-muted-foreground">
                          {row.getIsExpanded() ? "▾" : "▸"}
                        </span>
                        <span dir="auto">
                          {String(row.getValue(groupBy) || "—")}
                        </span>
                        <Badge variant="outline" className="text-muted-foreground">
                          {row.getLeafRows().length}
                        </Badge>
                      </button>
                    </TableCell>
                  </TableRow>
                );
              }
              return (
                <SortableRow
                  key={row.id}
                  rowId={row.original.id}
                  dragDisabled={!order.enabled}
                  {...rp}
                  onKeyDown={(e) => {
                    const ni = order.keyDown(i, e);
                    if (ni === null) rp.onKeyDown(e);
                    else focusRow(ni);
                  }}
                  style={rowTintStyle(row.original.display_color)}
                  className={cn(
                    row.original.pinned && "bg-muted/30",
                    "focus-visible:bg-muted/50 focus-visible:outline-none"
                  )}
                >
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id}>
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext()
                      )}
                    </TableCell>
                  ))}
                </SortableRow>
              );
            })}
            {tableRows.length === 0 && items.length > 0 && (
              <TableRow>
                <TableCell
                  colSpan={columns.length}
                  className="py-10 text-center text-muted-foreground"
                >
                  No assets match this filter.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
        </RowOrderDnd>
        </AsyncPanel>
      </div>

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>{editing ? "Edit asset" : "New asset"}</DialogTitle>
          </DialogHeader>
          <div className="grid grid-cols-2 gap-3">
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-kind`}>Kind</Label>
              <Select
                value={form.kind}
                onValueChange={(v) => setForm({ ...form, kind: v as AssetKind })}
              >
                <SelectTrigger id={`${uid}-kind`}>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="hardware">Hardware</SelectItem>
                  <SelectItem value="software">Software</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-site`}>Site</Label>
              <Select
                value={form.site_id}
                onValueChange={(v) => setForm({ ...form, site_id: v })}
              >
                <SelectTrigger id={`${uid}-site`}>
                  <SelectValue placeholder="None" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">None</SelectItem>
                  {sites.map((s) => (
                    <SelectItem key={s.id} value={String(s.id)}>
                      <span dir="auto">{s.name}</span>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-category`}>Category</Label>
              <Input
                id={`${uid}-category`}
                dir="auto"
                value={form.category}
                onChange={set("category")}
              />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-vendor`}>Vendor</Label>
              <Input
                id={`${uid}-vendor`}
                dir="auto"
                value={form.vendor}
                onChange={set("vendor")}
              />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-model`}>Model</Label>
              <Input
                id={`${uid}-model`}
                dir="auto"
                value={form.model}
                onChange={set("model")}
              />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-serial`}>Serial number</Label>
              <Input
                id={`${uid}-serial`}
                dir="ltr"
                value={form.serial_number}
                onChange={set("serial_number")}
              />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-version`}>Version</Label>
              <Input
                id={`${uid}-version`}
                dir="ltr"
                value={form.version}
                onChange={set("version")}
              />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-eol`}>EOL date</Label>
              <Input
                id={`${uid}-eol`}
                type="date"
                dir="ltr"
                value={form.eol_on}
                onChange={set("eol_on")}
              />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-support`}>Support status</Label>
              <Input
                id={`${uid}-support`}
                dir="auto"
                value={form.support_status}
                onChange={set("support_status")}
              />
            </div>
            <div className="col-span-2 grid gap-1.5">
              <Label htmlFor={`${uid}-purpose`}>Purpose</Label>
              <Input
                id={`${uid}-purpose`}
                dir="auto"
                value={form.purpose}
                onChange={set("purpose")}
              />
            </div>
            <div className="col-span-2 grid gap-1.5">
              <Label htmlFor={`${uid}-notes`}>Notes</Label>
              <Input
                id={`${uid}-notes`}
                dir="auto"
                value={form.notes}
                onChange={set("notes")}
              />
            </div>
          </div>
          <DialogFooter>
            <Button onClick={submit} disabled={busy}>
              {busy ? "Saving…" : editing ? "Save" : "Create"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={deleting !== null} onOpenChange={() => setDeleting(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete asset</DialogTitle>
          </DialogHeader>
          <p className="text-sm text-muted-foreground">
            Delete{" "}
            <span dir="auto" className="font-medium text-foreground">
              {deleting?.model ?? deleting?.serial_number}
            </span>
            ?
          </p>
          <DialogFooter>
            <Button variant="ghost" onClick={() => setDeleting(null)}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={doDelete}>
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <HistoryDialog
        open={historyFor !== null}
        onOpenChange={() => setHistoryFor(null)}
        objectType="Asset"
        objectId={historyFor?.id ?? null}
        title={historyFor?.model ?? historyFor?.serial_number}
      />
    </div>
  );
}
