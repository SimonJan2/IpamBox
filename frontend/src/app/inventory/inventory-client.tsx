"use client";

import { useCallback, useEffect, useId, useMemo, useState } from "react";
import { History, Pencil, Plus, Trash2 } from "lucide-react";
import { toast } from "sonner";
import {
  flexRender,
  getCoreRowModel,
  getSortedRowModel,
  useReactTable,
  type ColumnDef,
} from "@tanstack/react-table";

import { api } from "@/lib/api";
import { useAsyncData } from "@/lib/use-async-data";
import { useAuth } from "@/lib/auth";
import { PERM } from "@/lib/permissions";
import { foldHebrew } from "@/lib/utils";
import { useUrlParam, useUrlSorting, useUrlText } from "@/lib/url-state";
import { useRowNav } from "@/lib/row-nav";
import { SortHeader, columnAriaSort } from "@/components/sort-header";
import { AsyncPanel } from "@/components/async-panel";
import { HistoryDialog } from "@/components/history-panel";
import { InlineText } from "@/components/inline-edit";
import { SavedViews } from "@/components/saved-views";
import type { Asset, AssetKind, Site } from "@/types";
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
  const itemsQ = useAsyncData(() => api.get<Asset[]>("/api/v1/assets"));
  const sitesQ = useAsyncData(async () => {
    try {
      return await api.get<Site[]>("/api/v1/sites");
    } catch (e) {
      toast.error("Could not load sites", { description: String(e) });
      return [];
    }
  });
  const [q, setQ] = useUrlText("q");
  const [kindFilter, setKindFilter] = useUrlParam("kind", "all");
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

  const filtered = useMemo(() => {
    const needle = foldHebrew(q.toLowerCase());
    return rows.filter((a) => {
      if (kindFilter !== "all" && a.kind !== kindFilter) return false;
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
  }, [rows, q, kindFilter]);

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

  const columns = useMemo<ColumnDef<AssetRow>[]>(
    () => [
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
        cell: (c) => (
          <div className="flex justify-end gap-1">
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
    [canWrite, canDelete, saveField]
  );

  const table = useReactTable({
    data: filtered,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    state: { sorting },
    onSortingChange: setSorting,
  });

  const tableRows = table.getRowModel().rows;
  const { rowProps } = useRowNav({
    count: tableRows.length,
    onOpen: (i) => {
      const a = tableRows[i]?.original;
      if (!a) return;
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
        <h1 className="text-xl font-semibold">Inventory</h1>
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

      <div className="flex flex-wrap items-center gap-2">
        <Input
          placeholder="Search inventory…"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          className="max-w-xs"
        />
        <Select value={kindFilter} onValueChange={setKindFilter}>
          <SelectTrigger className="w-36">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All kinds</SelectItem>
            <SelectItem value="hardware">Hardware</SelectItem>
            <SelectItem value="software">Software</SelectItem>
          </SelectContent>
        </Select>
        <span className="ml-auto text-sm text-muted-foreground">
          {tableRows.length} of {items.length}
        </span>
        <SavedViews pageKey="inventory" />
      </div>

      <div className="rounded-lg border">
        <AsyncPanel
          loading={itemsQ.loading}
          error={itemsQ.error}
          onRetry={itemsQ.reload}
          empty={items.length === 0}
          emptyMessage="No assets yet — add the first one."
        >
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
            {tableRows.map((row, i) => (
              <TableRow
                key={row.id}
                {...rowProps(i)}
                className="focus-visible:bg-muted/50 focus-visible:outline-none"
              >
                {row.getVisibleCells().map((cell) => (
                  <TableCell key={cell.id}>
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </TableCell>
                ))}
              </TableRow>
            ))}
            {tableRows.length === 0 && items.length > 0 && (
              <TableRow>
                <TableCell
                  colSpan={10}
                  className="py-10 text-center text-muted-foreground"
                >
                  No assets match this filter.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
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
